---
title: SafeChord Knowledge Tree
doc_id: safechord.knowledgetree
last_updated: '2026-05-26'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Project Root
summary: The centralized navigational graph for the SafeChord project. Defines the 4-layer decoupled architecture and provides a semantic directory to all core documentation nodes.
keywords:
  - SafeChord
  - Knowledge Graph
  - Architecture Map
  - Navigation
logical_path: SafeChord.KnowledgeTree
related_docs:
  - index.md
doc_version: 0.3.5
archetype: map
app_version: null
---

# SafeChord Knowledge Map

## 🗺️ Navigation Guide

SafeChord utilizes a **Decoupled 4-Layer** architecture. Choose your reading path based on your role and objectives:

*   **⬜ Knowledge (Docs)**: The **Single Source of Truth (SSOT)**. Defines methodologies, standards, and global specifications.
*   **🟦 Application (SafeZone)**: Core business logic. Focuses on Python/Go source code, async dataflows, and TDD boundaries.
*   **🟨 Deployment (SafeZone-Deploy)**: Delivery and packaging. Focuses on Helm charts and GitOps promotion workflows.
*   **🟥 Infrastructure (Chorde)**: Platform layer. Manages the hybrid-cloud K3s cluster, network perimeters, and scheduling policies.

### 🏷️ Legend

| Icon | Meaning | Description |
| :--- | :--- | :--- |
| ⭐ | **Core Concept** | Essential reading for understanding critical architecture. |
| 📄 | **Document** | Standard technical specification or detailed design node. |
| 🛡️ | **Security** | Documents related to security architecture or secret management. |
| 🔄 | **Timeline** | Version evolution, changelogs, or migration context. |
| 🚧 | **WIP** | Work in progress or draft-stage documentation. |

---

## 🌳 Project Structure Tree

*   🧩 **SafeChord Ecosystem** - The Big Picture
    *   [📄 index.md](index.md) ⭐ (System Overview: MVA Philosophy, Tech Stack, and Strategic Evolution)
    *   [📄 knowledgetree.md](safechord.knowledgetree.md) (This document: Global Navigation)
    *   [📄 safechord.security.md](safechord.security.md) 🛡️ (Security Architecture & SecretOps Governance)
    *   🌐 **Environment Landscape** 
        *   [📄 safechord.environment.md](safechord.environment.md) ⭐ (Tiered Environments: From Local Compose to Platform Integration)

    *   ⬜ **Knowledge Layer (Repo: Docs)**
        *   *Focus: KDD Methodology, Standards, SSOT*
        *   [📄 safechord.kdd.introduction.md](safechord.kdd.introduction.md) (Introduction to KDD philosophy)
        *   [📄 safechord.kdd.practice.md](safechord.kdd.practice.md) ⭐ (Practice: The Three-Engine Model & Headless Protocol)

    *   🟦 **Application Layer (Repo: SafeZone)**
        *   *Focus: Source Code, Business Logic, AsyncIO Dataflow*
        *   **Core Architecture**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐ (App Map: Async Dataflow & Event-Driven Design)
            *   [📄 safechord.safezone.service.python_scaffold.md](safechord.safezone.service.python_scaffold.md) ⭐ (Blueprint: Standard Python Scaffold & Layering)
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md) (🔄 Application Version History & Tech Migrations)
        *   **Microservices**
            *   [📄 safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md) (Simulator: AsyncIO Data Source)
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md) (Ingestor: Kafka Producer Gateway)
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md) (Worker: Golang / Franz-Go Consumer)
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md) (API: Aggregator & Scaffold Blueprint)
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md) (UI: Time-Aware Visualization - Legacy)
            *   [📄 safechord.safezone.service.dashboard-v2.md](safechord.safezone.service.dashboard-v2.md) (UI: React SPA & Time Travel)
        *   **Toolkit & Workflow**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md) (Time Server: Virtual Clock Controller)
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md) (SZCLI: Operations Tooling & CLI Relay)
            *   [📄 safechord.safezone.workflow.md](safechord.safezone.workflow.md) ⭐ (Script: CI Workflow & Smoke Test Specifications)

    *   🟨 **Deployment Layer (Repo: SafeZone-Deploy)**
        *   *Focus: Configuration, Helm, GitOps CD*
        *   [📄 safechord.safezone.deployment.md](safechord.safezone.deployment.md) ⭐ (Deployment Architecture & Global ADRs)
            *   [📄 safechord.safezone.deployment.workflow.md](safechord.safezone.deployment.workflow.md) (Script: GitOps Workflow & Environment Promotion)

    *   🟥 **Infrastructure Layer (Repo: Chorde)**
        *   *Focus: Kubernetes, Platform Operators, Scheduling*
        *   [📄 safechord.chorde.md](safechord.chorde.md) (Chorde Overview: Platform Framework & Repo Structure)
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han: Hybrid-Cloud Cluster Navigation)
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) ⭐ (Physical Topology, Latency Matrix, & Tailscale SDN)
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md) (Ingress Perimeter: Dual-Channel Isolation)
            *   [📄 safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md) ⭐ (Scheduler: Reliability Tiers & Taints Policy)
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md) (Observability: Loki & Prometheus Operator)
            *   [📄 safechord.chorde.k3han.changelog.md](safechord.chorde.k3han.changelog.md) (🔄 Platform Version Evolution)
