---
date: 2026-09-25
authors:
  - bradyhau
categories:
  - Case Study
tags:
  - Kubernetes
  - CNI
  - flannel
  - Tailscale
  - Networking
---

# The overlay that wasn't

*We set out to price a fragmentation cost on our cluster's pod network. The cost turned
out to be zero, because the overlay we were measuring had never carried a byte.*

> **This is a dated record, not a spec.** It describes what we believed and measured on
> the dates given. For how the pod network works *now*, read
> [Pod Data Path & CNI](../../safechord.chorde.k3han.network.md).

<!-- more -->

## The setup

K3han is a three-node k3s cluster that spans a border. The control plane is a VPS in
Japan, the public edge is a GCE micro instance in Taiwan, and the primary worker is a
bare-metal box in a house in Taiwan. The nodes reach each other over Tailscale, because
one of them sits behind a residential NAT, and the WAN between them is ~80 ms.

k3s ships flannel as its CNI, with a VXLAN backend. Our mental model of cross-node pod
traffic was therefore the one on every diagram:

```
pod → cni0 (1450) → VXLAN (+50) → tailscale0 (1280) → WireGuard → internet
```

Two tunnels, one inside the other. And the arithmetic looked bad: a 1450-byte inner
packet plus VXLAN's 50 bytes overshoots a 1280-byte tunnel by 220 bytes. We assumed the
kernel was fragmenting silently, and the job was to put a number on the cost.

## Act 1: the cost that wasn't there (2026-09-21)

The measurement plan was simple. Run iperf3 across nodes pod to pod, once unclamped and
once with the MSS clamped low enough that nothing could fragment, then compare.

| Run | Median |
| :--- | :--- |
| Cross-node pod→pod, default | 209 Mbit/s |
| Cross-node pod→pod, MSS 1100 | 234 Mbit/s |
| Node→node over the tailnet | 232 Mbit/s |

The clamped run already sat at the node-to-node ceiling, and the unclamped run's spread
overlapped it. There was no measurable gap to explain.

**Throughput alone would not have been convincing. The counters were.** `IpFragCreates`
stayed at 0 on both ends across every run. Nothing was being fragmented, which meant the
premise was wrong somewhere.

`ip route` looked exactly as expected, with `10.42.1.0/24 via 10.42.1.0 dev flannel.1`.
But Linux consults `ip rule` before any table, and Tailscale had installed a rule at
preference 5270 pointing at its own table 52:

```
# table 52 — consulted first
10.42.1.0/24 dev tailscale0
```

Every node advertised its pod CIDR as a Tailscale subnet route, and `--accept-routes`
installed the others' routes in a table that outranks main. The interface counters
around a 10-second cross-node run settled it: `tailscale0` sent **+215,542,969 bytes**
and `flannel.1` sent **+1,460**.

flannel was still the CNI. It allocated the addresses, built the bridge and wrote the
iptables rules. But its VXLAN overlay, the thing we had spent a day pricing, had never
received a single byte on any node since boot. There was one tunnel, not two.

## Act 2: it works, so where are the edges? (2026-09-25)

"It works and we don't know why" is not a comfortable place to run production from. The
setup had been arrived at by trial: an earlier attempt to pin flannel to the tailnet
interface had failed and been reverted. Nobody had designed this path, so nobody knew
where its failure modes were. The second session went looking.

**Two of our own first-round conclusions were wrong.**

- *"flannel.1 carries nothing."* Its TX counter was nonzero on every node, 263 MB on
  one. A tcpdump showed tailscaled's own discovery probes. Its packets carry a fwmark that
  skips table 52, fall through to the main table, and leave via `flannel.1` into nowhere.
  **RX** was the honest counter, and it was still 0.
- *"The fallback is a dead path."* flannel's VTEP endpoints turned out to be the nodes'
  Tailscale addresses. If table 52 ever stopped winning, traffic would not break. It would
  slide onto VXLAN *inside* WireGuard, the double-encapsulated path we had originally
  assumed was running: slower, never measured, and completely silent.

