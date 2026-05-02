---
title: 'Policy: K3han Scheduling Strategy'
doc_id: safechord.chorde.k3han.scheduling
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Defines the resource orchestration logic for the K3han hybrid-cloud cluster. Covers Node Affinity, Taints, and operator-driven isolation to solve high-latency and resource contention challenges.
keywords:
  - Scheduling
  - Affinity
  - Taints
  - Data Locality
  - Reliability Tiering
logical_path: SafeChord.Chorde.K3han.Scheduling
related_docs:
  - safechord.chorde.k3han.cluster.md
  - safechord.safezone.deployment.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests
doc_version: 0.3.5
app_version: 0.3.0
---

# Scheduling & Orchestration Policy (Brain)

> **Strategic Goal**: Manage a highly asymmetric hybrid cloud by enforcing "Control Plane Locality" and "Reliability Tiering" to mitigate cross-border latency and resource scarcity.

---

## 1. Context & Challenges
K3han spans three distinct zones with vastly different characteristics:
*   **Contabo (JP)**: High stability, 12GB RAM, but ~80ms latency to Taiwan.
*   **GCE (TW)**: Premium peering, but only 1GB RAM and high bandwidth costs.
*   **Home (TW)**: High IOPS/CPU, Sunk Cost, but subject to consumer-grade ISP volatility.

Standard K8s scheduling is insufficient as it ignores "Bill risk" and "Home-lab power volatility."

## 2. Core Principles
1.  **Control Plane Locality**: Operators (CNPG, Strimzi, KEDA) must stay on Cloud nodes (<1ms API latency).
2.  **Data Locality**: Replicas and high-throughput brokers (Kafka/Redis) stay on Local nodes to save egress costs.
3.  **Edge Isolation**: The GCE node is restricted to traffic forwarding ONLY.
4.  **Reliability Tiering**: Use Taints to soft-reject critical production pods from landing on home-lab hardware unless tolerated.

---

## 3. Orchestration Decisions

### 3.1 Isolation Strategy (Taints)
| Taint Key | Effect | Target | Rationale |
| :--- | :--- | :--- | :--- |
| `node-role.kubernetes.io/control-plane` | `NoSchedule` | `ct-serv-jp` | **Master Protection**: Prevents business load from impacting ArgoCD/Operators. |
| `chorde.io/purpose=proxy-only` | `NoSchedule` | `gce-agent-tw` | **Ingress Protection**: Preserves 1GB RAM for Nginx-Ingress only. |
| `chorde.io/provider=local` | `PreferNoSchedule`| `acer-agent` | **Availability Filter**: Prevents non-fault-tolerant pods from landing on home hardware. |

### 3.2 Label Schema (v0.3.x Snapshot)
> 💡 **Reference**: Use these labels in your `nodeSelector` or `affinity` blocks.

| Label Key | Value | Purpose |
| :--- | :--- | :--- |
| `topology.kubernetes.io/region` | `jp` / `tw` | Geographic cost & latency calculation. |
| `chorde.io/provider` | `contabo` / `gce` / `local` | Hardware reliability grouping. |
| `chorde.io/tier` | `low` / `medium` / `high` | Resource capacity ranking. |
| `node.safechord.io/capability` | `high-iops` | Pins DBs/Kafka to local SSDs. |

---

## 4. Implementation Reference (YAML)

### Pattern: Pinning Operators to Cloud
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: node-role.kubernetes.io/control-plane
              operator: Exists
```

### Pattern: Pinning Replicas/Apps to Local TW
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: chorde.io/region
              operator: In
              values: ["tw"]
            - key: chorde.io/tier
              operator: In
              values: ["medium"]
```

---

## 5. Trade-offs & Consequences
*   **Pro**: Near-zero cross-border bandwidth costs for data replication.
*   **Pro**: Extreme stability for the GitOps and Operator layers.
*   **Con**: High `acer-agent` dependency. Replicas are lost if the home lab loses power.
*   **Mitigation**: Defined manual promotion scripts for cloud standby nodes.

## 6. References
*   **Inventory**: `Chorde/cluster/k3han/ansible/inventory.ini`
*   **Manifests**: Review Affinity blocks in `Chorde/gitops/k3han/manifests/`.
