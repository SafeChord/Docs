---
title: 'Map: SafeZone Deployment & Operations'
doc_id: safechord.safezone.deployment
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Navigation map and architectural decision records for SafeZone's deployment layer. Defines the tiered Helm Chart design philosophy, deployment stage ordering intent, and the responsibility boundary between App and Deploy layers.
keywords:
  - Deployment
  - Operations
  - Helm
  - GitOps
  - Umbrella Chart
  - KEDA
logical_path: SafeChord.SafeZone.Deployment
related_docs:
  - safechord.safezone.deployment.workflow.md
  - safechord.environment.md
  - safechord.safezone.md
parent_doc: safechord.safezone
archetype: map
code_paths:
  - SafeZone-Deploy/helm-charts
  - SafeZone-Deploy/deploy
doc_version: 0.3.0
---

# SafeZone Deployment

> "Code is liability, Deployment is delivery."

This document defines the **architectural intent** behind SafeZone's deployment
layer. For implementation details (chart structure, values, manifests), refer
directly to the `SafeZone-Deploy` repository.

---

## Navigation

| Topic | Document | Focus |
| :--- | :--- | :--- |
| **GitOps Workflow** | [Deployment Workflow](safechord.safezone.deployment.workflow.md) | Branch promotion, GitHub Actions orchestration, rollback strategy |
| **Environment Strategy** | [Environment Landscape](safechord.environment.md) | Local / Preview / Staging tiers, service discovery, Chorde PaaS integration |

> *Implementation reference: `SafeZone-Deploy/` repository — Helm charts, ArgoCD manifests, deploy scripts.*

---

## Boundary: App Layer vs. Deployment Layer

*   **App Layer (`SafeZone`)**: Produces immutable Docker images (artifacts).
*   **Deployment Layer (`SafeZone-Deploy`)**: Declares how those images run
    across environments (replicas, env vars, resources, secrets). Fully
    GitOps-driven — every commit triggers ArgoCD reconciliation.

---

## ADR: Tiered Umbrella Chart Strategy

SafeZone uses a **tiered Umbrella Chart** architecture instead of a single
monolithic Helm chart, primarily to enforce deployment ordering and isolate
failure domains.

### Why: DAG-Based Deployment Ordering

Services have strict directed acyclic graph (DAG) dependencies. The tiered
design forces ArgoCD to deploy in the correct sequence via Sync Waves:

| Stage | Layer | Intent |
| :--- | :--- | :--- |
| **1. Foundation** | Infrastructure (ConfigMap, Secret, Ingress, CLI Relay) | Ensure all connection strings and platform services are ready before any app starts. |
| **2. Bootstrap** | Seed-Init (Schema migration, time-server setup) | Prevent Core services from CrashLooping on missing DB schema or time state. |
| **3. Core** | Business services (write pipeline + read pipeline) | Establish the complete data processing pipeline. |
| **4. Data Warming** | Seed-Data (historical data injection via live pipeline) | Inject 30+ days of history so Dashboard has meaningful charts on first load. Must run **after** Core, since it depends on the live ingestion pipeline. |
| **5. Experience** | UI (Dashboard) | User-facing layer — only starts when backend data is ready. |

### Why: Data Lifecycle Orchestration

Separating seed tasks (init vs. data) enables fine-grained control:

*   **Cold-start protection**: Schema migration (`seed-init`) completes before
    any application pod starts.
*   **Live traffic simulation**: `seed-data` sends requests through the actual
    ingestion pipeline (Simulator → Ingestor → Kafka → Worker → DB), doubling
    as an end-to-end integration test.

### Why: KEDA as Rate Buffering Bridge

The Worker service integrates KEDA to auto-scale based on Kafka consumer lag.
This acts as a **rate buffering bridge** — absorbing the impedance mismatch
between Kafka's high-throughput ingestion and the remote Primary DB's write
capacity, preventing database overload during burst scenarios.
