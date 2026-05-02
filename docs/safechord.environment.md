---
title: Environment Landscape & Evolution
doc_id: safechord.environment
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Global
summary: Defines the environmental strategy for the SafeChord system. Explains how we make pragmatic architectural trade-offs between resource isolation and platform integration across different lifecycle stages (Local, Preview, Staging).
keywords:
  - Environment
  - Docker Compose
  - Kubernetes
  - GitOps
  - Service Discovery
  - PaaS
  - Valkey
  - Kafka
logical_path: SafeChord.Environment
related_docs:
  - safechord.chorde.k3han.md
  - safechord.safezone.deployment.md
parent_doc: safechord
doc_version: 0.3.5
archetype: map
app_version: null
---

# Environment Evolution

SafeChord operates on the **Chorde/K3han Hybrid-Cloud Kubernetes Platform**. Given the physical constraints of hybrid-cloud nodes (see [K3han Cluster](safechord.chorde.k3han.cluster.md)), we adopt a pragmatic **MVA (Minimum Viable Architecture)** strategy. Rather than maintaining a formal Production environment, we concentrate resources on **Staging**, establishing it as the highest standard for system stability.

This document defines three environment tiers and their interactions with the Chorde platform.

---

## 🌍 Environment Tier Overview

| Feature | 🟢 Level 1: Local (Dev) | 🟡 Level 2: Preview (CI) | 🔴 Level 3: Platform (Staging) |
| :--- | :--- | :--- | :--- |
| **Positioning** | **Developer Experience (DX)** | **Isolation & Validation** | **Stability & Delivery** |
| **Primary Goal** | Rapid iteration, hot-reloading, and debugging. | Independent PR sandboxing without data pollution. | **Soak Testing** and technical showcases. |
| **Infra Source** | **SafeZone** (Ad-hoc) | **SafeZone-Deploy** (Degraded infra) | **Chorde PaaS** (Shared SaaS) |
| **Config Source** | `SafeZone/docker-compose/` | `SafeZone-Deploy/deploy/preview/` | `Chorde/gitops/` |
| **Config Type** | Docker Compose | ArgoCD Application (Manifests) | ArgoCD ApplicationSet (Helm) |
| **Persistence** | Bind Mounts (Resettable) | **Ephemeral** (EmptyDir/Temporary) | **Persistent** (PVC / Cloud Volumes) |
| **Deployment** | `docker compose up` | GitHub Actions (Auto-trigger) | Platform Ops / ArgoCD Sync |

> **Note**: The first segment of the configuration path represents the repository name (e.g., `SafeZone`).

---

## 🟢 Level 1: Local Development (The Origin)
> *"The minimal functional set where everything begins."*

At the local level, our priority is **Developer Experience (DX)**. We deliberately shield developers from Kubernetes complexity, allowing them to focus on business logic.

### Profiles Strategy
We leverage Docker Compose `profiles` to manage dependencies:
*   **`infra`**: Starts local instances of PostgreSQL, Valkey (State & Cache), and Kafka. This is the standard dependency set for development.
*   **`core/ui`**: Core services usually run directly on the Host (IDE) and connect to the Docker infrastructure via `localhost` for the fastest debug loop.

```bash
# Start infrastructure while keeping core code on the host
docker compose --profile infra up -d
```

---

## 🟡 Level 2: Preview Sandbox (The Isolated Buffer)
> *"A temporary isolation zone built for testing."*

This is the **heart of CI/CD**. To prevent parallel PRs from interfering with each other or polluting Staging with test data, the Preview environment adopts a **"Self-Contained"** isolation strategy, supplemented by shared resource mechanisms where necessary.

### 1. Downgrade & Isolation Strategy
Preview environments are installed via GitHub Actions using manifests in the `infras` path, deploying a "lightweight" suite within an independent namespace:
*   **Ephemeral Infra**: Uses CNPG to deploy a single Primary cluster without read-write separation. Valkey is deployed with `emptyDir` for faster restarts.
*   **Shared Kafka Cluster**: Since Kafka is resource-intensive, Preview environments share a platform-level Kafka cluster but maintain logical isolation via the `preview.` topic prefix.
*   **Disposable Namespaces**: The entire environment is destroyed immediately after a PR is merged or closed.

### 2. Configuration Management
All Preview-specific configurations (e.g., disabling persistence, connecting to shared Kafka) are encapsulated within `SafeZone-Deploy/deploy/preview/infras`. This ensures core logic remains identical to production while significantly reducing operational costs.

---

## 🔴 Level 3: Platform Staging (The Reality Sink)
> *"The closest approximation of the real world."*

Staging is a long-running showcase environment. Here, SafeZone transitions from an independent entity to a **Tenant of the Chorde Platform**, validating system behavior within a real platform architecture.

### 1. Core Mission: Soak Testing
The strategic purpose of Staging is:
*   **Soak Testing**: Capturing issues that only surface after long-duration runs, such as memory leaks or connection pool exhaustion.
*   **Technical Showcase**: As a technical portfolio window, this environment requires high availability and enough historical data to feel authentic.

### 2. Chorde SaaS Integration
In Staging, SafeZone no longer manages its own foundational infra. Instead, it connects to platform-grade services managed by the **Chorde** operations team via `ExternalName` or connection strings:
*   **PostgreSQL**: Connects to a physically separated, monitored DB cluster with full backup policies.
*   **Kafka**: Plugs into the shared message bus managed by the Strimzi Operator.
*   **Valkey**: Utilizes platform-level state storage and app-managed caching.

---

## ⚙️ Configuration Alignment Principles

To ensure system stability during environment transitions, we follow the principle: **"Intent in Docs, Values in Code."** Concrete service discovery DNS addresses, connection strings, and topic names are treated as highly volatile implementation details and should be retrieved directly from the source code of the respective environment:

*   **Local (Compose)**: Consult `.yml` and `.env` files in `SafeZone/docker-compose/`.
*   **Preview (CI)**: Consult Kustomize patches and manifests in `SafeZone-Deploy/deploy/preview/`.
*   **Staging (Platform)**: Consult Helm values and ArgoCD configs in `Chorde/gitops/`.

### Service Discovery Mechanism
*   **Internal Communication**: Prioritize K8s internal Service Names (`<svc-name>`) for inter-service calls.
*   **Cross-Namespace Access**: Use Fully Qualified Domain Names (FQDN, e.g., `<svc>.<namespace>.svc.cluster.local`) when accessing shared Chorde platform services.
*   **Read-Write Separation**: In Staging, application layers must distinguish between Primary (RW) and Replica (RO) connections to fully utilize the database cluster's resources.

---
> ⚠️ **Postscript**: The configurations above reflect current architectural decisions. Specific implementation details (e.g., credentials, keys) may evolve; always refer to the actual codebase for the definitive state.
