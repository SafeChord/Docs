---
title: 'Script: SafeZone CI/CD Workflow'
doc_id: safechord.safezone.workflow.ci
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: SafeZone App Repo
summary: Defines the CI/CD playbooks for the SafeZone application. Covers the GitFlow branching strategy, Container-Native smoke test gates, and the Docker artifacts build/release lifecycle.
keywords:
  - CI
  - GitHub Actions
  - Smoke Test
  - GitFlow
  - Build Pipeline
  - Container-Native
logical_path: SafeChord.SafeZone.Workflow.CI
related_docs:
  - safechord.safezone.deployment.workflow.md
  - safechord.environment.md
parent_doc: safechord.safezone
archetype: script
code_paths:
  - SafeZone/.github/workflows
doc_version: 0.3.5
app_version: 0.3.2
---

# SafeZone Development & CI Workflow

This document standardizes the code lifecycle of the `SafeZone` (Application) repository. Our objective is to ensure that every line of code reaching the `main` branch is fully tested, containerized, and deployable.

---

## 1. Git Branching Strategy

We follow a standard GitFlow model, adapted for automated CI/CD triggers:

| Branch Name | Role | Protection | Triggered Action |
| :--- | :--- | :--- | :--- |
| **`main`** | **Production Trunk** | 🔒 PR Only | Publishes official Releases |
| **`dev`** | **Development Trunk** | 🔒 PR Only | Triggers Smoke Test Suite |
| **`feature/*`** | Feature Development | Open | Local Testing |
| **`release/*`** | Release Preparation | Open | Feature Freeze / Bug Fixes |
| **`hotfix/*`** | Emergency Fixes | Open | Immediate Merge to Main/Dev |

> **Developer Rule**: All new features must branch off `dev` as `feature/xxx`. Once complete, open a Pull Request (PR) back to `dev` to trigger the CI gauntlet.

---

## 2. Continuous Integration (CI Pipeline)

CI acts as the quality gatekeeper. We use GitHub Actions (`smoke-test.yml`) to execute this phase.

### Core Steps (The Gauntlet)
1.  **Dynamic Versioning**: Extracts the Git SHA (first 7 chars) as a temporary version tag (e.g., `0.3.2-a1b2c3d`).
2.  **Artifact Building**:
    *   Executes `make build-all` and `make build-tool-cli`.
    *   Builds all microservices and the **Ops Testing Image** (`safezone-cli-ops`) within the GitHub Runner.
3.  **Smoke Testing (Container-Native)**:
    *   Executes `make smoke-test`.
    *   **Architecture**: The test engine (`smoke_test.py`) runs inside the `safezone-cli-ops` container, directly joining the Docker Compose internal network.
    *   **Stateful Test Flows**: Test cases are defined via CSV, supporting logical step dependencies (e.g., *Simulate Data* ➡️ *Verify Cache Hit*).
    *   **Async Event Verification**: To handle system asynchrony (Kafka lag, DB flushing), the engine features "Adaptive Polling & Retries" to verify eventual consistency rather than relying on static sleep timers.
    *   **Checkpoints**: Includes end-to-end data persistence, cache lifecycle checks, and automated database cleanup.

> **Note**: CI-stage images are **not** pushed to GHCR; they remain in the runner cache for testing purposes only.

---

## 3. Continuous Delivery (CD / Release)

When code is ready for production delivery, the Release workflow (`release.yml`) is triggered.

### Trigger Condition
*   A Git Tag pushed to the `main` branch matching the pattern `v*.*.*`.

### Execution Steps
1.  **Tag Validation**: Extracts the official version number (e.g., `0.3.2`) from the tag.
2.  **Official Build**: Rebuilds all services using the official version tag.
3.  **Image Publishing**:
    *   Executes `make push-all`.
    *   Pushes official images to the **GitHub Container Registry (GHCR)**. These artifacts are then referenced by the `SafeZone-Deploy` repository for deployment.

---

## 4. Local Development & Testing

Before submitting a PR, developers MUST verify logic locally. Following the v0.3.2 automation improvements, test commands are now self-healing:

*   **Unit & Integration Tests**: `make test-<service-name>` (e.g., `make test-data-ingestor`).
    *   **Auto-Build**: The command automatically triggers `make build-<service-name>`, ensuring tests run against the latest container image without manual pre-building.
    *   **Standardized Layout**: All Python services follow the Scaffold standard, with tests split into `test/unit/` (logic) and `test/integration/` (API).
*   **Global Validation**: `make test-all` (runs all service tests).
*   **Local Integration**: `make dev-up` (starts the full Docker Compose environment).
    *   Consult [Environment Evolution](safechord.environment.md) to learn how to use **Profiles** (`infra`/`core`) for faster local loops.
