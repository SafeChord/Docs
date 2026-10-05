---
title: 'Policy: K3han Persistent Storage'
doc_id: safechord.chorde.k3han.storage
status: active
authors:
  - bradyhau
  - Claude Opus 5.5
last_updated: '2026-10-05'
summary: Defines where stateful platform workloads on K3han keep their data and what each volume is expected to survive. Volumes are static node-local PVs on the node their consumer is pinned to; durability against node loss comes from the data being rebuildable, not from the volume.
keywords:
  - Persistent Volume
  - Local Volume
  - NFS
  - Durability
  - Data Locality
logical_path: SafeChord.Chorde.K3han.Storage
related_docs:
  - safechord.chorde.k3han.md
  - safechord.chorde.k3han.scheduling.md
  - safechord.chorde.k3han.cluster.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests
  - SafeZone-Deploy/deploy
tech_stack:
  - Kubernetes local volumes
  - CloudNativePG
  - Strimzi
  - Valkey
doc_version: 0.3.9
app_version: 0.3.0
---

# Persistent Storage Policy (Brain)

> **One-line version**: a volume sits on the same node as the pod that uses it, and nothing
> on the home node is allowed to be irreplaceable.

---

## 1. Design Constraints (Red Walls)

*   **No network filesystem in front of a local disk.** When a workload is pinned to one
    node, its volume is a local volume on that node.
*   **No fsync across the WAN.** A workload that fsyncs (PostgreSQL, Kafka, Valkey with AOF)
    never has its volume on a different node from its pod.
*   **A replica never shares a disk with its primary.**
*   **Nothing irreplaceable on home hardware.** `acer-agent` has one disk, shared by the OS
    and every volume on it; losing the disk loses the node. Data placed there must be
    rebuildable from a cloud node or from git. The source of truth stays on `ct-serv-jp`.
*   **Every static PV is reserved for its claim.** A PV names its claim in `claimRef`. Two
    PVs of the same size and class on the same node are otherwise interchangeable to the
    binder.
*   **Operator-swappable data stays at an operator-chosen host path.** The simulator's input
    file is replaced on the host on purpose; whatever backs it must keep that path
    addressable.

## 2. Strategy / Policy Definition

### What a volume is for

A volume here answers one question: *what must still be there after the pod restarts?* It
does not answer *what must survive the node*. That second question is settled by where the
data can be rebuilt from.

| Workload | Node | The volume protects | Rebuilt from, if the node is lost |
| :--- | :--- | :--- | :--- |
| PostgreSQL primary | `ct-serv-jp` | The system's source of truth | Not rebuildable. This is the data the others derive from. |
| PostgreSQL replica | `acer-agent` | A streaming copy | The primary, by `pg_basebackup` |
| Kafka broker | `acer-agent` | Messages acknowledged to the producer but not yet consumed; the cluster's identity and consumer offsets | The topic is declared as a `KafkaTopic`; in-flight messages are lost and replayed by the simulator |
| Valkey | `acer-agent` | System state (status and simulated time) | Lost. Whether the application reinitialises it cleanly has not been verified. |
| Simulator input | `acer-agent` | A read-only CSV | The SafeZone repository |

Kafka runs as a single broker with a replication factor of 1, so the volume is the only
thing that makes an acknowledgement mean anything. That is why it is persistent rather than
ephemeral: with `emptyDir`, every pod recreation would silently drop messages the ingestor
believes were delivered.

### Static node-local volumes

*   **Approach**: Each volume is a pre-created `local` PV with a `nodeAffinity` naming its
    node and a host path under `/mnt/k3han-pv/`. The class is `local-path`. Because the PV
    is reserved through `claimRef`, the claim binds to it directly and the `local-path`
    provisioner never creates a volume of its own.
*   **Rationale**: The scheduling policy already pins these workloads to one node
    ([Scheduling §2](safechord.chorde.k3han.scheduling.md)). A local volume states that
    dependency in the PV instead of hiding it behind a mount that only works from that node.

### Rejected: an NFS server on the control plane

