---
title: 'Toolkit: SafeZone CLI (szcli)'
doc_id: safechord.safezone.toolkit.cli
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: SafeZone CLI (szcli) is the system's control plane. It adopts a Client-Relay architecture to enable secure, high-privilege operations (Database, Dataflow, Time) from outside the cluster while maintaining strict RBAC and distributed traceability.
keywords:
  - szcli
  - Client-Relay
  - Typer
  - Smoke Test
  - Trace ID Genesis
  - OAuth Relay
logical_path: SafeChord.SafeZone.Toolkit.CLI
related_docs:
  - safechord.safezone.toolkit.cli.reference.md
  - safechord.security.md
parent_doc: safechord.safezone.toolkit
archetype: blueprint
code_paths:
  - SafeZone/toolkit/cli
tech_stack:
  - Python 3.13
  - Typer (Client Framework)
  - FastAPI (Relay Server)
  - Google OAuth 2.0
  - Rich (Terminal UI)
doc_version: 0.3.5
app_version: 0.3.2
---

# SafeZone CLI (Toolkit Blueprint)

The SafeZone CLI (`szcli`) is the primary interface for system orchestration. It is designed to bridge the gap between external developer environments and internal cluster resources through a secure proxy pattern.

## 1. Responsibility & Positioning
*   **System Control Plane**: The unified entry point for administrative tasks, including database seeding, simulation triggering, and system state verification.
*   **Security Gateway (Relay Pattern)**: Shields internal infrastructure (PostgreSQL, Redis) by relaying commands through a trusted internal API, eliminating the need for direct port-forwarding or public DB access.
*   **Validation Engine**: Hosts the **Container-Native Smoke Test Engine**, which automates end-to-end dataflow verification using CSV-driven test cases.

## 2. Architecture: Client-Relay Pattern

Unlike standard microservices, `szcli` is divided into three functional layers:

### 2.1 The Client (`command/`)
*   **Tech**: Typer + Rich.
*   **Role**: Handles user input, command-line arguments, and terminal rendering.
*   **Auth**: Manages **Headless Google OAuth**. It automatically handles Token Refresh logic to obtain valid ID Tokens for the Relay.
*   **Traceability**: Acts as the **Trace ID Genesis**. Every single `szcli` execution generates a new `uuid4` as the `trace_id`, which is injected into all logs and forwarded to the Relay via `X-Trace-ID` headers.

### 2.2 The Relay (`relay/`)
*   **Tech**: FastAPI.
*   **Role**: A trusted proxy running inside the Kubernetes cluster.
*   **Security**: Verifies the Client's Google ID Token and enforces a whitelist-based RBAC.
*   **Execution**: Translates authorized HTTP requests into direct operations on internal databases and services.

### 2.3 The Smoke Test Engine (`ops/`)
*   **Logic**: Replaces complex Bash/JQ scripts with a Python-based execution engine.
*   **Mechanism**: Performs sequential assertions with smart polling to handle eventual consistency. For the detailed list of test case paradigms, refer to the [CLI Command Reference](safechord.safezone.toolkit.cli.reference.md).

## 3. Technical Requirements & Observability

### 3.1 Distributed Traceability
*   **Genesis Requirement**: The CLI must initiate the tracing chain. The `trace_id` is set in the global context at the start of every command.
*   **Propagation**: All requests to the Relay must include the `X-Trace-ID` header.

### 3.2 Command Paradigm
For the comprehensive list of commands, flags, and intent-driven instruction sets, please refer to the **[CLI Command Reference (Instruction Set)](safechord.safezone.toolkit.cli.reference.md)**. This manual serves as the primary authority for both human operators and AI agents.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Google Identity** | Auth | Used for identity verification at the Relay. |
| **Cluster Resources** | Sink | The Relay requires direct access to PostgreSQL and Redis. |
| **Time Server** | Downstream | The CLI acts as the primary controller for virtual time settings. |

---
> **Agent Directive**: This component utilizes a non-standard directory structure. When modifying CLI commands or Relay logic, ensure that cross-component dependencies (e.g., shared Pydantic models in `utils/`) are respected.
