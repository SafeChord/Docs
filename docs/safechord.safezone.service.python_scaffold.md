---
title: 'Blueprint: Python Microservice Scaffold'
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

# Blueprint: Python Microservice Scaffold

This document defines the **standardized internal directory structure and layering conventions** for all Python microservices within SafeZone. It is a "Convention over Framework" standard designed to eliminate architectural entropy across microservices, ensuring consistent context for both AI agents and human engineers.

## 1. Scope & Boundaries

### In-Scope
*   Internal directory layout of a single Python microservice.
*   Responsibilities of each layer and Dependency Injection (DI) rules.

### Out-of-Scope
*   **Cross-service contracts**: Pydantic models, DB schemas, logging, tracing, and event schemas. These are defined in the `utils/` git submodule. Microservices **must never** redefine models already present in `utils/`.
*   **Deployment artifacts**: Dockerfiles, Helm charts, and CI pipelines are governed elsewhere.
*   **Presentation Layer**: Dashboard services (planned migration to React SPA) do not follow this backend-only scaffold.

---

## 2. Canonical Directory Layout

Any new or refactored Python microservice must strictly adhere to the following structure:

```text
app/
├── main.py                 # Application Assembly
├── api/
│   ├── endpoints.py        # HTTP Transport Layer
│   └── dependencies.py     # DI Providers
├── services/               # Business Logic Layer (Framework-Free)
│   └── *.py
├── core/
│   ├── settings.py         # Environment Configuration
│   └── lifecycle.py        # Resource Lifecycle Management
└── exceptions/
    ├── custom.py           # Domain Exceptions
    └── handlers.py         # Framework Exception Handlers

test/
├── conftest.py             # Standardized Fixtures
├── unit/
│   └── test_*.py           # Fast isolated logic tests
├── integration/
│   └── test_*.py           # API level TestClient tests
├── cases/
│   └── *.json              # Data-driven test parameters
└── data/
    └── *                   # Static test assets (e.g. CSV)
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

## 5. Legacy Migration Map

When upgrading legacy services (e.g., `data-ingestor` or `pandemic-simulator`) to the v0.3.x scaffold, follow this mapping:

| Legacy Path | Scaffold Path | Action |
| :--- | :--- | :--- |
| `pipeline/orchestrator.py` | `services/*.py` | Rename and refactor (remove Request dependency) |
| `pipeline/query_service.py` | `services/query_service.py` | Direct move |
| `config/settings.py` | `core/settings.py` | Direct move |
| `config/cache.py` | Split into `services/` & `api/` | Move connection logic to `dependencies.py`, calculation to `services/cache_service.py` |
| `test/tests/unit_test/` | `test/unit/` | Flatten directory |
| `test/tests/integration_test/`| `test/integration/` | Flatten directory |

---
> **Agent Directive**: When creating a new microservice or refactoring an existing one, you MUST load this document into your context as the sole standard for structural compliance.