**One risk we had feared did not exist.** The first draft worried about PMTUD black holes:
if ICMP "fragmentation needed" were filtered somewhere on the internet, TCP would hang.
But the MTU step here is on the *first hop*. The sending node is the pod's router, it
generates the ICMP itself, and it delivers it over the local bridge. That ICMP never
crosses a network where anyone could drop it. Counters since boot: 0 fragments created,
5,353 packets dropped with an ICMP reply. That is PMTUD working exactly as RFC 1191
describes.

**One bug was real, and it was already happening.** Tailscale and kube-router, the
NetworkPolicy engine k3s embeds, both write iptables' `FORWARD` chain. Neither knows the
other exists, and iptables has no priorities, so whoever inserts last goes first. On one
node Tailscale had won. Its rule marked every packet arriving from the tunnel, and its
NAT rule then masqueraded them.

We deployed a probe matrix: a server on each node, allowed and denied clients on each
node, and 27 pairs in all. **Every policy verdict was correct**, because netfilter runs
`FORWARD` before `POSTROUTING`, so policy always sees the original address. But every
server on the affected node saw every cross-node client as `10.42.1.1`, the node's own
bridge address. Access logs, rate limits and database host rules would all have
recorded one address for everyone. One flag, `--snat-subnet-routes=false`, fixed it. We
rolled it out node by node with the matrix re-run after each change.

**And the provisioning code could not rebuild any of it.** The playbook discovered each
node's pod CIDR by grepping for Traefik's load-balancer pods. Traefik had been disabled
long ago, so discovery always returned nothing, and the advertise step was always
skipped, under `ignore_errors` anyway. The route approval that makes the whole thing work
had been clicked by hand in the Tailscale admin console and was recorded nowhere.

## What we changed

- **Assert the outcome, not the inputs.** The path depends on four things at once: the
  rule preference, `--accept-routes`, each node advertising its own CIDR, and approval.
  Checking each one separately misses the combination. The playbook now ends with a gate
  that asks the kernel directly, with `ip route get`, whether every peer's pod CIDR
  resolves to `dev tailscale0 table 52`. The same gate runs as a read-only script against
  the live cluster.
- **Stop depending on chain order where we can.** SNAT is off on every node. The ordering
  race itself remains. The planned fix is Tailscale's `nodivert` mode, which lets us place
  its jumps at the chain tail where nothing can displace them.
- **Write down what the kernel was doing.** Our docs had justified loose reverse-path
  filtering as a tolerance for "VXLAN alongside Tailscale". The real reason is stricter:
  pod packets arrive on `tailscale0` while their reverse route points at `flannel.1`, so
  strict mode would drop every one of them. The value was right and the reasoning was
  wrong, and the next person hardening that setting would have broken the cluster.

## It turns out someone had designed this

After all of that, we found the architecture already had a name. [Kilo](https://kilo.squat.ai/),
a multi-cloud Kubernetes overlay built on WireGuard, ships a flannel add-on mode:
*"Kilo will take care of the network between locations, while Flannel will take care of
the network within locations."* That is our split, with Tailscale in Kilo's seat.

The comparison is useful in both directions:

- **What we gain.** Kilo needs a publicly routable node in each location. Tailscale does
  not, which is what lets a house behind a NAT join at all.
- **What we lose.** Kilo reads pod CIDRs from Kubernetes and programs its routes itself.
  We had to build that reconciliation, and it had been silently broken.

## Lessons

1. **Counters beat throughput.** Three iperf runs on a public path produce noise, and
   `IpFragCreates = 0` settles the question in one read.
2. **Documentation absence has a cost.** No document stated which component carried pod
   traffic, and that single gap sent a day of measurement after the wrong mechanism.
3. **"It works" hides the edges.** Every failure mode we found was silent by construction,
   including a fallback that works, an address rewrite that passes policy, and a playbook
   step that skips cleanly. None of them would ever have paged anyone.
4. **Two systems that each assume they are the top layer will eventually disagree.** Here
   it happened twice, once in the routing table and once in iptables, and nothing
   arbitrated either.

*Tracked in [Chorde#16](https://github.com/SafeChord/Chorde/issues/16).*
