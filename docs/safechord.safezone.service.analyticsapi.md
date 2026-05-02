---
title: 'Service: Analytics API'
doc_id: safechord.safezone.service.analyticsapi
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Analytics API is the high-performance query engine of SafeZone. It provides a RESTful interface for aggregating raw pandemic events into multi-tier geographic views, utilizing multi-layer caching (Redis & In-memory) to achieve sub-millisecond latency under high concurrency.
keywords:
  - Analytics API
  - FastAPI
  - Redis Cache
  - Global Invalidation
  - Cache Versioning
  - Scaffold Blueprint
logical_path: SafeChord.SafeZone.Service.AnalyticsAPI
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dashboard.md
  - safechord.safezone.service.worker.md
  - safechord.safezone.service.python_scaffold.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/analytics-api
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Redis (redis-py async)
  - SQLAlchemy 2.0 (Sync)
  - psycopg2-binary
doc_version: 0.3.1
app_version: 0.3.1
---

# Analytics API (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `analytics-api` microservice.
> *Inherits from `archetype.blueprint.microservice.md`*

## 1. Responsibility & Positioning
*   **Role**: Reader / Aggregator / Gateway
*   **Characteristics**: Stateless, High-Concurrency, Read-Heavy, Read-Only
*   **Core Objective**: Acts as the primary data egress for the system. It aggregates raw pandemic events from PostgreSQL based on user-requested geographic tiers (National/City/Region). By implementing a sophisticated multi-layer caching strategy, it ensures millisecond-level response times even during peak traffic loads.
*   **Architecture Reference**: [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. File Structure
```text
SafeZone/services/analytics-api/
├── app/
│   ├── main.py                   # App Factory, Middleware, Lifespan
│   ├── api/                      # Routing Layer: HTTP handling & Dependency Injection
│   ├── services/                 # Business Logic: Aggregation & Caching (Decoupled from Web Framework)
│   ├── core/                     # Configuration & Global State (Settings, Lifecycle, Context)
│   └── exceptions/               # Domain Exceptions & Global Exception Handlers
├── test/                         # TDD Convergence Boundaries (Unit, Integration, E2E)
├── Dockerfile                    # Production Image Builder
└── requirements.txt              # Production Dependencies
```
*(Note: Detailed Pydantic Models and specific test cases are implemented within the codebase; this document defines business boundaries only.)*

## 3. Business Requirements

The service's core intent is to transform complex relational data into intuitive aggregate views while maintaining high availability under peak load.

### 3.1 Core Query Capabilities (Functional)
Provides an HTTP interface for querying pandemic data across three geographic dimensions:
*   **National**: Total trends across the entire country for a specified interval.
*   **City**: Epidemic metrics for a specific city.
*   **Region**: Fine-grained data for specific administrative regions.
*   **Query Flexibility**: All queries must support filtering by time interval, reference date, and optional calculations (e.g., ratio metrics).
> *Implementation Reference: Query parameters are defined in `app/api/endpoints.py` within the codebase.*

### 3.2 Performance & Cache Protection
*   **Database Shielding**: Since aggregation queries are resource-intensive, a robust caching mechanism is mandatory. All identical read requests must be intercepted by Redis; direct penetration to the relational database is strictly prohibited during cache validity.

### 3.3 Consistency & Invalidation
*   **Global Cache Invalidation**: The service must remain aware of underlying data changes. When the Write Pipeline updates raw data and publishes a new "Cache Version," this service must invalidate stale data to ensure consumers do not receive outdated metrics.

### 3.4 Observability & Ops
*   **Cache Status Tracking**: Every API request must explicitly indicate its cache state (e.g., `X-Cache-Status: Hit/Miss`) in the HTTP headers for monitoring and analysis.
*   **Health Checks**: Must provide a health check endpoint for Kubernetes Liveness/Readiness probes.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **PostgreSQL** | Primary Source (Read-Only) | Source of raw pandemic events. |
| **Redis (Cache)** | Storage | Store high-frequency aggregation results. |
| **Redis (State)** | Controller | Monitors global `current_cache_version` to trigger invalidation. |
| **Dashboard** | Client | The primary consumer of this service. |

## 5. TDD Convergence Boundaries

Per KDD philosophy, service correctness is enforced by automated tests in the codebase. Any implementation or modification must satisfy these "Physical Red Walls":

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Aggregation Logic** | Ensure results across intervals and tiers perfectly match the DB truth. | `test/unit/` |
| **Domain Exceptions** | Ensure business failures throw specific Exception instances from `exceptions/` rather than raw system errors. | `test/unit/` |
| **Stampede Protection** | Implement Double-Check Locking during cache misses to prevent overwhelming the DB with concurrent identical requests. | `test/unit/` (Cache Service) |
| **Global Invalidation** | API must correctly identify stale cache and force recalculation upon `current_cache_version` changes. | `test/integration/` |
| **Contract Stability** | Ensure HTTP response schemas and `X-Cache-Status` headers remain stable. | `test/integration/` |
| **Error Translation** | Verify that global handlers correctly map Domain Exception instances to standard HTTP status codes and JSON messages. | `test/integration/` |

## 6. Architecture Decision Records (ADR)

*   **[v0.3.1] Layered Dependency Injection**
    *   **Decision**: Replaced `request.app.state` access with explicit DI in `api/dependencies.py`.
    *   **Why**: Sacrificed slight development speed for significant testability, allowing business logic in `services/` to remain framework-agnostic.
*   **[v0.3.1] Pure ASGI Middleware**
    *   **Decision**: Switched from `BaseHTTPMiddleware` to a pure ASGI interface for `TraceAndCacheMiddleware`.
    *   **Why**: Resolved isolation issues where `ContextVar` (e.g., for `X-Cache-Status`) failed to propagate across task groups, ensuring consistent observability.
*   **[v0.2.0] Cache Versioning & Stampede Protection**
    *   **Decision**: Implemented `asyncio.Lock` for Double-Check Locking within the `@redis_cache` decorator.
    *   **Why**: Prevents "Cache Stampede" where concurrent requests hit the DB simultaneously during a cache miss.
*   **[v0.2.0] Response Caching**
    *   **Decision**: Implemented Redis-based response caching for all aggregation endpoints.
    *   **Why**: Minimizes API latency and provides a defensive layer for the PostgreSQL backend in a read-heavy environment.
*   **[v0.1.0] In-Memory Static Data Preloading**
    *   **Decision**: Preload low-frequency data (City/Region mappings, population benchmarks) into memory during startup.
    *   **Why**: Reduced complex SQL JOINs to simple fact-table aggregations, significantly improving query performance.

## 7. External Links
*   **GitHub Issues**: [Relevant Issue Tracker Link]
