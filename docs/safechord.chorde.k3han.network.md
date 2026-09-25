---
title: 'Policy: Pod Data Path & CNI'
doc_id: safechord.chorde.k3han.network
status: active
authors:
  - bradyhau
  - Claude Opus 5.5
last_updated: '2026-09-25'
summary: Explains how pod-to-pod traffic actually moves across the K3han cluster. flannel stays the CNI but its VXLAN overlay is idle; Tailscale subnet routes carry every cross-node packet in a single WireGuard tunnel. Defines the invariants this rests on, how they are verified, what was traded away, and what was rejected.
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
> not carry a single cross-node byte. Tailscale does. The two were never designed to share
> a node, so this document is mostly about where they meet and who wins.

---

## 1. Design Constraints (Red Walls)

*   **One tunnel, not two.** Cross-node pod traffic crosses the WAN inside exactly one
    encapsulation: WireGuard, via Tailscale. VXLAN-inside-WireGuard is a fallback that
    works but is never the intended steady state.
*   **The routing outcome is the invariant, not the flags.** On every node, the route to
    every *other* node's pod CIDR must resolve to `dev tailscale0 table 52`. The
    individual preconditions (§2.3) are each necessary and none is sufficient, so the
    kernel's final decision is what gets asserted.
*   **Cross-node pod traffic is never source-NATed.** A server pod sees the client's real
    pod IP, from any node. Nothing that reads a source address (access logs, per-IP rate
    limits, `pg_hba.conf`, broker ACLs) may be handed a node address instead.
*   **NetworkPolicy holds on both paths.** Same-node traffic (bridged) and cross-node
    traffic (routed) are both policed. This depends on
    `net.bridge.bridge-nf-call-iptables = 1`, which is a kernel invariant in
    [Cluster Strategy §3](safechord.chorde.k3han.cluster.md).
