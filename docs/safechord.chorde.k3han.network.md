---
title: 'Policy: Pod Data Path & CNI'
doc_id: safechord.chorde.k3han.network
status: active
authors:
  - bradyhau
  - Claude Opus 5.5
last_updated: '2026-09-25'
summary: Explains how pod-to-pod traffic actually moves across the K3han cluster. flannel stays the CNI but its VXLAN overlay is idle; Tailscale subnet routes carry every cross-node packet in a single WireGuard tunnel. Separates the mechanism (what the kernel and the two projects actually do) from the four decisions taken on top of it, each with its own alternatives and cost.
keywords:
  - CNI
  - flannel
  - Tailscale
  - Pod Networking
  - Policy Routing
  - NetworkPolicy
  - PMTUD
logical_path: SafeChord.Chorde.K3han.Networking.PodDataPath
related_docs:
  - safechord.chorde.k3han.md
  - safechord.chorde.k3han.cluster.md
  - safechord.chorde.k3han.ingress.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/cluster/k3han
  - Chorde/scripts/test/pod-path
tech_stack:
  - flannel
  - Tailscale
  - kube-router (k3s embedded NetworkPolicy)
  - Linux netfilter / policy routing
doc_version: 0.3.8
app_version: 0.3.0
---

# Pod Data Path & CNI (Brain)

