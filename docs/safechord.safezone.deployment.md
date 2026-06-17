---
title: 'Map: SafeZone Deployment & Operations'
doc_id: safechord.safezone.deployment
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-06'
summary: Navigation map and architectural decision records for SafeZone's deployment layer. Covers the tiered Helm chart structure, the DAG-based deployment phase ordering, and how physical cluster constraints (cross-border latency, service dependencies) drive the design of SafeZone-Deploy.
keywords:
  - Deployment
  - Operations
  - Helm
  - GitOps
  - Umbrella Chart
  - KEDA
logical_path: SafeChord.SafeZone.Deployment
related_docs:
  - safechord.safezone.delivery.workflow.md
  - safechord.environment.md
  - safechord.safezone.md
  - safechord.chorde.k3han.cluster.md
parent_doc: safechord.safezone
archetype: map
code_paths:
  - SafeZone-Deploy/helm-charts
  - SafeZone-Deploy/deploy
  - SafeZone-Deploy/.github/workflows
doc_version: 0.3.1
---

# SafeZone Deployment

> "Code is liability, Deployment is delivery."

This document maps the **architectural intent** behind SafeZone's deployment layer. Implementation details live directly in `SafeZone-Deploy/`.

---

## Boundary: App Layer vs. Deployment Layer

*   **App Layer (`SafeZone`)**: Produces immutable Docker images.
*   **Deployment Layer (`SafeZone-Deploy`)**: Declares how those images run across environments — replicas, env vars, resources, secrets. Fully GitOps-driven via ArgoCD.
*   **`app/` vs `infra/` split**: Within each environment, `app/` contains the SafeZone service manifests; `infra/` contains environment-specific infrastructure bootstrap (namespace, RBAC, secrets, and workloads). The key difference between environments lives here — Preview provisions its own ephemeral DB and Valkey, while Staging delegates those to the Chorde PaaS and only bootstraps Kafka topics and secrets. See [Environment Landscape](safechord.environment.md) for the full tier strategy.

---

## Navigation

| Topic | Document | Focus |
| :--- | :--- | :--- |
| **GitOps Workflow** | [Unified Delivery Workflow](safechord.safezone.delivery.workflow.md) | Branch promotion, GitHub Actions orchestration, rollback strategy |
| **Environment Strategy** | [Environment Landscape](safechord.environment.md) | Local / Preview / Staging tiers, service discovery, Chorde PaaS integration |
| **Cluster Constraints** | [K3han Cluster Topology](safechord.chorde.k3han.cluster.md) | Node specs, cross-border latency measurements — the physical reality this layer must respect |

---

## Repo Structure

```
SafeZone-Deploy/
├── helm-charts/
│   ├── safezone-common/       # Shared Helm template library
│   ├── safezone-foundation/   # Phase 1: Infrastructure prerequisites
│   ├── safezone-seed/         # Phase 2, 4 & 6: Schema migration, data injection, recurring scheduler (same chart, different values)
│   ├── safezone-core/         # Phase 3: Business services
│   └── safezone-ui/           # Phase 5: Dashboard
├── deploy/
│   ├── preview/
│   │   ├── app/               # ArgoCD Application manifests for SafeZone services
│   │   └── infra/             # Preview-owned ephemeral infra (CNPG, Valkey, Kafka topic, SealedSecrets)
│   └── staging/
│       ├── app/               # ArgoCD Application manifests for SafeZone services
│       └── infra/             # Staging infra bootstrap (Kafka topic, SealedSecrets only — DB/Kafka delegate to Chorde PaaS)
├── scripts/
│   ├── ops/seal-secrets.sh    # Seals secrets via kubeseal
│   └── ops/gen-kubeconfig.sh  # Generates namespace-scoped low-privilege kubeconfig
└── .github/workflows/
    └── init-deploy.yml        # Manual deployment trigger (workflow_dispatch, self-hosted runner)
```

---

## Deployment Phases

