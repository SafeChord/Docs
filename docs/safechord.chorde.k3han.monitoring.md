---
title: 'Policy: K3han Monitoring Stack'
doc_id: safechord.chorde.k3han.monitoring
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Defines the observability architecture for the K3han hybrid-cloud cluster. Covers metrics (Prometheus), log offloading to S3 (Loki), and the use of heterogeneous agents (Alloy & Fluent-bit).
keywords:
  - Monitoring
  - Observability
  - Prometheus
  - Loki
  - Alloy
  - Zero Trust
logical_path: SafeChord.Chorde.K3han.Monitoring
related_docs:
  - safechord.chorde.k3han.md
  - safechord.security.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests/monitoring
tech_stack:
  - Prometheus Operator
  - Loki (S3 Storage)
  - Grafana Alloy
  - Fluent-bit
doc_version: 0.3.5
app_version: 0.3.0
---

# Observability & Monitoring Policy (Brain)

> **Core Rationale**: Adopt a "Zero-Local-Footprint" strategy to overcome edge node disk I/O limits and retention costs in a heterogeneous hybrid cloud.

---

## 1. Design Vision
K3han utilizes cloud-native storage offloading and heterogeneous agents to achieve high visibility without taxing local resources.

*   **S3-Offloading**: All log data is asynchronously pushed to Cloud Object Storage (S3), decoupling log durability from node uptime.
*   **Heterogeneous Agents**:
    *   **Alloy**: Heavy-duty relabeling on high-performance nodes.
    *   **Fluent-bit**: Minimal footprint on resource-constrained edge nodes.
*   **GitOps Driven**: Monitoring CRDs are synchronized first (`sync-wave: 1`) to enable auto-discovery for application services.

---

## 2. Metrics & Logs Architecture

### 2.1 Prometheus (Metrics)
*   **Retention Target**: Short-term only (days, not weeks) — long-term analysis relies on Grafana dashboards and S3-backed Loki logs.
*   **Storage Constraint**: Must fit within a single small Local PV to avoid competing with app workloads (Postgres/Kafka) for disk I/O.
*   **Security**: Grafana is gated via `nginx-private` (Tailscale) + Cloudflare Access (OIDC).

> *Current retention and storage values are defined in Prometheus CRDs under `code_paths`.*

### 2.2 Loki (Logs)
*   **Mode**: SingleBinary — chosen for MVA simplicity; migrate to microservice mode when log volume exceeds single-node capacity.
*   **Backend Constraint**: Cloud Object Storage in a region co-located with the Control Plane to minimize egress latency.
*   **Credential Masking**: S3 keys are strictly managed via `SealedSecrets`; Pods only see `SecretKeyRefs`.

> *Backend configuration (provider, region, bucket) is defined in Loki manifests under `code_paths`.*

---

## 3. Implementation Standards

### 🏷️ Label Normalization (Mandatory)
Agents must automatically extract and normalize the following tags for cross-cluster querying:
*   `namespace`: The K8s namespace.
*   `pod`: The Pod name.
*   `container`: The container name.
*   `node_name`: Physical host ID.
*   `job`: Scraper category (e.g., `alloy`, `fluent-bit`).

### 🛡️ Log Sanitization
*   **Rule**: Agents MUST drop log lines containing `password`, `bearer`, or `api_key` via regex filters before offloading to S3.

---

## 4. Trade-offs & Consequences
*   **Pros**: Local disk I/O is 100% available for app workloads (Postgres/Kafka).
*   **Pros**: Logs are permanent even if a home-lab node is wiped.
*   **Cons**: Introduces S3 operational costs and cross-region egress traffic.
*   **Mitigation**: Aggressive log dropping of non-essential noise (sidecar heartbeats, debug-level probes).

## 5. References
*   **Log Queries**: Use `LogCLI` for terminal-based retrieval.
*   **App Monitoring**: Defined via `SafeZone-Deploy` (ServiceMonitors).
