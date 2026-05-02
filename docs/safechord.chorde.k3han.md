---
title: 'Map: K3han Hybrid Cluster'
doc_id: safechord.chorde.k3han
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Navigational map for the K3han subsystem. Indexes specification documents regarding hybrid-cloud topology, network perimeters (Ingress), and resource scheduling policies.
keywords:
  - K3han
  - Map
  - Hybrid Cloud
  - Index
  - Navigation
logical_path: SafeChord.Chorde.K3han
related_docs:
  - safechord.chorde.md
  - safechord.chorde.k3han.cluster.md
  - safechord.chorde.k3han.ingress.md
  - safechord.chorde.k3han.scheduling.md
parent_doc: safechord.chorde
archetype: map
code_paths:
  - Chorde/cluster/k3han
  - Chorde/gitops/k3han
doc_version: 0.3.5
app_version: 0.3.0
---

# 🗺️ K3han Subsystem Map

> **Type**: Map (Cluster Knowledge Hub)
> **Context**: The core runtime for SafeChord, built on K3s and Tailscale.

### 🏷️ Etymology
**K3han** = **K3s** + **Khan** (可汗).
Inspired by the vast and Coordination-heavy empires of history. In its initial architecture, K3han penetrated the network barriers between Japan (Contabo) and Taiwan (GCE/Home) using Tailscale, establishing a cross-border, lightweight operational territory.

---

## 1. Documentation Index

Select a specialized node for deep-dive specifications:

| Domain | Document | Summary | Archetype |
| :--- | :--- | :--- | :--- |
| **Topology** | [**Cluster Strategy**](safechord.chorde.k3han.cluster.md) | **Hardware & Mesh**. Defines Contabo/GCE/Home node specs, geographic distribution, and Tailscale mesh architecture. | `Brain` |
| **Networking** | [**Ingress Policy**](safechord.chorde.k3han.ingress.md) | **Traffic Ingress**. Defines the Public/Private dual-channel strategy, SSL termination, and firewall hardening. | `Brain` |
| **Orchestration** | [**Scheduling Logic**](safechord.chorde.k3han.scheduling.md) | **Resource Placement**. Explains data locality decisions (DB placement) and control-plane isolation (Taints). | `Brain` |
| **Observability** | [**Monitoring Stack**](safechord.chorde.k3han.monitoring.md) | **Telemetry**. Defines the Prometheus/Loki stack and multi-dimensional log collection patterns. | `Brain` |
| **History** | [**Changelog**](safechord.chorde.k3han.changelog.md) | **Evolution**. Records the architectural shifts of K3han from v0.1.0 to v0.3.x. | `Timeline` |

---

## 2. System Context

**K3han** is an experimental cluster designed to validate the **MVA (Minimum Viable Architecture)** philosophy. It proves that even with extreme resource constraints and suboptimal network environments, a high-availability Kubernetes environment can be constructed via Software-Defined Networking (SDN).

### Key Characteristics
*   **Hybrid Cloud**: Spans GCP (Taiwan), Contabo (Japan), and Home Lab (Taiwan).
*   **Overlay Mesh**: All nodes interconnected via Tailscale Mesh, bypassing NAT and firewall restrictions.
*   **Recursive GitOps v2**: Utilizes an **ArgoCD ApplicationSet** synchronization strategy (Stages -> Manifests) for dynamic service discovery.

---

## 3. Implementation Assets

*   **Source Paths**:
    *   Cluster Provisioning: `Chorde/cluster/k3han/` (Ansible & systemd units)
    *   GitOps Entry: `Chorde/gitops/k3han/root.yaml` (Points to stages/)
    *   Service Inventory: `Chorde/gitops/k3han/manifests/` (Multiple Sources Pattern)
*   **Access**:
    *   Refer to the [Ingress Policy](safechord.chorde.k3han.ingress.md) to understand how to access management interfaces via authorized tunnels.