Until 2026-10 the volumes on `acer-agent` were NFS exports that the node mounted from itself.
When the node's disk came under suspicion, the first plan was to move the export to
`ct-serv-jp` and leave the pods where they were. It was dropped:

*   It protects data that is already rebuildable, and does not protect the service: the
    pods still die with the node.
*   Every fsync would cross the Taiwan–Japan link, and the mount is `hard`, so a Tailscale
    outage would hang the workloads rather than fail them.
*   The replica would sit on the same disk as the primary.

### Changing the storage of a running workload

None of the three operators applies a storage class change to a live workload: StatefulSet
`volumeClaimTemplates` are immutable, Strimzi rejects a class change on an existing node
pool, and CloudNativePG leaves an existing claim alone. Because ArgoCD tracks `main` with
self-heal and prune, the new manifests must be merged first, and each workload is then
recreated by hand:

*   Delete the claim before the owning resource, so the recreated workload cannot reuse it.
*   For data moved in place, do not create the target directory in advance. A local PV whose
    path is missing holds the new pod in `ContainerCreating` until the data arrives.
*   For a Kafka node pool, delete the pool and keep the `Kafka` resource: the pod set
    belongs to the pool, the cluster ID belongs to `Kafka`.
*   For a replica, delete the `Cluster` and let it bootstrap again.

## 3. Reference Snapshots

> Verified 2026-10-05, during the cutovers recorded in Chorde #27 / #28 / #29 and SafeZone-Deploy #18.

| Observation | Value | Constraint Validated |
| :--- | :--- | :--- |
| `acer-agent` → `ct-serv-jp` RTT over Tailscale (direct) | 35 ms | No fsync across the WAN |
| Disks on `acer-agent` | 1 (OS and volumes share it) | Nothing irreplaceable on home hardware |
| Replica rebuild by `pg_basebackup` | Healthy 26 s after recreation, streaming at the primary's LSN | Replica is rebuildable |
| Kafka after moving its log directory | Same cluster ID, end offsets and committed group offsets; lag 0 | Volume preserves cluster identity |
| Valkey after moving its data directory | Same keyspace, AOF loaded | Volume survives pod recreation |
| Simulator input after copying it to its new path | Same size and sha256 on the host and in the pod; mounted read-only from the local disk | Volume is rebuildable from a copy |
| NFS left on `acer-agent` | No mounts, no server, no client packages; the `local-nfs` class is deleted | No network filesystem in front of a local disk |

> *Current values live in manifests under `code_paths`.*

## 4. Trade-offs & Consequences

| Pros | Cons | Mitigation |
| :--- | :--- | :--- |
| Local fsync latency; no dependency on Tailscale for disk I/O | A volume cannot follow its pod to another node | The workloads were already pinned; moving one means rebuilding its data on the target |
| The PV states which node holds the data | Losing `acer-agent` loses the replica, in-flight Kafka messages and Valkey state together | The replica and Kafka are rebuildable and the primary is on a cloud node; Valkey's recovery is unverified (§2) |
| No NFS server to operate for these workloads | Host directories are created and removed by hand | Paths follow one convention, `/mnt/k3han-pv/<workload>`. The simulator input exists once per environment, so it sits at `/mnt/k3han-pv/safezone/simulator/<env>/covid-data` |

**Not established.** Why the `acer-agent` disk intermittently goes undetected at boot. SMART
reported no reallocated, pending or uncorrectable sectors on 2026-10-05.

**Not tested.** Whether replacing the simulator's CSV on the host reaches a running pod.
The file is mounted alone through a `subPath`, which is expected to keep serving the old
file when the new one is swapped in by rename rather than overwritten in place. Until it
is tested, restart the simulator pod after a swap.

## 5. References

*   **Manifests**: the `PersistentVolume` beside each workload under `code_paths`; the
    simulator's are per environment, under `SafeZone-Deploy/deploy/<env>/infra/foundation`
*   **Related Policies**: [Scheduling Logic](safechord.chorde.k3han.scheduling.md), [Cluster Strategy](safechord.chorde.k3han.cluster.md)
*   **Tickets**: Chorde #27, Chorde #28, Chorde #29, SafeZone-Deploy #18
