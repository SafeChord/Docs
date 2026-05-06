---
title: 'Policy: K3han Monitoring & Observability'
doc_id: safechord.chorde.k3han.monitoring
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-06'
summary: Defines the strategic observability architecture for the K3han hybrid-cloud cluster. Focuses on balancing monitoring overhead across asymmetric hardware (GCE 1GB vs Home 16GB), ensuring log persistence via S3 archiving, and routing actionable alerts while suppressing K3s structural noise.
keywords:
  - Monitoring
  - Observability
  - Prometheus
  - Loki
  - Alloy
  - Fluent-bit
  - S3 Offloading
  - Tailscale Mesh
  - Alertmanager
logical_path: SafeChord.Chorde.K3han.Monitoring
related_docs:
  - safechord.chorde.k3han.cluster.md
  - safechord.chorde.k3han.scheduling.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests/prometheus
  - Chorde/gitops/k3han/manifests/loki
  - Chorde/gitops/k3han/manifests/alloy
  - Chorde/gitops/k3han/manifests/fluent-bit
tech_stack:
  - Prometheus Operator (7d local retention)
  - Loki (SingleBinary with S3 Archiving)
  - Grafana Alloy (tier: medium — acer-agent)
  - Fluent-bit (tier: low — GCE Ingress)
doc_version: 0.3.9
---

# Observability & Monitoring Policy (Brain)

The K3han monitoring stack is designed to provide high-fidelity visibility across a heterogeneous hybrid-cloud environment while protecting the hardware integrity of resource-constrained gateway nodes.

---

## 1. Vision & Problem Statement

In a cluster spanning high-performance home-lab hardware and memory-starved GCE instances, standard patterns fail. K3han solves three core challenges:
*   **Networking Gaps**: Nodes in different regions cannot see each other's private IPs; we must scrape across the **Tailscale Mesh**.
*   **Hardware Asymmetry**: Monitoring agents must not starve the 1GB RAM gateway (GCE), while leveraging the i5-8500 (Home Lab) for heavy processing.
*   **Volatility**: Logs must survive even if the Home Lab (the primary compute node) goes offline due to local ISP or power issues.

---

## 2. Tiered Deployment Strategy

We adopt a **"Centralized Control, Distributed Collection"** pattern based on node capabilities:

| Component | Placement | Rationale |
| :--- | :--- | :--- |
| **Control Plane** (Prometheus / Grafana / Alertmanager / Loki) | `ct-serv-jp` (JP) | Pinned to the stable Japan Hub to ensure monitoring remains queryable during Taiwan-side outages. |
| **Alloy Agent** | `acer-agent` (TW-Home) | Deployed on `chorde.io/tier: medium` nodes. Handles complex relabeling and heavy-duty log processing. |
| **Fluent-bit** | `gce-agent-tw` (TW-GCE) | Deployed on `chorde.io/tier: low` nodes. Uses a "forward-only" profile to preserve memory for Ingress traffic. |

---

## 3. Observability Pipeline (The Dataflow)

### 3.1 Metrics Path (Pull Model across Mesh)
Prometheus scrapes metrics across the international border.
*   **Relabeling**: Maps local node IPs to **Tailscale IPs (100.64.x.x)** via `relabel_configs` to bypass cross-border NAT restrictions. Applies to `/metrics`, `/metrics/cadvisor`, and `/metrics/probes` endpoints.
*   **Retention**: 7 days / 10Gi (Local Buffer) to minimize local disk IOPS contention.

### 3.2 Logs Path (Offloading to S3)
To ensure durability against Home Lab volatility, logs are treated as transient on-node and persistent in the cloud.
*   **Mechanism**: Collectors forward logs to **Loki on `ct-serv-jp`**, which offloads raw chunks to **AWS S3 (ap-northeast-1)**. Because both Loki and S3 are independent of `acer-agent`, logs remain fully queryable even when the Home Lab is offline — this directly closes the Volatility problem stated in Section 1.
*   **Backfill Protection**: Alloy drops log entries older than 7 days before forwarding, preventing ingest storms after `acer-agent` restarts.

### 3.3 Alerts Path (Alertmanager → Slack)
Alertmanager routes firing alerts to Slack (`#k3han-error-notification`) and applies targeted silencing to suppress K3s structural noise.
*   **K3s Silence Rules**: `KubeProxyDown`, `KubeSchedulerDown`, and `KubeControllerManagerDown` are permanently silenced. K3s merges these components into a single binary and never exposes their individual metrics endpoints — these alerts will always fire and are never actionable.
*   **Scope**: `TargetDown` in `kube-system` / `monitoring` namespaces is also silenced for the same reason. All other namespaces remain alerted.

---

## 4. Key Architectural Decisions (ADR)

### ADR-001: Minimal Monitoring on Gateway Nodes
*   **Decision**: Strictly use Fluent-bit on `chorde.io/tier: low` nodes.
*   **Rationale**: Protecting the Ingress path is the highest priority. Alloy's resource footprint is too high for this specific tier.

### ADR-002: S3-Backed Log Persistence
*   **Decision**: Abandon local PVs for logs in favor of Cloud Object Storage.
*   **Rationale**: Decouples log availability from Home Lab uptime and prevents "Disk Full" scenarios from crashing edge nodes.

### ADR-003: Slack Alert Silence Policy
*   **Decision**: Mute K3s internal service alerts (`KubeProxy*`, `TargetDown` in control namespaces).
*   **Rationale**: Reduces alert noise caused by K3s's unique binary structure, focusing on actual application failures.

### ADR-004: Alloy Drop-Old Gate
*   **Decision**: Drop log entries older than 7 days in Alloy's processing pipeline before forwarding to Loki.
*   **Rationale**: `acer-agent` may go offline for extended periods (power/ISP). On restart, without this gate, Alloy would replay all buffered logs and overwhelm Loki ingest.

---

## 5. Security & Access Control
*   **Zero-Trust**: Grafana is restricted to the Tailscale mesh via `ingressClassName: nginx-private`.
*   **Safe Credentials**: S3 keys and Slack webhook are managed exclusively via `SealedSecrets`.

---

> **Settler Note**: When adding new nodes, ensure they are labeled with `chorde.io/tier: high` or `medium` for Alloy, or `low` for Fluent-bit, to automatically trigger the appropriate tiered agent deployment.