*   **Never lower `cni0` to the tunnel's MTU.** The one MTU step (`cni0` → `tailscale0`) is
    resolved by PMTUD on the first hop (§2.4). Pinning `cni0` to 1280 is the configuration
    that collapses throughput in
    [tailscale#16820](https://github.com/tailscale/tailscale/issues/16820).

---

## 2. Strategy / Policy Definition

### 2.1 Division of labour

| Concern | Owner | Notes |
| :--- | :--- | :--- |
| Pod IPAM (one `/24` per node from `.spec.podCIDR`) | flannel (CNI plugin) | Load-bearing |
| `cni0` bridge, veth wiring, pod default gateway | flannel (CNI plugin) | Load-bearing |
| Pod egress masquerade, `FLANNEL-FWD` accept rules | flannel (iptables) | Load-bearing: on `-P FORWARD DROP` nodes, `FLANNEL-FWD` is what admits unpoliced pod traffic |
| **Cross-node transport** | **Tailscale subnet routes** | Each node advertises its own pod CIDR and accepts the others' |
| VXLAN overlay (`flannel.1`) | flannel backend | **Idle.** Configured, up, 0 bytes received since boot |
| NetworkPolicy | kube-router (embedded in k3s) | Per-pod iptables chains, both routed and bridged |

"Is there a CNI?" Yes, and it is doing real work. What is idle is flannel's *backend*,
the part that was supposed to move packets between nodes.

### 2.2 How a packet travels

The fork happens inside the **pod's own routing table**, before the host is involved.
flannel writes three routes into every pod:

```
<own node /24>   dev eth0              ← same node: on-link, L2
10.42.0.0/16     via <cni0 address>    ← other nodes: hand to the gateway
default          via <cni0 address>
```

**Same node: switched at L2.**

```
pod A → veth → cni0 (bridge) → veth → pod B
```

The host's IP routing is never consulted: no `ip rule`, no table 52, no `tailscale0`.
iptables still sees the frame because `bridge-nf-call-iptables` hands bridged traffic to
it. kube-router's `-m physdev --physdev-is-bridged` rules are written for exactly this
case.

**Cross node: routed at L3.**

```
pod A → cni0 (frame addressed to the bridge itself) → host IP stack
  PREROUTING   conntrack; kube-proxy DNAT (Service VIP → pod IP)
  routing      ip rule 5270 → table 52 → 10.42.x.0/24 dev tailscale0
  FORWARD      kube-router NetworkPolicy; kube-proxy; ts-forward; FLANNEL-FWD
  POSTROUTING  KUBE-POSTROUTING → ts-postrouting → FLANNEL-POSTRTG
→ tailscale0 (TUN, no L2) → tailscaled (userspace) encrypts
→ a NEW UDP packet from tailscaled: OUTPUT → routing (fwmark 0x80000 → main) → eth0
```

Two points are worth pausing on:

*   **Each cross-node packet crosses netfilter twice on the sending node.** Once as the
    forwarded pod packet, and again as the WireGuard datagram tailscaled emits. The
    `0x80000` fwmark on tailscaled's own socket steers the second pass past table 52;
    without it the encrypted packet would be routed back into the tunnel.
*   **The hook order is kernel-fixed; the order *within* a hook is not.** PREROUTING →
    routing → FORWARD → POSTROUTING is hard-coded in the kernel and identical on every
    distribution and kernel we run. Rule order inside a chain is whoever inserted last
    (§2.5).

### 2.3 Why Tailscale wins the route, and what that depends on

Both systems install a route for each remote `10.42.x.0/24`. flannel puts
`via flannel.1` in the **main** table. Tailscale puts `dev tailscale0` in **table 52**.
Neither adds a competing `ip rule`. flannel adds none at all.

The kernel walks `ip rule` in ascending preference and takes the first table that has a
matching route. **Longest-prefix match applies within a table, never across tables.**
Tailscale's `5270: lookup 52` precedes the main table's `32766`, so table 52 wins
regardless of prefix length.

That outcome needs four things at once:

| Precondition | Held by | Declared where |
| :--- | :--- | :--- |
| Rule 5270 precedes the main table | Tailscale (a constant in its source) | Upstream; not ours to set |
| `--accept-routes` on every node | tailscaled prefs | Playbook |
| Each node advertises its own `.spec.podCIDR` | tailscaled prefs | Playbook |
| The advertised route is **approved** on the tailnet | Tailscale control plane | **Nowhere.** Approved by hand in the admin console |

When any one of them fails, nothing breaks. Traffic slides onto `flannel.1`, whose VTEPs
point at the Tailscale IPs (`--node-external-ip`, `--flannel-external-ip`), so the
fallback is VXLAN inside WireGuard. It is reachable, double-encapsulated, never measured,
and silent. That silence is why the playbook asserts the kernel's decision
(`ip route get` → `dev tailscale0 table 52`) rather than the four inputs.

### 2.4 MTU and PMTUD: the bottleneck is the first hop

Pods get `cni0`'s 1450; `tailscale0` is 1280. Linux TCP always sets DF, so the first
full-size segment is **dropped, not fragmented**. The sending node, acting as the pod's
first-hop router, answers with ICMP *fragmentation needed* (RFC 1191). The pod's kernel
caches a 1280 path MTU for that destination and TCP shrinks its segments. The cost is one
round trip per new path, repeated when the cache entry expires.

**The classic PMTUD black hole does not apply here.** A black hole needs the ICMP to cross
some middlebox that filters it. Here the ICMP is generated by the same host and delivered
over `cni0` to a local pod. It never leaves the node. The only things that could eat it
are local, and the obvious one is covered: every kube-router pod chain accepts traffic
from the local node (`--src-type LOCAL`) ahead of its default policy chains.

This is why `net.ipv4.tcp_mtu_probing` (RFC 4821 PLPMTUD, the ICMP-free fallback) is
**not** a kernel invariant. It would insure against a failure mode this topology does not
have.

### 2.5 Netfilter: shared, unarbitrated ownership

Three to four writers share each node's `filter` and `nat` tables: kube-router, kube-proxy
and flannel, Tailscale, plus ufw (`ct-serv-jp`) or Docker (`acer-agent`). iptables has no
priority between them; whoever last ran `-I CHAIN 1` goes first. kube-router re-asserts its
own jump at position 1 on resync, but it does not reorder anyone else.

Two properties make this safe enough to leave shared:

*   **Policy verdicts cannot be bypassed by ordering.** kube-router ends every denial with
    `REJECT` inside its own per-pod chain, so a denied packet never returns to `FORWARD` to
    meet Tailscale's blanket `ACCEPT`.
*   **Policy always sees the original source.** `FORWARD` (where policy runs) precedes
    `POSTROUTING` (where any masquerade happens).

And one policy decision closes the gap ordering *did* open:

*   **Tailscale subnet SNAT is off on every node** (`--snat-subnet-routes=false`). With it
    on, a node where `ts-forward` ran before kube-router's ACCEPT would mark every packet
    arriving on `tailscale0` and then masquerade it. That happened on `acer-agent`: every
    cross-node client reached its pods as the node's `cni0` address. flannel's own rules
    exempt pod→pod traffic from masquerade, but `ts-postrouting` runs first.

**Residual, accepted:** where `ts-forward` or `ts-input` sits above kube-proxy's chains
(currently `acer-agent`), traffic arriving on `tailscale0` is accepted before
`KUBE-PROXY-FIREWALL`, `KUBE-FORWARD` and `KUBE-FIREWALL` run. Only tailnet members can
send it, and no Service currently uses `loadBalancerSourceRanges`. See §5.

### 2.6 Verification

| Check | Where | What it proves |
| :--- | :--- | :--- |
| Peer-route gate | Playbook, end of the pod data path tasks | Every node routes every peer CIDR via `tailscale0 table 52`; prefs match |
| `node-routing-test.sh` | `Chorde/scripts/test/pod-path/` | The same gate on the live cluster, plus `bridge-nf-call-iptables` and `flannel.1` RX = 0 |
| `netpol-matrix-test.sh` | `Chorde/scripts/test/pod-path/` | 27 client→server probes across all node pairs: policy verdicts correct, real source IP seen |

Watch `flannel.1` **RX**, never TX. TX is nonzero on every node and is not pod traffic:
tailscaled's disco probes to peers' `10.42.x.0/.1` addresses carry the bypass fwmark, fall
through to the main table, and leave via `flannel.1` into nowhere.

---

## 3. Alternatives Considered

| Option | Verdict | Why |
| :--- | :--- | :--- |
| **flannel VXLAN as the transport** (the k3s default) | Replaced | Across a WAN it needs its own encryption and NAT traversal, which flannel does not do. Running it over the tailnet means two tunnels |
| **VXLAN over Tailscale** (`--flannel-iface=tailscale0`, k3s `--vpn-auth`) | Rejected | Double encapsulation into a 1280 tunnel, with `cni0` forced toward ~1230, the #16820 territory. `--vpn-auth` is still experimental. `--flannel-iface` was tried by hand and did not work on the k3s version of the time. Today this path is the silent fallback, not the plan |
| **flannel `wireguard-native`** | Rejected | A real single-layer design, but `acer-agent` sits behind residential NAT, and flannel does no NAT traversal. It trades Tailscale's hole-punching for hand-built keepalives |
| **Replace the CNI** (Cilium, or `--flannel-backend=none` + another) | Rejected | A live CNI swap on a cross-border three-node cluster, to remove an overlay that costs nothing |
| **Lower `cni0` to 1280** | Rejected | Measured elsewhere to collapse TCP throughput; PMTUD already resolves the step for free |
| **MSS clamping on each node** | Rejected | A hand-maintained constant doing PMTUD's job, for a black hole that cannot occur (§2.4) |
| **Tailscale `--netfilter-mode=off`** | Deferred | Removes the ordering race at the root, but `ct-serv-jp`'s ufw has no allow rules: its API server, kubelet and WireGuard port are admitted by `ts-input` alone |
| **Tailscale `--netfilter-mode=nodivert`** | Deferred (preferred next step) | Tailscale keeps its chains current and we place the jumps, at the tail where kube-* inserts cannot displace them. Ordering becomes declared, not raced |

**Why the result is convergent, not improvised.** Stretching one cluster across regions is
not the mainstream answer, because etcd wants single-digit-millisecond peers, and
`ct-serv-jp` ↔ `acer-agent` is ~80 ms. The projects that do span WANs, such as
[Kilo](https://kilo.squat.ai/) and Cilium with WireGuard, let one component own both
transport and MTU. That is the shape here: Tailscale owns the path end to end, and flannel
is reduced to local plumbing. It was assembled from two projects rather than chosen from
one, which is why their boundary needs this much documentation.

---

## 4. Reference Snapshots

> Point-in-time, **not SSOT**. Verified 2026-09-21 (throughput) and 2026-09-25 (the rest).

| Observation | Value | Validates |
| :--- | :--- | :--- |
| Cross-node pod→pod TCP, default MSS | 209 Mbit/s median | One tunnel runs at the path ceiling |
| Cross-node pod→pod TCP, MSS clamped to 1100 | 234 Mbit/s median | No measurable MTU cost (spread overlaps the row above) |
| Node→node over the tailnet | 232 Mbit/s median | Path ceiling |
| Same-node pod→pod | 32.1 Gbit/s | The bridge path never touches the tunnel |
| `tailscale0` vs `flannel.1` TX during a 10 s cross-node run | +215,542,969 B vs +1,460 B | Table 52 carries the traffic |
| `flannel.1` RX, all nodes | 0 B since boot | The VXLAN fallback has never been used |
| `IpFragCreates` / `IpFragFails` on `ct-serv-jp` since boot | 0 / 5353 | Drop-and-report PMTUD, never fragmentation |
| NetworkPolicy matrix (3 nodes × 3 clients × 3 servers) | 27/27 | Policy holds same-node and cross-node, ingress and egress |
| Source IP seen by servers after `NoSNAT` everywhere | Real client pod IP, all pairs | No source rewriting |

---

## 5. Trade-offs & Consequences

| Pros | Cons | Mitigation |
| :--- | :--- | :--- |
| One WireGuard tunnel end to end; runs at the path ceiling | Correct routing rests on Tailscale's rule preference, an upstream constant under open discussion ([tailscale#6231](https://github.com/tailscale/tailscale/issues/6231)) | Playbook gate + `flannel.1` RX tripwire. If the rule stops winning: `ip rule add not fwmark 0x80000/0xff0000 to 10.42.0.0/16 lookup 52 pref 5000`, persisted after tailscaled. This works only while Tailscale still uses table 52 |
| NAT traversal for the home node comes free with the tailnet | Subnet-route approval lives in the Tailscale admin console, outside git | Gate fails the play until a new node's route is approved. Declarative `autoApprovers` is open |
| No CNI replacement; flannel keeps doing what it does well | The node's config advertises an overlay that carries nothing; `flannel.1` and its routes mislead anyone reading `ip route` | This document |
| NetworkPolicy works unchanged, verified on every pair | Four writers share `FORWARD`/`INPUT` with no arbitration; on `acer-agent`, tailnet traffic skips kube-proxy's firewall chains | SNAT off removes the visible damage. `nodivert` is the planned root fix; chain-order tripwire planned |
| Loose `rp_filter` keeps asymmetric pod paths alive | Loose reverse-path filtering on every node | Required, not optional: see [Cluster Strategy §3](safechord.chorde.k3han.cluster.md) |

---

## 6. References

*   **Provisioning & gate**: `Chorde/cluster/k3han/ansible/privision.yaml`
*   **Recorded k3s units**: `Chorde/cluster/k3han/k3s/`
*   **Tests**: `Chorde/scripts/test/pod-path/`
*   **Tickets**: Chorde#16 (this design), Chorde#15 (the playbook has never run)
*   **Related Policies**: [Cluster Strategy](safechord.chorde.k3han.cluster.md) (kernel invariants), [Ingress Policy](safechord.chorde.k3han.ingress.md) (north-south traffic)
*   **External**: [Tailscale netfilter modes](https://tailscale.com/docs/reference/netfilter-modes), [Tailscale route injection](https://tailscale.com/docs/reference/route-injection), RFC 1191 (PMTUD), RFC 4821 (PLPMTUD)