> **One-line version**: flannel hands out the addresses and wires the bridge, but it does
> not carry a single cross-node byte. Tailscale does.
>
> **This split is not improvised.** It is the architecture [Kilo](https://kilo.squat.ai/)
> ships as its flannel add-on mode: *"Kilo will take care of the network between
> locations, while Flannel will take care of the network within locations."* We fill the
> between-locations role with Tailscale instead of Kilo (D1). What Kilo does inside one
> component, we get from two projects that were never designed to share a node. That is
> why most of this document is about where they meet and who wins.

---

## 1. Design Constraints (Red Walls)

*   **One tunnel, not two.** Cross-node pod traffic crosses the WAN inside exactly one
    encapsulation: WireGuard, via Tailscale.
*   **The routing outcome is the invariant, not the flags.** On every node, the route to
    every *other* node's pod CIDR resolves to `dev tailscale0 table 52` (§2.3).
*   **Cross-node pod traffic is never source-NATed.** A server pod sees the client's real
    pod IP, from any node (D2).
*   **NetworkPolicy holds on both paths**, bridged and routed. Same-node traffic only
    crosses a Linux bridge, and by default the kernel does not show bridged traffic to
    iptables at all. The switch `net.bridge.bridge-nf-call-iptables = 1` makes it do so.
    Without that switch, NetworkPolicy never sees same-node traffic. It is a kernel
    invariant in [Cluster Strategy §3](safechord.chorde.k3han.cluster.md) (§2.2).
*   **Never lower `cni0` to the tunnel's MTU** (D4). PMTUD already resolves the step on
    the first hop at no cost. Pinning `cni0` to 1280 is the configuration in
    [tailscale#16820](https://github.com/tailscale/tailscale/issues/16820), where iperf3
    TCP fell to 2–3 Mbit/s against 700–800 direct.

---

## 2. Mechanism

Facts, not choices: what the kernel, flannel and Tailscale do when put on one node.
Nothing here has an alternative. Each claim is backed by §4.

### 2.1 Who does what

| Concern | Owner |
| :--- | :--- |
| Pod IPAM (a `/24` per node from `.spec.podCIDR`), `cni0` bridge, veth wiring | flannel (CNI plugin) |
| Pod egress masquerade; `FLANNEL-FWD`, which admits unpoliced pod traffic on `-P FORWARD DROP` nodes | flannel (iptables) |
| **Cross-node transport** | **Tailscale subnet routes** |
| VXLAN overlay (`flannel.1`) | flannel backend. **Idle:** 0 bytes received since boot |
| NetworkPolicy | kube-router, embedded in k3s |

### 2.2 Same node vs. cross node

The fork happens inside the **pod's own routing table**. flannel gives every pod:

```
<own node /24>   dev eth0              ← same node: on-link, L2
10.42.0.0/16     via <cni0 address>    ← other nodes: hand to the gateway
default          via <cni0 address>
```

**Same node, switched at L2:** `pod A → veth → cni0 → veth → pod B`. The bridge forwards
the frame like a switch does, so the host's IP routing, and with it iptables, is never
involved. That would leave same-node traffic invisible to NetworkPolicy. The
`bridge-nf-call-iptables` switch (loaded with the `br_netfilter` module) closes that gap:
it passes bridged frames through iptables too. kube-router writes a separate rule
variant for exactly this case (`-m physdev --physdev-is-bridged`).

**Cross node, routed at L3.** Each packet crosses netfilter **twice** on the sender:

```
Pass 1 — the pod packet, forwarded
  pod A → cni0 (frame addressed to the bridge) → host IP stack
    PREROUTING   conntrack; kube-proxy DNAT (Service VIP → pod IP)
    routing      ip rule 5270 → table 52 → 10.42.x.0/24 dev tailscale0
    FORWARD      kube-router NetworkPolicy; kube-proxy; ts-forward; FLANNEL-FWD
    POSTROUTING  KUBE-POSTROUTING → ts-postrouting → FLANNEL-POSTRTG
  → tailscale0 (TUN, no L2) → handed to tailscaled in userspace

Pass 2 — the WireGuard datagram, locally generated
  tailscaled encrypts → new UDP packet from its own socket (fwmark 0x80000)
    OUTPUT       local egress
    routing      ip rule 5210: fwmark 0x80000 → main (skips table 52)
    POSTROUTING
  → eth0 → the peer node's public endpoint
```

Without the fwmark, pass 2 would hit table 52 like any other packet and route the
ciphertext back into the tunnel.

The hook order (PREROUTING → routing → FORWARD → POSTROUTING) is fixed in the kernel,
identical across our distributions and kernels. The rule order *within* a chain is not:
it is whoever inserted last.

### 2.3 Why Tailscale wins the route

flannel puts `via flannel.1` in the **main** table; Tailscale puts `dev tailscale0` in
**table 52**. The kernel walks `ip rule` in ascending preference and uses the first table
with a match. **Longest-prefix match applies within a table, never across tables.**
Tailscale's `5270: lookup 52` precedes the main table's `32766`, so table 52 wins.
flannel installs no `ip rule` at all.

That outcome needs four things at once:

| Precondition | Held by |
| :--- | :--- |
| Rule 5270 precedes the main table | Tailscale (a constant in its source) |
| `--accept-routes` on every node | tailscaled prefs |
| Each node advertises its own `.spec.podCIDR` | tailscaled prefs |
| The advertised route is **approved** on the tailnet | Tailscale admin console (by hand) |

> ⚠️ **Silent fallback.** When any one precondition fails, nothing errors. Traffic slides
> onto `flannel.1`, whose VTEPs are the Tailscale IPs, so the fallback is VXLAN inside
> WireGuard: reachable, double-encapsulated, never measured. The only signal is
> `flannel.1` **RX** leaving 0 (§2.6).

### 2.4 MTU: the bottleneck is the first hop

Pods get `cni0`'s 1450; `tailscale0` is 1280. Linux TCP sets DF, so the first full-size
segment is **dropped, not fragmented**. The sending node, acting as the pod's first-hop
router, returns ICMP *fragmentation needed* (RFC 1191). The pod caches a 1280 path MTU and
TCP shrinks its segments. The cost is one round trip per new path, repeated when the cache
entry expires.

The ICMP is generated and delivered **inside one host**, so no middlebox can filter it.
kube-router's pod chains accept traffic from the local node (`--src-type LOCAL`) ahead of
their default policy chains.

### 2.5 Netfilter has several writers and no arbiter

kube-router, kube-proxy, flannel and Tailscale write each node's `filter` and `nat`
tables, and so does ufw on `ct-serv-jp` and Docker on `acer-agent`. iptables has no
priority between them; whoever last ran `-I CHAIN 1` goes first. kube-router re-asserts
its own jump on resync but reorders nobody else.

Policy survives this for two structural reasons:

*   kube-router ends every denial with `REJECT` **inside its own chain**, so a denied
    packet never returns to meet Tailscale's blanket `ACCEPT`.
*   `FORWARD`, where policy runs, precedes `POSTROUTING`, where masquerade runs. Policy
    always sees the original source.

### 2.6 Verification

| Check | Where | What it asserts |
| :--- | :--- | :--- |
| Peer-route gate | Final tasks of `privision.yaml` | Prefs match; every peer CIDR resolves to `dev tailscale0 table 52`. Fails the play |
| `node-routing-test.sh` | `Chorde/scripts/test/pod-path/` | The same gate on the live cluster, plus `bridge-nf-call-iptables` and `flannel.1` RX = 0. Read-only; first thing to run when cross-node traffic looks wrong |
| `netpol-matrix-test.sh` | `Chorde/scripts/test/pod-path/` | 27 probes across all node pairs: policy verdicts and real source IPs. Creates and deletes a namespace |

Watch `flannel.1` **RX**, never TX. TX is nonzero everywhere: tailscaled's disco probes to
peers' `10.42.x.0/.1` addresses carry the bypass fwmark, fall through to the main table
and leave via `flannel.1`.

---

## 3. Decisions

### D1. Transport: Tailscale subnet routes, not flannel's overlay

*   **Decision.** Each node advertises its pod CIDR on the tailnet and accepts the others'.
    flannel is kept as CNI; its VXLAN backend is left configured and idle.
*   **Why.**
    *   The home node sits behind residential NAT, and the tailnet already solves NAT
        traversal and encryption.
    *   One component owns the path end to end, so there is one MTU step instead of two.
*   **Prior art.** This is Kilo's flannel add-on topology, with Tailscale in Kilo's seat.
    flannel handles the network within a node; a WireGuard mesh handles the network
    between them.
    *   Kilo needs at least one node with a routable public IP per location. Tailscale
        does not, since it relays through DERP when direct paths fail. That matters for
        the home node.
    *   What we give up against Kilo is integration. Kilo reads the pod CIDRs from
        Kubernetes and programs routes itself. Here, advertising and approving routes is
        our job (see Cost).
*   **Alternatives rejected.**
    *   *flannel VXLAN over the WAN* (the k3s default): no encryption, no NAT traversal.
    *   *VXLAN over Tailscale* (`--flannel-iface=tailscale0`, `--vpn-auth`): two tunnels,
        and `cni0` forced toward ~1230. `--vpn-auth` is experimental. `--flannel-iface`
        was tried and failed on the k3s version of the time. It survives only as the
        silent fallback.
    *   *flannel `wireguard-native`*: single-layer, but no NAT traversal for the home node.
    *   *Replace the CNI* (Cilium, `--flannel-backend=none`): a live CNI swap across
        borders, to remove an overlay that costs nothing.
*   **Cost.**
    *   Correct routing rests on Tailscale's rule preference, an upstream constant under
        open discussion ([tailscale#6231](https://github.com/tailscale/tailscale/issues/6231)).
    *   Route approval lives in the admin console, outside git.
    *   `flannel.1` and its routes advertise an overlay that carries nothing, which
        misleads anyone reading `ip route`.
*   **Mitigation.**
    *   The gate and tests in §2.6 assert the kernel's decision, not the four inputs. A
        standing `flannel.1` RX tripwire is planned.
    *   If the rule ever stops winning:
        `ip rule add not fwmark 0x80000/0xff0000 to 10.42.0.0/16 lookup 52 pref 5000`,
        persisted after tailscaled. This holds only while Tailscale still uses table 52.
*   **Context.** Stretching one cluster across ~80 ms is not mainstream, because etcd
    wants single-digit-millisecond peers. The projects built for it (Kilo, Cilium with
    WireGuard) converge on the same rule: one component owns the transport and its MTU.
    The alternatives above that stack VXLAN on WireGuard break that rule.

### D2. No subnet SNAT

*   **Decision.** `--snat-subnet-routes=false` on every node.
*   **Why.** With SNAT on, source identity depended on chain order (§2.5). Where
    `ts-forward` ran before kube-router's ACCEPT, packets arriving on `tailscale0` were
    marked and then masqueraded. On `acer-agent`, every cross-node client reached its pods
    as the node's `cni0` address. flannel exempts pod→pod from masquerade, but
    `ts-postrouting` runs first.
*   **Alternatives rejected.**
    *   *Fix the chain order by restarting services*: it lasts until the next tailscaled
        restart. Auto-update is on.
*   **Cost.** A non-cluster tailnet client reaching a pod now depends on the return route,
    not on SNAT. No such client is active.
*   **Mitigation.** `netpol-matrix-test.sh` asserts that every server sees the real client
    IP.

### D3. Keep netfilter shared (for now)

*   **Decision.** Leave Tailscale's netfilter mode at the default. Accept the unarbitrated
    ordering for everything except SNAT (D2).
*   **Why.** Policy verdicts are ordering-proof (§2.5). The remaining exposure is narrow:
    where `ts-forward`/`ts-input` sit above kube-proxy's chains (currently `acer-agent`),
    tailnet traffic skips `KUBE-PROXY-FIREWALL`, `KUBE-FORWARD` and `KUBE-FIREWALL`. Only
    tailnet members can send it, and no Service uses `loadBalancerSourceRanges`.
*   **Alternatives deferred.**
    *   *`--netfilter-mode=nodivert`* (**preferred next step**): Tailscale keeps its chains
        current; we place the jumps at the chain tail, where kube-* inserts cannot
        displace them. Ordering becomes declared.
    *   *`--netfilter-mode=off`*: removes the race entirely. But `ct-serv-jp`'s ufw has no
        allow rules, so its API server, kubelet and WireGuard port are admitted by
        `ts-input` alone. Those must become explicit rules first.
*   **Cost.** Chain order still differs between nodes and still depends on startup order.
*   **Mitigation.** A chain-order tripwire is planned.

### D4. No MTU tuning

*   **Decision.** Leave `cni0` at flannel's derived value. Do not clamp MSS. Do not set
    `tcp_mtu_probing`.
*   **Why.** The MTU step is resolved by PMTUD on the first hop, and the ICMP never leaves
    the node (§2.4). The classic black hole does not apply.
*   **Alternatives rejected.**
    *   *Lower `cni0` to 1280*: the configuration that collapses TCP throughput in
        [tailscale#16820](https://github.com/tailscale/tailscale/issues/16820).
    *   *MSS clamping*: a hand-kept constant doing PMTUD's job.
    *   *`tcp_mtu_probing = 1`* (RFC 4821): insures against a failure mode this topology
        does not have.
*   **Cost.** `cni0`'s value is flannel's NIC-derived number, computed for an overlay that
    carries nothing. It happens to be right. It is already inconsistent across nodes
    (`gce-agent-tw` derives lower), harmlessly.
*   **Mitigation.** The red wall in §1.

---

## 4. Reference Snapshots

> Point-in-time, **not SSOT**. Verified 2026-09-21 (throughput) and 2026-09-25 (the rest).

| Observation | Value | Backs |
| :--- | :--- | :--- |
| Cross-node pod→pod TCP, default / MSS 1100 / node→node | 209 / 234 / 232 Mbit/s median | D1, D4: pod traffic runs at the node-to-node tailnet rate, so the CNI arrangement adds no measurable cost. What bounds that rate (uplink, cross-border path, WireGuard CPU) was not investigated |
| Same-node pod→pod | 32.1 Gbit/s | §2.2: bridge path never touches the tunnel |
| `tailscale0` vs `flannel.1` TX, 10 s cross-node run | +215,542,969 B vs +1,460 B | §2.3 |
| `flannel.1` RX, all nodes | 0 B since boot | §2.3: fallback never used |
| `IpFragCreates` / `IpFragFails`, `ct-serv-jp` since boot | 0 / 5353 | §2.4: drop-and-report, never fragmentation |
| NetworkPolicy matrix, 3 nodes × 3 clients × 3 servers | 27/27 | §2.5 |
| Source IP seen after NoSNAT everywhere | Real client pod IP, all pairs | D2 |

---

## 5. References

*   **Provisioning & gate**: `Chorde/cluster/k3han/ansible/privision.yaml`
*   **Recorded k3s units**: `Chorde/cluster/k3han/k3s/`
*   **Tests**: `Chorde/scripts/test/pod-path/`
*   **Tickets**: Chorde#16 (this design), Chorde#15 (the playbook has never run), Chorde#17 (playbook roles)
*   **Related Policies**: [Cluster Strategy](safechord.chorde.k3han.cluster.md), [Ingress Policy](safechord.chorde.k3han.ingress.md)
*   **External**: [Tailscale netfilter modes](https://tailscale.com/docs/reference/netfilter-modes), [Tailscale route injection](https://tailscale.com/docs/reference/route-injection), RFC 1191, RFC 4821
