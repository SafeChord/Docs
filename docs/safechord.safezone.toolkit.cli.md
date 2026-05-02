---
title: 'Toolkit: SafeZone CLI (szcli)'
doc_id: safechord.safezone.toolkit.cli
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: SafeZone CLI (szcli) is the project's orchestrator and control plane. It utilizes a Client-Relay architecture where a Typer-based CLI interacts with a trusted internal Cluster Relay to perform privileged operations, including Google OAuth verification and dataflow automation.
keywords:
  - SafeZone CLI
  - szcli
  - Client-Relay Pattern
  - Typer
  - FastAPI
  - Headless OAuth
  - Ops Automation
logical_path: SafeChord.SafeZone.Toolkit.CLI
related_docs:
  - safechord.safezone.toolkit.cli.reference.md
  - safechord.safezone.md
  - safechord.security.md
parent_doc: safechord.safezone.toolkit
archetype: blueprint
code_paths:
  - SafeZone/toolkit/cli
tech_stack:
  - Python 3.13
  - Typer (CLI Framework)
  - FastAPI (Relay Server)
  - Google OAuth 2.0 (Headless)
  - Rich (Terminal UI)
doc_version: 0.3.5
app_version: 0.3.2
---

# SafeZone CLI (Toolkit Blueprint)

> **Type**: Blueprint (Technical Specification)
> **Focus**: Orchestration, secure relay patterns, and ops automation.
> **Constraint**: Implementation details (CLI subcommands, OAuth flows) live in the codebase.

---

## 1. Responsibility & Positioning
*(Required)*
*   **Role**: Orchestrator / Gateway / Ops Tool
*   **Core Objective**:
    *   **Unified Ingress**: Acts as the single control point for the system, shielding developers from complex internal K8s connection strings.
    *   **Security Boundary**: Utilizes a Relay pattern to allow external users to perform controlled operations (e.g., database seeding) without exposing DB/Redis ports directly.
    *   **Automated Validation**: Integrates the **Smoke Test Engine** to verify end-to-end dataflows via CSV-driven scripts.
*   **Characteristics**: Client-Relay Architecture, Stateful Auth (Local Token Cache).

## 2. File Structure
*(Recommended — directory-level only)*
```text
SafeZone/toolkit/cli/
├── command/                      # [Client] Typer App (Runs on Host/Bastion)
│   ├── main.py                   # Registry of subcommands
│   └── bin/client.py             # Auth-aware HTTP Client
├── relay/                        # [Server] FastAPI App (Runs inside Cluster)
│   ├── api/endpoints.py          # Trusted operations & RBAC
│   └── bin/                      # Domain logic helpers
└── ops/                          # [Automation] CSV-driven test engine
    ├── smoke_test.py             # Engine core
    └── test_cases/               # Test definitions (*.csv)
```

## 3. Business Requirements
*(Required)*

### Functional
*   **Dataflow Control**: Must provide commands to trigger simulations and verify data persistence.
*   **System Maintenance**: Commands for database initialization, cache clearing, and virtual time adjustment.
*   **Security Relay**: The relay must verify Google ID Tokens and enforce RBAC based on a whitelist.

### Non-Functional
*   **Headless Operation**: Must support fully automated execution in CI/CD environments (GitHub Actions) using Refresh Tokens.
*   **Observability**: CLI output must be machine-readable (JSON) while remaining human-friendly (Rich Tables).

## 4. Dependencies & Control
*(Required)*

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Google Identity** | Auth Provider | The Relay uses Google Public Keys for token verification. |
| **Cluster Infras** | Sink | The Relay requires direct connectivity to PostgreSQL and Redis. |
| **Time Server** | Downstream | The CLI manages simulation time by calling the Time Server API. |

## 5. TDD Convergence Boundaries
*(Required)*

> ⚠️ **KDD Notice**: This component was historically developed as a rapid prototype without comprehensive TDD. To satisfy KDD 2.0 standards, any future refactoring or feature additions MUST establish the following automated verification boundaries.

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Command Parsing** | Ensure subcommand arguments and flags are parsed correctly using `typer.testing.CliRunner`. | `command/` (Future Backfill) |
| **Relay RBAC** | Verify that the Relay rejects unauthorized tokens with 403 Forbidden and accepts whitelisted emails. | `relay/` (Future Backfill) |
| **Smoke Engine Logic** | Validate that the CSV parser correctly translates test steps into API calls. | `ops/` (Future Backfill) |

## 6. Architecture Decision Records (ADR)
*(Optional — append as the component evolves)*

*   **[v0.3.0] Client-Relay Architecture**
    *   **Decision**: Decoupled the CLI into a thin Client and a trusted Cluster Relay.
    *   **Why**: Solves the security risk of exposing database credentials to developer laptops. The Relay acts as a "Trust Proxy" within the VPC.
*   **[v0.1.0] Prioritizing Speed over Coverage**
    *   **Decision**: Omitted initial unit tests for the CLI during the early MVP phase.
    *   **Why**: Functional requirements were highly volatile. **Correction**: Under KDD 2.0, this is now considered technical debt. Future work MUST backfill tests to provide the "Physical Red Wall" for AI agents.

## 7. External Links
*   **Command Reference**: [CLI Instruction Set (szcli)](safechord.safezone.toolkit.cli.reference.md)
