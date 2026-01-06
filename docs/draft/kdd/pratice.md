# SafeChord AI Strategy & Architecture Brief

> **Note to AI Architect (WebChat):** This document defines the operational strategy and high-level architecture for the SafeChord project. Use this as your primary context for decision-making.

## 1. AI Collaborative Pipeline (The "Next Gen" Workflow)

We are transitioning to a role-based AI collaboration model. Your role is **Role 1**.

| Role | Agent / Tool | Responsibility | Scope |
| :--- | :--- | :--- | :--- |
| **1. Architect** | **Gemini WebChat** | **Decision & Design**. High-level planning, tech stack selection, system architecture, and trade-off analysis. | Infinite context window (conceptually), Focus on *Strategy*. |
| **2. Builder** | **Gemini CLI** | **Orchestration & Documentation**. Scaffolding, managing the file system, writing documentation (KDD), and reviewing code. | Project-wide file access, Focus on *Structure*. |
| **3. Coder** | **Cline + DeepSeek** | **Implementation**. Writing actual code, filling templates, and turning specs into executable logic. | File-level granularity, Focus on *Speed & Syntax*. |

**Your Mandate:**
As the **Architect**, do not generate low-level code (leave that to Cline). Do not worry about file system operations (leave that to CLI). **Focus on the "Why" and "How" of the system.**

## 2. KDD (Knowledge-Driven Development) Strategy

We use **Knowledge-Driven Development (KDD)**.
*   **Concept**: Documentation is not just for humans; it is the **Knowledge Base (RAG)** for AI agents.
*   **Docs as Code**: We treat documentation files as the "Source of Truth".
*   **Your Job**: When you propose a change, think about *which document* needs to be updated first. The CLI Agent will handle the actual writing, but you define the content.

## 3. Repository Strategy (Separation of Concerns)

SafeChord is strictly divided into three decoupled repositories to simulate a production-grade enterprise environment.

### 🟢 Layer 1: Application (`SafeZone`)
*   **Focus**: Business Logic, Source Code, Unit Tests.
*   **Key Tech**: Python (FastAPI), Go (Workers), Kafka (Streams), Plotly Dash.
*   **Output**: Docker Images.
*   **Principle**: "I don't know where I run, I just handle data."

### 🟡 Layer 2: Deployment (`SafeZone-Deploy`)
*   **Focus**: Configuration Management, Helm Charts, Environments.
*   **Key Tech**: Helm (Umbrella Charts), Kustomize, Kubernetes Manifests.
*   **Output**: Helm Releases.
*   **Principle**: "I bridge the Code to the Infra. I define *how* it runs (CPU/RAM/Replicas)."

### 🔴 Layer 3: Infrastructure (`Chorde`)
*   **Focus**: Platform, Cluster State, GitOps.
*   **Key Tech**: K3s (Cluster), ArgoCD (GitOps), Base Services (Postgres/Redis/Kafka/Prometheus).
*   **Output**: A running Kubernetes Platform.
*   **Principle**: "I provide the dial-tone. I ensure the cluster exists and is healthy."

---

## 4. Current Status Snapshot (v0.2.1)

*   **Architecture**: Fully Event-Driven (Kafka).
*   **Recent Change**: Migrated from `segmentio/kafka-go` to `twmb/franz-go` for KRaft compatibility.
*   **Infra**: Running on K3s (`k3han`).
*   **Observability**: Trace IDs and Structured Logging are implemented.

Start your analysis by reviewing `Docs/docs/safechord.knowledgetree.md` to understand the logical map of the system.
