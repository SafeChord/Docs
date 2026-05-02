---
title: 'Map: Chorde Platform Framework'
doc_id: safechord.chorde
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Navigational map for the Chorde platform layer. Defines the multi-cluster management framework, GitOps v2 synchronization mechanisms, and infrastructure lifecycle policies.
keywords:
  - Chorde
  - Platform Layer
  - Multi-cluster
  - GitOps v2
  - ApplicationSet
  - Hybrid Cloud
logical_path: SafeChord.Chorde
related_docs:
  - index.md
  - safechord.chorde.k3han.md
parent_doc: safechord
archetype: map
code_paths:
  - Chorde/cluster
  - Chorde/gitops
doc_version: 0.3.5
app_version: 0.3.0
---

# 🛠️ Chorde Platform Map

> **Type**: Map (Infrastructure Command Center)
> **Context**: Manages heterogeneous clusters, implements GitOps v2 delivery, and maintains hybrid-cloud security perimeters.

---

## 1. Platform Vision

**Chorde** (Cluster + Horde) aims to establish a "decentralized yet highly coordinated" infrastructure tribe. As of v0.3.0, the platform has transitioned from simple IaC scripts to an **Operator-managed** modern architecture, realizing the KDD loop of "Code as Environment, Docs as Source."

---

## 2. Repository Structure

Chorde utilizes a **Recursive GitOps v2** architecture, enabling automated orchestration through a single entry point (`root.yaml`).

```text
Chorde/
├── cluster/                 # [Physical] Hardware & OS-level definitions
│   └── k3han/               
│       ├── ansible/         # Record of Actions: Node initialization & OS hardening
│       └── k3s/             # Node Descriptors: K3s configuration backups
│
├── gitops/                  # [State] GitOps Desired State (SSOT)
│   └── k3han/               
│       ├── root.yaml        # Entry Point: The Root Application
│       ├── stages/          # [Layer 0: Orchestrator] Stage-based ApplicationSets
│       │   ├── 00-bootstrap.yaml  # Core: ArgoCD, SealedSecrets, Ingress
│       │   ├── 01-platform.yaml   # Ops: Monitoring, Logging, Operators
│       │   └── 02-components.yaml # App: DB, MQ, SafeZone Microservices
│       │
│       └── manifests/       # [Content] Declarative Resources (YAML/Helm)
│           ├── alloy/       # Multiple Sources Pattern
│           ├── cnpg-*/      # CloudNativePG Operator & Clusters
│           └── ...          # 20+ Platform services
│
├── scripts/                 # [Lifecycle] Operational & Validation Tools
│   ├── ops/                 # bootstrap-cluster.sh, seal.sh
│   └── test/                # Cross-region connectivity & health checks
│
└── legacy/                  # [Archive] Historical configurations (v0.1.x / v0.2.x)
```

---

## 3. Core Component Navigation

### 3.1 Runtime Clusters
*   [**K3han (Hybrid K3s)**](safechord.chorde.k3han.md) ⭐:
    *   **Context**: Highly asymmetric Taiwan-Japan hybrid cloud.
    *   **Status**: Running K3s v1.34+, utilizing Tailscale SDN to mask geographic latency.

---

## 4. Engineering Practices (v2)

Chorde strictly adheres to the following SRE principles:

1.  **ArgoCD Multiple Sources**: Abandoned local `helm-charts/` copies. Directly references Upstream Helm Charts paired with local `values-custom.yaml` overlays.
2.  **ApplicationSet Pattern**: Replaced monolithic `Application` manifests with `ApplicationSet` for automated service discovery and tiered synchronization (Sync Waves).
3.  **Operator-First**: Foundation services (DB, Kafka, Postgres) are entirely **Operator-managed**, ensuring self-healing and zero-downtime upgrades.
4.  **Availability Tiers**: Leverages Taints (`PreferNoSchedule`) to establish availability zones between on-prem and cloud nodes, preventing critical workloads from landing on non-HA nodes.
5.  **Test-Driven Ops**: Major configuration changes must be validated via scripts in `scripts/test/` to satisfy the "Test is the Law" policy.

---

## 5. Quick Access

*   **Cluster Map**: [K3han Hybrid Cluster Map](safechord.chorde.k3han.md)
*   **Scheduling Logic**: [K3han Scheduling Brain](safechord.chorde.k3han.scheduling.md)
*   **Source Code**: [SafeChord/Chorde (GitHub)](https://github.com/SafeChord/Chorde)
