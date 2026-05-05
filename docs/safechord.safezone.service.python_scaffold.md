---
title: 'Python Microservice Scaffold'
doc_id: safechord.safezone.service.python_scaffold
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: SafeZone App Repo
summary: Defines the standardized internal directory structure and layered architecture (Layered DI) for all Python microservices within SafeZone. This serves as the Single Source of Truth (SSOT) for all Python service development from v0.3.x onwards.
keywords:
  - Scaffold
  - Microservice
  - Dependency Injection
  - FastAPI
  - Architecture
logical_path: SafeChord.SafeZone.Service.PythonScaffold
related_docs:
  - safechord.safezone.md
parent_doc: safechord.safezone
archetype: blueprint
doc_version: 0.3.1
---

# Python Microservice Scaffold

This document defines the **standardized internal directory structure and layering conventions** for all Python microservices within SafeZone. It is a "Convention over Framework" standard designed to eliminate architectural entropy across microservices, ensuring consistent context for both AI agents and human engineers.

## 1. Scope & Boundaries

### In-Scope
*   Internal directory layout of a single Python microservice.
*   Responsibilities of each layer and Dependency Injection (DI) rules.
*   **Containerization Standards**: Standardized Dockerfile and Dockerfile.test patterns.
*   **Testing Strategy**: Integration of unit/integration tests within the container lifecycle.
*   **Universal Technical Contracts**: Traceability and Health Check protocols.

### Out-of-Scope
*   **Cross-service contracts**: Pydantic models, DB schemas, logging, tracing, and event schemas. These are defined in the `utils/` git submodule.
*   **Deployment artifacts**: Helm charts, and global CI pipelines are governed elsewhere.
---

## 2. Canonical Directory Layout

Any new or refactored Python microservice must strictly adhere to the following structure:

```text
app/                        # Source Code
├── main.py                 # Application Assembly
├── api/                    # Transport Layer (Endpoints & DI)
├── services/               # Business Logic Layer (Framework-Free)
├── core/                   # Settings & Lifecycle
└── exceptions/             # Domain Exceptions & Handlers

test/                       # Test Suite
├── conftest.py             # Standardized Fixtures
├── unit/                   # Isolated logic tests
├── integration/            # API level TestClient tests
├── cases/                  # Data-driven parameters
└── data/                   # Static test assets

Dockerfile                  # Multi-stage Production Image Builder
Dockerfile.test             # Test Image Overlay (Inherits from Production)
requirements.txt            # Production dependencies
requirements.test.txt       # Test-only dependencies
```

---

## 3. Layer Definitions & Strict Rules

### 3.1 `app/main.py` — Application Assembly
*   **Responsibility**: Initializes the FastAPI `app` instance, mounts routers, and registers middleware/lifespan.
*   **Rules**:
    *   Must be the sole entry point for `uvicorn`.
    *   **Prohibited**: Must not contain business logic or define route handlers directly.

### 3.2 `app/api/endpoints.py` — HTTP Transport Layer
*   **Responsibility**: Defines Route Handlers. Forwards HTTP requests to business logic.
*   **Rules**:
    *   Handlers should only: receive dependencies via `Depends()`, call `services/` functions, and return responses.
    *   **Prohibited**: Must not contain business logic (e.g., data transformations, loops, conditional branching).
    *   **Prohibited**: Direct access to `request.app.state` is forbidden; use `dependencies.py` instead.

### 3.3 `app/api/dependencies.py` — Dependency Injection Providers
*   **Responsibility**: Defines functions compatible with `Depends()` to extract resources from `app.state` with type hinting.
*   **Rules**:
    *   This is the **only file** besides `main.py` allowed to access `request.app.state`.
    *   Each provider must return a single resource (e.g., `Session`, `RedisClient`).

