---
title: 'Map: SafeChord Ecosystem'
doc_id: safechord
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The top-level navigational map for the SafeChord project. Defines the system-wide architecture context, the MVA design philosophy, and the strategic evolution roadmap. This is the entry point for understanding the SafeChord ecosystem.
keywords:
  - SafeChord
  - Project Overview
  - MVA
  - Architecture Context
  - Hybrid Cloud
  - System Map
logical_path: SafeChord
related_docs:
  - safechord.knowledgetree.md
  - safechord.environment.md
  - safechord.safezone.md
  - safechord.chorde.md
parent_doc: null
archetype: map
tech_stack:
  - Kubernetes (K3s)
  - Python (FastAPI)
  - Golang (Franz-Go)
  - Kafka, PostgreSQL, Redis
  - ArgoCD, KEDA, Cloudflare
doc_version: 0.3.5
app_version: null
---

# 🎼 SafeChord Ecosystem

> **From event triggering and asynchronous processing to persistent storage and interactive visualization.**
>
> SafeChord is a production-grade "Cloud-Native Laboratory" designed to demonstrate end-to-end dataflow pipelines and modern SRE practices. Our goal is to prove that high availability and observability can be achieved through disciplined architectural design, even under tight resource constraints.

---

## 🏛️ System Context

SafeChord adheres to strict **Separation of Concerns (SoC)**, decoupling the ecosystem into three primary dimensions: Application, Delivery, and Platform.

```mermaid
graph TB
    %% Styles
    classDef person fill:#08427b,stroke:#052e56,color:#fff;
    classDef app fill:#1168bd,stroke:#0b4884,color:#fff;
    classDef deploy fill:#438dd5,stroke:#2e6295,color:#fff;
    classDef infra fill:#2c3e50,stroke:#000,color:#fff;

    %% Actors
    User(User):::person
    Ops(Operator):::person

    %% SafeChord Boundary
    subgraph SafeChord [SafeChord Ecosystem]
        direction TB

        subgraph SafeZone [🟦 SafeZone]
            direction LR
            Dashboard(Dashboard<br/>Interactive UI):::app
            Services(Microservices<br/>Python / Go):::app
            Kafka(Event Bus<br/>Kafka):::app
        end

        subgraph Deploy [🟨 SafeZone-Deploy]
            Helm(Helm Charts):::deploy
            GitOps(ArgoCD Config):::deploy
        end

        subgraph Chorde [🟥 Chorde]
            K3han(K3s Cluster):::infra
            Network(Tailscale Mesh):::infra
        end
    end

    %% Interactions
    User -->|"View Metrics"| Dashboard
    Ops -->|"Push Code"| SafeZone
    Ops -->|"Manage Config"| Deploy
    Ops -->|"Provision Cluster"| Chorde
    
    Deploy -->|"Orchestrates"| SafeZone
    Chorde -->|"Hosts"| SafeZone
```

---

## 🏗️ Architectural Tiers

| Tier | Positioning | Core Responsibility | Navigation |
| :--- | :--- | :--- | :--- |
| 🟦 **SafeZone** | **Application** | Business logic implementation, including simulators, ingestion gateways, and data workers. | [**App Map**](safechord.safezone.md) |
| 🟨 **SafeZone-Deploy** | **Delivery** | Packaging and lifecycle management. Governs Helm charts and GitOps promotion workflows. | [**Delivery Map**](safechord.safezone.deployment.md) |
| 🟥 **Chorde** | **Platform** | Infrastructure and networking. Manages the hybrid K3han cluster and Tailscale overlay mesh. | [**Platform Map**](safechord.chorde.md) |

---

## 🛠️ Technology Stack

| Domain | Core Technologies | Purpose |
| :--- | :--- | :--- |
| **Languages** | **Python (FastAPI)** | Business logic, Aggregation APIs, Simulators, Dash UI. |
| | **Golang** | High-throughput data workers, Franz-Go consumer. |
| **Data** | **Kafka** | Asynchronous event bus for system decoupling. |
| | **PostgreSQL** | Relational storage for pandemic facts. |
| | **Redis** | Caching and distributed state control. |
| **Platform** | **K3s** | Lightweight Kubernetes distribution for hybrid environments. |
| | **Tailscale** | Peer-to-peer SDN for multi-cloud node connectivity. |
| | **Cloudflare** | DNS management, Tunnels, and Zero Trust access control. |
| **Operations** | **ArgoCD** | Declarative GitOps for continuous delivery. |
| | **KEDA** | Event-driven autoscaling based on Kafka consumer lag. |

---

## 🎯 Design Philosophy

### 1. MVA (Minimum Viable Architecture)
In resource-constrained environments, we prioritize "Necessary Complexity" over "Over-Engineering." Every resource is precisely allocated to segments that deliver the highest architectural value.

### 2. Environment Evolution
The system is designed for environment-agnostic adaptability:
*   **🟢 Local**: Rapid iteration via Docker Compose.
*   **🟡 Preview**: Automated smoke testing within temporary K3s namespaces.
*   **🔴 Platform**: Live operation on the hybrid K3han cluster (Staging).

### 3. KDD (Knowledge-Driven Development)
We practice **"Documentation as Codebase."** All architectural decisions and workflows are recorded in this knowledge base, serving as the Single Source of Truth (SSOT) that drives AI and human collaboration.

---

## 🛣️ Strategic Evolution (Merged Roadmap)

> **"Reliability is not an accident; it is a feature. Optimization is not a guess; it is a measurement."**

SafeChord evolves through disciplined phases, moving from a stable foundation to measurable performance.

| Phase | Theme | Objective |
| :--- | :--- | :--- |
| **v0.3.x** | **Stabilization** | ✅ **Completed**. Unified microservice scaffolds and backfilled unit tests. |
| **v0.3.5** | **Modernization** | **Current**. Migrating to English-first documentation and React SPA frontend. |
| **v0.4.x** | **Stress Testing & Reliability** | Integrating load testing tools and defining Service Level Objectives (SLOs) to establish architectural baselines. |
| **v0.5.x** | **Scaling** | Surgically optimizing throughput bottlenecks based on collected metrics. |

*For granular task tracking, active sprints, and real-time status, please refer to our [**GitHub Issues Board**](https://github.com/SafeChord/SafeZone/issues).*

---

## 🚀 Getting Started

If this is your first time here, we recommend the following reading path:
1.  **System Overview** (This document)
2.  [**Environment Evolution**](safechord.environment.md)
3.  [**Knowledge Tree (Safechord Wiki Navigation)**](safechord.knowledgetree.md)
