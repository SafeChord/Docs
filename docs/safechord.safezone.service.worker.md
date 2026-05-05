---
title: 'Service: Worker (Golang)'
doc_id: safechord.safezone.service.worker
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Worker is the data processing core of SafeZone, implemented with Golang 1.24 and Franz-Go. It efficiently consumes events from Kafka and persists them to PostgreSQL using batch inserts and idempotent upsert mechanisms.
keywords:
  - Worker
  - Kafka Consumer
  - Golang
  - Franz-Go
  - PostgreSQL
  - Batch Processing
  - Idempotency
logical_path: SafeChord.SafeZone.Service.Worker
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dataingestor.md
  - safechord.safezone.service.analyticsapi.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/worker-golang
tech_stack:
  - Golang 1.24
  - Franz-Go (Kafka)
  - pgx/v5 (PostgreSQL)
  - sqlx
doc_version: 0.3.1
app_version: 0.3.1
---

# Worker - Golang (Service Blueprint)

## 1. Responsibility & Positioning
*   **Role**: Consumer (Kafka) / Persister 
*   **Characteristics**: High-Throughput, Idempotent, In-Memory Buffered (Soft-Stateful)
*   **Core Objective**: Acts as a high-throughput data consumption engine, leveraging Golang's concurrency model to process peak Kafka traffic and persist unstructured events as structured relational data in PostgreSQL.

## 2. File Structure
```text
SafeZone/services/worker-golang/
├── app/
│   ├── main.go                     # Entry Point (Signal Handling & Lifecycle)
│   ├── service/                    # Core Business Logic: Worker Pool & Batch Strategy
│   ├── adapter/                    # Input Adapters: Kafka Consumer (Franz-Go)
│   ├── strategy/                   # Output Ports: PostgreSQL Batch Upsert
│   ├── schema/                     # Data Models & Business Validation Logic
│   ├── config/                     # Configuration Loader
│   └── pkg/                        # Shared Internal Packages: Logger, Redis Cache
├── go.mod                          # Dependency Definition
└── Dockerfile                      # Multi-stage Image Builder
```
*(Note: The Go service follows Hexagonal Architecture principles; implementation details are located in the codebase.)*

## 3. Business Requirements

The service's core intent is to ensure data integrity and high throughput when transitioning from an asynchronous message queue to persistent storage.

### 3.1 Efficient Processing (Functional)
*   **Batch Persistence**: Must not call the database for every single message. Implements size-based or time-based buffering to group messages into batches for SQL Upsert operations.
*   **Concurrent Consumption**: Supports multiple consumer goroutines to process Kafka partitions in parallel, utilizing a worker pool for compute and I/O parallelism.

### 3.2 Integrity & Idempotency (Consistency)
*   **Idempotent Upsert**: Must handle "at-least-once" consumption scenarios. Uses `(Date, City, Region)` as a unique key to perform `ON CONFLICT DO UPDATE` to maintain eventual consistency.
*   **Payload Validation**: Validates message content (e.g., geographic IDs, non-negative values) before DB insertion. Invalid messages are logged and discarded without affecting the rest of the batch.

### 3.3 Resource Governance (Efficiency)
*   **Graceful Shutdown**: Upon receiving a SIGTERM, the service must stop consuming and flush remaining buffered data to the database before exiting. This is critical as the internal buffer represents in-flight "Soft State."

### 3.4 Observability
*   **Technical Standards**: Inspired by the Universal Service Standards (Traceability) defined in the system's architecture. While not an HTTP service, the Worker ensures end-to-end visibility of pandemic events.
*   **Consumer Lag Monitoring**: Provides metrics reflecting the offset gap between current consumption and Kafka's high watermark.
*   **Traceability**: Must extract `trace_id` from the `CovidEvent` JSON payload. This `trace_id` is injected into the Go `context` and must be present in all structured logs (via `ContextLogger`) and database transaction metadata.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Kafka Cluster** | Upstream (Source) | Source of raw pandemic events. |
| **PostgreSQL** | Downstream (Sink) | Final destination for structured facts. |
| **Control Plane** | N/A | Daemon service managed by Kubernetes. |

## 5. TDD Convergence Boundaries

As a Go service using Ports & Adapters, correctness is verified through isolated logic tests:

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Batching Logic** | Verify that the buffer only flushes when size or time thresholds are met, and remains empty after flush. | `app/service/` (Unit) |
| **Idempotent Upsert** | Simulate duplicate primary key writes and verify that the DB state reflects the final input. | `app/strategy/` (Integration) |
| **Validation Resilience** | Ensure single-message validation failures do not crash the worker or block subsequent consumption. | `app/schema/` (Unit) |
| **Resource Leakage** | Ensure Contexts are cancelled properly in goroutine loops and connection pools are managed. | `app/pkg/` (Unit) |

## 6. Architecture Decision Records (ADR)

*   **[v0.3.0] Idiomatic Go Refactor**
    *   **Decision**: Replaced Java-style factories with package-level constructors and interface injection.
    *   **Why**: Simplifies the code hierarchy and adheres to Go conventions, making mocking adapters for unit tests significantly easier.
*   **[v0.3.0] Franz-Go Client Migration**
    *   **Decision**: Switched from `segmentio/kafka-go` to `twmb/franz-go`.
    *   **Why**: Superior performance and full KRaft protocol support, reducing CPU overhead during peak consumption.
*   **[v0.2.5] Batch-First Persistence**
    *   **Decision**: Set default batch size to 1000 records.
    *   **Why**: Individual SQL inserts are the primary bottleneck for DB performance. Shifting pressure from DB IOPS to memory allows the system to handle simulator bursts effectively.
*   **[v0.2.0] At-Most-Once Lean Strategy**
    *   **Decision**: Implemented an aggressive offset commit strategy coupled with DB Upserts.
    *   **Why (Trade-off)**: Prioritizes throughput over strict exactly-once guarantees. In non-financial scenarios like SafeZone, this trade-off simplifies state management while remaining recoverable via upstream replays.

## 7. External Links
*   **Database Schema**: `SafeChord-Deploy/helm-charts/safezone-foundation/templates/db/init.sql` (Reference)
*   **Upstream Contract**: [Data Ingestor Blueprint](safechord.safezone.service.dataingestor.md)