### 3.4 `app/services/` — Business Logic Layer 🚨 (Core Constraint)
*   **Responsibility**: Pure domain logic and business calculations.
*   **Absolute Rule**: **Files in this directory are strictly forbidden from importing modules from `fastapi` or `starlette`.**
*   **Design Philosophy**: All dependent resources (DB, Cache) must be passed in as arguments (DI via arguments). This layer must be unit-testable without FastAPI and serves as the interface foundation for potential future migrations to Go.

### 3.5 `app/core/` — Settings & Lifecycle
*   **`settings.py`**: Handles environment variable definitions using `pydantic-settings`. No connection logic.
*   **`lifecycle.py`**: Implements the FastAPI `lifespan`. Initializes shared resources (DB Engine, Redis, Kafka Producer), stores them in `app.state`, and ensures graceful shutdown.

---

## 4. Test Layer Specification

Testing is the primary defense against regression during refactoring.

*   **`test/conftest.py`**: Provides pytest fixtures corresponding to `dependencies.py`. Integration tests use the FastAPI `TestClient`, while unit tests provide mock resources.
*   **`test/unit/`**: Focused on the `services/` layer. **Prohibited** from importing FastAPI or using TestClient. Must maintain sub-second feedback speed.
*   **`test/integration/`**: Focused on `api/endpoints.py`. Uses `app.dependency_overrides` to swap underlying resources.
*   **`test/cases/`**: Usage of JSON files for data-driven parameterized testing is encouraged.

---

## 5. Dockerization & Testing Strategy: "Test Image Overlay"

To ensure environmental parity between development, testing, and production, SafeZone follows a strict image layering pattern:

### 5.1 Production Image (`Dockerfile`)
*   **Multi-Stage Build**: Utilizes a `builder` stage for dependencies and a `runner` stage for the minimal runtime environment.
*   **Resource Inclusion**: Explicitly copies required `utils/` submodules from the project root into the container's Python path.

### 5.2 Test Image (`Dockerfile.test`)
*   **Overlay Principle**: Must inherit `FROM` the production image of the same service (ensuring "Test what you fly").
*   **Content**: Adds `test/` directory, `requirements.test.txt`, and necessary test configurations.
*   **Benefit**: Guarantees that the code running in tests is identical to the production artifact, with only test-specific dependencies and suites added on top.

### 5.3 Automated Validation Workflow
*   **Make Integration**: Use `make test-<service-name>` to automate the cycle:
    1.  Build the Production Image (tag: `latest`).
    2.  Build the Test Image (tag: `latest_test`) using the production image as a base.
    3.  Run the test container to execute unit and integration tests.
*   **Smoke Test**: After all service-level tests pass, the CI pipeline triggers `make smoke-test` to perform End-to-End validation across the full Docker Compose stack.

---

## 6. Universal Service Standards (The Contract)

All services inheriting from this scaffold must implement the following technical standards to ensure system-wide interoperability and observability.

### 6.1 Distributed Traceability
*   **Requirement**: Every service must support cross-service request tracing.
*   **Inheritance**: Must inherit `X-Trace-ID` from incoming HTTP headers (for API services) or Kafka headers/payloads (for consumers).
*   **Generation**: If a trace ID is missing, the service must generate a new UUID.
*   **Propagation**: The `trace_id` must be injected into the application context (e.g., Python `contextvars` or Go `context`), included in all structured logs, and forwarded to all downstream dependencies.

### 6.2 Standard Health Checks (API Services)
*   **Liveness Probe (`/healthz`)**: Confirms the process is running and not in a deadlocked state.
*   **Readiness Probe (`/readyz`)**: Confirms the service is fully initialized and its critical dependencies (e.g., Database, Redis, Kafka) are reachable and healthy.
*   **Non-API Services**: Workers or CLI tools must implement equivalent health reporting (e.g., via log signals or file-based heartbeats) suitable for their execution environment.

---
> **Agent Directive**: When creating a new microservice or refactoring an existing one, you MUST load this document into your context as the sole standard for structural compliance.
