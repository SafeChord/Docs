---
title: 'Platform: K3han Changelog'
doc_id: safechord.chorde.k3han.changelog
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-06-04'
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
doc_version: 0.3.6
app_version: 0.3.0
---

# K3han Platform Changelog

This document tracks the significant architectural shifts of the K3han cluster, serving as a historical reference for technical debt analysis and decision tracing.

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
