---
title: SafeZone ChangeLog
doc_id: safechord.safezone.changelog
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: SafeZone Module
summary: Records the version evolution of the SafeZone application layer. This document is a critical reference for AI agents to track architectural changes, deprecated features, and newly introduced technologies.
keywords:
  - SafeZone
  - Changelog
  - Release Notes
  - v0.3.1
  - v0.3.2
  - Scaffold
  - KDD
logical_path: SafeChord.SafeZone.ChangeLog
related_docs:
  - safechord.knowledgetree.md
  - safechord.safezone.md
parent_doc: safechord.safezone
doc_version: 0.3.5
app_version: 0.3.2
---

# SafeZone ChangeLog

This document provides a semantic version navigation for the SafeZone application layer, synchronized with the repository's `CHANGELOG.md`.

---

## [0.3.2] - 2026-05-02

### 🚀 Critical Changes (Scaffold Propagation)
*   **Template Propagation**: The Python Microservice Scaffold (v0.3.1) has been successfully propagated to `data-ingestor` and `pandemic-simulator`.
*   **Directory Restructuring**:
    *   `data-ingestor`: Extracted `services/ingest_service.py` (zero FastAPI imports) and added `api/dependencies.py` for Kafka DI.
    *   `pandemic-simulator`: Merged `pipeline/` modules into the `services/` layer and structured test directories into `unit/` and `integration/`.
*   **Automation Improvements**:
    *   **Makefile Automation**: `make test-*` targets now automatically trigger `make build-*`, ensuring tests always run against the latest image.
    *   **Cleanup**: Removed legacy service READMEs in favor of the central KDD Knowledge Base in `Docs/`.

### 🧪 Quality & Testing
*   **Test Backfill**: Added comprehensive unit tests for `data-ingestor` using mocked Kafka producers, achieving 87% coverage.
*   **CI/CD Alignment**: Verified the full local-ci pipeline (build -> test -> smoke-test) with the new scaffold structure.

---

## [0.3.1] - 2026-04-22

### 🏗️ Architectural Milestone (Scaffold Design)
*   **Python Microservice Scaffold**: Established the canonical `api/core/services/exceptions` layered architecture within `analytics-api` as the project's blueprint.
*   **Pure ASGI Middleware**: Replaced `BaseHTTPMiddleware` with a pure ASGI implementation to fix `ContextVar` isolation issues, ensuring `X-Cache-Status` headers are correctly propagated.
*   **Layered Dependency Injection**: Decoupled the `redis_cache` decorator from FastAPI `Request` objects, moving to explicit DI providers in `api/dependencies.py`.
*   **Cache Stampede Protection**: Implemented Double-Check Locking within the cache service to prevent database overwhelming during concurrent cache misses.

---

## [0.3.0] - 2026-04-16

### 🛡️ System Hardening
*   **Worker Hardening (Golang)**: 
    *   **Memory Leak Fix**: Resolved a critical timer goroutine leak caused by improper `defer cancel()` placement in loops.
    *   **Go Idiomatic Refactor**: Replaced Java-style factories with package-level constructors (`NewWorker`) and interface-based DI.
*   **Container-Native Smoke Test**: 
    *   Migrated from shell-based testing to a Python-based CSV-driven engine (`smoke_test.py`).
    *   The test engine now runs within a dedicated `safezone-cli-ops` container for consistent CI/CD execution.
*   **szcli Enhancements**: Added global `--verbose` support for HTTP header inspection and non-interactive `--yes` flags for automation.

---

## [0.2.1] - 2025-09-12

### 🚀 Optimization
*   **Franz-Go Migration**: Switched Kafka client from `segmentio/kafka-go` to `twmb/franz-go` for KRaft support and better performance.
*   **Manual Offset Management**: Disabled auto-commits in the Go Worker to ensure "At-least-once" delivery semantics.
*   **Partitioning Logic**: Implemented "Natural Key" partitioning (city-region) to guarantee regional data ordering.

---

## [0.2.0] - 2025-09-01

### ✨ Major Features
*   **Observability Foundation**: Standardized Trace ID propagation and JSON logging across all services.
*   **Async Data Pipeline**: Fully decoupled the system using Kafka as the central event bus.
*   **Persistence Layer**: Introduced the Golang Worker for batch PostgreSQL upserts and Redis for API response caching.
*   **Time Server**: Centralized virtual clock for simulation control.

---

## [0.1.0] - 2025-05-16

### 📦 MVP
*   Initial synchronous dataflow verification: `simulator` -> `ingestor` -> `analytics-api`.