Services have hard DAG dependencies. Deployment is orchestrated as sequential phases via GitHub Actions, with health checks gating each transition.

| Phase | Chart | Wait Condition | Why This Order |
| :--- | :--- | :--- | :--- |
| **1. Foundation** | `safezone-foundation` | `cli-relay` + `time-server` healthy | All services depend on connection strings and synchronized time state. `time-server` is the system-wide time SSOT — it controls the clock all services read from, and can simulate arbitrary dates for testing. |
| **2. Seed Schema** | `safezone-seed` (schema values) | Job completion | Core services will CrashLoop on missing DB schema. DDL migration must complete first. |
| **3. Core** | `safezone-core` | `analytics-api` + `ingestor` + `pandemic-simulator` healthy | The full write + read pipeline must be established before data can flow through it. `safezone-worker` is also part of this phase but is not health-gated — it is a pure Kafka-to-DB writer (no API interface, no health endpoint to probe against). |
| **4. Seed Cases** | `safezone-seed` (cases values) | Job completion | Historical case data is injected through the live ingestor pipeline; the pipeline must already be running. |
| **5. UI** | `safezone-ui` | `dashboard` healthy | User-facing layer starts only when the backend data pipeline is ready. |
| **6. Scheduler** *(staging only)* | `safezone-seed` (cronjob values) | — | Production-cadence data scheduling is not needed in preview environments. |

> **Operational note**: The `skip_seeding` flag on `init-deploy.yml` bypasses Phases 2 and 4. Use this for re-deploys where the schema and dataset are already in place.

---

## ADR: Tiered Umbrella Chart Strategy

SafeZone uses separate umbrella charts per phase rather than a single monolithic chart.

*   **Decision**: Four deployment units (`foundation`, `seed`, `core`, `ui`), each independently deployable and health-gated.
*   **Rationale**: A monolithic chart cannot express DAG ordering. Helm has no mechanism to wait for a Job to complete before starting a Deployment within the same release. Separating charts gives GitHub Actions a natural gate point between phases, and isolates failure domains — a seed failure does not roll back the foundation.

---

## ADR: `safezone-seed` Multi-Mode Deployment

The same `safezone-seed` chart is deployed twice in each pipeline run, with different values files.

*   **Phase 2 (schema)**: Runs a one-time DDL migration Job. Must complete before Core starts.
*   **Phase 4 (cases)**: Injects historical case data through the live ingestor pipeline. Must run after Core, because data flows through the running services.
*   **Phase 6 (cronjob, staging only)**: The same chart rendered as a CronJob for production-cadence scheduling. Preview environments skip this entirely.
*   **Rationale**: Merging both seed phases into one would require either running schema migration after core (unsafe) or blocking data injection until before core (impossible — the pipeline isn't running yet). The split is the only topologically valid ordering. Reusing the same chart for all three modes keeps the deployment surface minimal.
*   **Why one chart covers all three**: `safezone-seed` handles every data lifecycle task by wrapping [`szcli`](safechord.safezone.toolkit.cli.md) commands as K8s Jobs or CronJobs. Because `szcli` is the system's unified control plane for all operational actions (db init, simulation, scheduling), the chart needs no custom logic of its own — changing the values file changes which `szcli` command runs and in what workload type.

---

## ADR: KEDA as Cross-Border Write Buffer

The `safezone-worker` service uses KEDA to auto-scale based on Kafka consumer lag.

*   **Decision**: Worker replicas are driven by Kafka lag metrics, not CPU/memory.
*   **Rationale**: The Primary DB is on `ct-serv-jp` (Japan), ~80ms from the Taiwan worker nodes. Under burst ingestion, synchronous write throughput is physically bounded by this latency. Kafka absorbs the burst; KEDA scales workers to drain the queue at a rate the cross-border link can sustain. Without this buffer, high-frequency ingest events would saturate DB connections during spikes.
*   **Reference**: [K3han Cluster Topology](safechord.chorde.k3han.cluster.md) — cross-border latency constraints.
