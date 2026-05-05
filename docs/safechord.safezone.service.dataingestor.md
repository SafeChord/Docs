---
title: 'Service: Data Ingestor'
doc_id: safechord.safezone.service.dataingestor
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Data Ingestor serves as the primary ingress gateway for the SafeZone system. It provides a RESTful API to receive raw pandemic events, validating and wrapping them into standardized Kafka messages (CovidContract) to achieve asynchronous decoupling and load leveling.
keywords:
  - Data Ingestor
  - Kafka Producer
  - Gateway
  - Event Driven
  - FastAPI
  - Load Leveling
logical_path: SafeChord.SafeZone.Service.DataIngestor
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.pandemicsimulator.md
  - safechord.safezone.service.worker.md
  - safechord.safezone.service.python_scaffold.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/data-ingestor
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Kafka (aiokafka 0.12)
  - Pydantic v2
doc_version: 0.3.0
app_version: 0.3.1
---

# Data Ingestor (Service Blueprint)

## 1. Responsibility & Positioning
*   **Role**: Gateway / Producer (Kafka)
*   **Characteristics**: Stateless, High-Throughput, Event-Driven, Write-Only
*   **Core Objective**: Acts as the single entry point for all pandemic data ingestion. It validates raw events and offloads them to Kafka buffers for downstream consumption.
*   **Architecture Reference**: [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. Structural Design
*   **Directory Layout**: Adheres to the standardized structure defined in the [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md).
*   **Tech Stack**: Python 3.13, FastAPI 0.115, Kafka (aiokafka 0.12).

## 3. Business Requirements

The service's core intent is to provide a highly available, low-latency window for data ingestion, transforming uncontrolled external traffic into a manageable internal stream.

### 3.1 Data Reception & Validation (Functional)
*   **Single Point of Entry**: Provides a standard HTTP interface to receive pandemic events matching the `CovidDataModel`.
*   **Structural Validation**: Uses Pydantic for strict type checking.
*   **Contract Wrapping**: Wraps raw payloads into a `CovidContract` containing metadata like `trace_id`, `event_time`, and `version`.

### 3.2 Performance & Reliability
*   **Asynchronous Decoupling**: Implements an asynchronous producer to ensure HTTP requests return immediately.
*   **Load Leveling**: Uses Kafka as an intermediary to shield the database and compute clusters from sudden traffic bursts.

### 3.3 Consistency & Ordering
*   **Regional Ordering Guarantee**: Ensures events from the same "City-Region" maintain strict chronological order via partitioning keys.

### 3.4 Observability
*   **Technical Standards**: Adheres to the Universal Service Standards (Traceability & Health Checks) defined in the [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md).

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Upstream** | Source | Pandemic Simulator or CLI tools producing raw data. |
| **Kafka Cluster** | Downstream (Sink) | Message broker for event buffering (topic name defined in codebase). |
| **Control Plane** | N/A | Passive gateway triggered by external requests. |

## 5. TDD Convergence Boundaries

Any modifications to this service must satisfy these "Physical Red Walls" enforced via automated tests:

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Contract Wrapping** | Ensure `CovidContract` contains all required metadata and the payload remains unmodified. | `test/unit/` |
| **Partitioning Strategy** | Verify that data from the same `city-region` always maps to the same partition key. | `test/unit/` |
| **Ingress Strictness** | Validate that well-formed data passes while malformed requests (422) are blocked with standard error messages. | `test/integration/` |
| **Circuit Breaking (Kafka)** | Throw specific Domain Exceptions when the Kafka cluster is unavailable, rather than crashing the process. | `test/integration/` |
| **Lifespan Integrity** | Ensure the Kafka Producer is initialized correctly at startup and gracefully shut down to prevent message loss. | `test/integration/` |

## 6. Architecture Decision Records (ADR)

*   **[v0.3.1] Python Microservice Scaffold Integration**
    *   **Decision**: Refactored the flat directory structure into the `api/core/services/exceptions` layered pattern.
    *   **Why**: Standardizes development across all SafeZone services to reduce cognitive load for both AI and human engineers.

*   **[v0.2.1] Asynchronous Production (aiokafka)**
    *   **Decision**: Integrated `aiokafka` into the FastAPI event loop.
    *   **Why**: Resolved HTTP thread blocking issues caused by synchronous Kafka writes, significantly increasing gateway throughput.

*   **[v0.2.0] Natural Key Partitioning**
    *   **Decision**: Switched to using `city-region` as the Kafka Partition Key.
    *   **Why (Trade-off)**: While it might lead to partition skew, it guarantees strict chronological order for regional data, which is a prerequisite for accurate backend statistics.

*   **[v0.2.0] Evolution: From Sync DB to Event-Driven Ingestion**
    *   **Decision**: Removed direct PostgreSQL write logic in favor of a Kafka Producer.
    *   **Why (Load Leveling)**: The previous synchronous model coupled Ingestor throughput to DB IOPS. Decoupling via Kafka provides a buffer for traffic bursts and allows the database to be taken offline for maintenance without stopping data ingestion.

## 7. External Links
*   **Refactor Tracker**: [Issue #22: Refactor Data Ingestor to Golang](https://github.com/SafeChord/SafeZone/issues/22) (Planned)
