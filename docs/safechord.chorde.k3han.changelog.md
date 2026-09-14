---
title: 'Platform: K3han Changelog'
doc_id: safechord.chorde.k3han.changelog
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5
last_updated: '2026-09-14'
summary: Records the architectural evolution of the K3han cluster. Tracks changes in node layout, GitOps orchestration, operator management, and design philosophy shifts since v0.1.0.
keywords:
  - K3han
  - Changelog
  - Infrastructure Evolution
  - Release Notes
  - GitOps v2
logical_path: SafeChord.Chorde.K3han.Changelog
related_docs:
  - safechord.knowledgetree.md
  - safechord.chorde.k3han.md
parent_doc: safechord.chorde.k3han
tech_stack: []
doc_version: 0.3.7
app_version: 0.3.0
---

# K3han Platform Changelog

This document tracks the significant architectural shifts of the K3han cluster, serving as a historical reference for technical debt analysis and decision tracing.

---

## 🔖 [v0.3.7] - 2026-09-14

### 🧬 Node Dimensions & Kernel Invariants (Chorde #10, #13)
*   **Kernel Invariants Documented**: Two outages this month (`SafeZone#63`, plus a control-plane wedge that recurred for 11 and 16 days) traced to kernel parameters that lived only on live hosts and appeared in **no document**. `inotify` quota, `ip_forward` and loose `rp_filter` are now red walls in the Cluster Brain, stated on the **effective** value rather than on the drop-in file — `sysctl --system` is last-write-wins, so writing a file was never evidence it won.
*   **`node_platform` Dimension Added**: New inventory variable (`bare-metal` | `vm`) discriminating hardware class. Introduced because `node_provider` cannot express it — `local` records that a box sits in the operator's house, not that it is bare metal. First consumer is firmware-tooling removal on guests.
*   **External Addressing Policy**: `node_external_ip` recorded per node, governed by a publication rule rather than treated as bookkeeping — `Chorde` is public, so an empty value means "not recorded here", never "none exists". `ct-serv-jp`'s address remains an **open decision**.
*   **Control Plane Hardware & Cost Corrected**: `ct-serv-jp` had been recorded as 6 vCPU / 12GB at ~NT$350/mo since v0.3.0. Both were wrong in the same direction — the node runs **8 vCPU / 24GB** at **USD $9.55/mo** (≈NT$300). Contabo's 2026-05-07 price rise bundled a free higher-spec upgrade, which is why the spec and the price moved together. The NT$800/mo red wall holds with ~NT$50/mo more headroom than the old figures showed, though it is **denominated in NT$ against USD-billed inputs** and therefore exposed to FX on its own.
*   **Node Rename Reconciled**: `hz-serv-sin` → `ct-serv-jp`, `node_provider` `hetzner` → `contabo`, completing a migration that had lived only in the inventory.

> ⚠️ **Enforcement gap**: the provisioning playbook carrying these invariants has never been executed — no ansible reaches any project machine. `Chorde#15` owns closing that; until then the invariants are written intent with no runtime assert.

---

## 🔖 [v0.3.6] - 2026-06-04

### 🌐 NGINX Gateway Fabric & Gateway API Migration (Issue #4, #6)
*   **Ingress Engine Swap**: Retired EOL `kubernetes/ingress-nginx` (CVE-2026-42945). Standardized on **NGINX Gateway Fabric (NGF v2.6.3)** and **Kubernetes Gateway API (v1.5)**.
*   **Decoupled Control/Data Planes**:
    *   Unified Control Plane pinned to master node (`ct-serv-jp`).
    *   Isolated Private Data Plane (`private-gateway`) run as a `ClusterIP` Service on `ct-serv-jp`.
    *   Public Data Plane (`public-gateway`) pinned via node label `chorde.io/purpose=proxy-only` to TW GCE Edge node using `hostPort 80/443` with memory limits tuned for the 1GB RAM constraint.
*   **Zero-Trust Private Tunneling**: Transitioned host systemd-managed Cloudflare Tunnels and Tailscale-NIC bindings to an **in-cluster `cloudflared` Deployment** forwarding traffic securely to the private gateway `ClusterIP`.
*   **Gateway Filter Hardening**:
    *   Unified SSL termination with wildcard certs at Gateway listener.
    *   Applied Gateway API filters: `AuthenticationFilter` (Basic Auth), `URLRewrite` (path rewrites), `ResponseHeaderModifier` (stripped `X-Powered-By`).
    *   Enforced per-IP `RateLimitPolicy` (HTTP 429) at TW edge.
    *   Configured `NginxProxy.rewriteClientIP` to restore real client IPs (synchronized with GCP VPC firewall rules).

---

## 🔖 [v0.3.5] - 2026-05-02

### 🏗️ Documentation Modernization
*   **Archetype Shift**: Formally transitioned all Infrastructure specifications from `Blueprint` to `Brain` archetypes.
*   **English-First SSOT**: Completed the full English rewrite of the Chorde documentation stack, establishing the root `/docs/` as the Single Source of Truth.
*   **Strategy Consolidation**: Merged high-level roadmaps and evolution guides into the core platform maps.

---

## 🔖 [v0.3.0] - 2026-03-07

### 🚀 GitOps v2 Refactoring
*   **Recursive Orchestration**: Introduced ArgoCD `ApplicationSet` to replace monolithic `Application` manifests, enabling dynamic service registration and tiered dependency management.
*   **Three-Stage Sync (Stages)**: Implemented a mandatory sync wave strategy:
    *   `00-bootstrap`: Security, Ingress, and Controllers.
    *   `01-platform`: Monitoring, Logging, and Operators.
    *   `02-components`: Databases, Queues, and SafeZone services.
*   **Global Entry Point**: Established `root.yaml` as the centralized orchestrator for the entire cluster.

### 🛡️ Operator-First Migration
*   **Database**: Migrated from Bitnami-style Helm charts to **CloudNativePG (CNPG)** for automated failover and native Kubernetes backup integration.
*   **Messaging**: Migrated Kafka from standard charts to **Strimzi Operator**, simplifying the lifecycle of brokers and topics.
*   **ArgoCD Multiple Sources**: Adopted the Multiple Sources pattern to reference official upstream Helm charts while overlaying local `values-custom.yaml`, drastically reducing repository bloat.
*   **Deprecation**: Formally retired the local `helm-charts/` directory in the Chorde repository.

### 📊 Observability Enhancements
*   **S3 Log Offloading**: Successfully migrated the Loki storage backend to Amazon S3 (JP region), enabling zero-local-footprint log retention.
*   **Telemetry Hardening**: Optimized Prometheus scrape rules to filter out noise from Grafana and sidecar probes.

---

## 🔖 [v0.2.0] - 2024-05-09

### 🏗️ Topology Stabilization
*   **Single Control Plane**: Consolidated the control plane on `ct-serv-jp` (Contabo Japan).
*   **Edge Gateway**: Established `gce-agent-tw` as the sole public ingress point for Taiwan traffic, shielding internal UI modules from direct exposure.
*   **Data Locality**: Focused display modules and PostgreSQL replicas on `acer-agent` (Home TW) to leverage local high-speed I/O.
*   **Mesh Hardening**: Redesigned node labels and taints to reflect reliability tiering (Cloud vs. Local).

---

## 🏁 [v0.1.0] - 2024-05-04

### 📦 Initial MVP (Proof of Concept)
*   Verified hybrid-cloud feasibility using nodes in Singapore (Hetzner) and Taiwan (GCP).
*   Implemented initial Tailscale overlay mesh for NAT traversal.
*   Established basic master-replica PostgreSQL synchronization across geographic regions.
