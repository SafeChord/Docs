---
title: 'Service: Pandemic Simulator'
doc_id: safechord.safezone.service.pandemicsimulator
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Pandemic Simulator is the source of the SafeZone dataflow, responsible for "activating" static pandemic data into dynamic time-series events. Built with an AsyncIO architecture, it supports multiple trigger modes including historical replay, system seeding, and pressure testing.
keywords:
  - Pandemic Simulator
  - Data Generation
  - AsyncIO
  - Control Plane
  - Event Sourcing
  - System Seeding
logical_path: SafeChord.SafeZone.Service.PandemicSimulator
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dataingestor.md
  - safechord.safezone.toolkit.cli.md
  - safechord.safezone.service.python_scaffold.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/pandemic-simulator
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - AsyncIO
  - httpx
  - Pandas
doc_version: 0.3.0
app_version: 0.3.1
---

# Pandemic Simulator (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `pandemic-simulator` microservice.
> *Inherits from `archetype.blueprint.microservice.md`*

## 1. Responsibility & Positioning
*   **Role**: Source / Generator
*   **Characteristics**: Passive-Triggered, Stateless, AsyncIO, Read-Only (CSV)
*   **Core Objective**: Transforms static CSV pandemic data into a live event stream. It solves the lack of a real live data source during development and testing phases and provides precisely controllable traffic simulation for stress testing the entire pipeline.
*   **Architecture Reference**: [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. File Structure
```text
SafeZone/services/pandemic-simulator/
├── app/
│   ├── main.py                   # App Factory & Routes Registration
│   ├── api/                      # Routing Layer: Receives simulation trigger requests
│   ├── services/                 # Business Logic: Orchestrator, Productor (Pandas), Sender (httpx)
│   ├── core/                     # Configuration & Global State
│   └── exceptions/               # Domain Exceptions & Global Exception Handlers
├── data/                         # Static data source directory (mounted CSV)
├── test/                         # TDD Convergence Boundaries (Unit, Integration, E2E)
├── Dockerfile                    # Production Image Builder
└── requirements.txt              # Production Dependencies
```
*(Note: Detailed data production logic and test cases are implemented within the codebase.)*

## 3. Business Requirements

The service's core intent is to provide a flexible "Time Machine" that allows the system to replay or preview pandemic dataflows from any time period.

### 3-1 Data Generation & Replay (Functional)
*   **Daily Replay**: Reads all geographic region data for a specific date from CSV and transforms them into events.
*   **Interval Replay**: Supports batch simulation across multiple dates, sent in strict chronological order.
*   **Data Activation**: Ensures generated events contain correct `event_time` and `payload`, adhering to the `CovidDataModel` spec.

### 3-2 Traffic Control (Performance)
*   **Concurrency Throttling**: Limits concurrent requests to prevent overwhelming the downstream Ingestor.
*   **High-Efficiency Transmission**: Leverages AsyncIO to send data points concurrently, minimizing I/O wait time.

### 3-3 Resilience
*   **Invalid Date Handling**: When requested dates do not exist in the CSV or are in the future, the service should return empty sets or clear error codes instead of crashing.
*   **Downstream Fault Isolation**: If the Ingestor returns an error, the Simulator should log the failure and continue with the rest of the batch to ensure simulation completion.

### 3-4 Observability
*   **Simulation Feedback**: Each simulation request should return the total count of successful and failed transmissions.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Control Plane** (CLI) | Trigger | The primary activator, triggered via the SafeZone CLI. |
| **Local File System** | Source (Input) | Depends on the mounted `covid_data.csv`. |
| **Data Ingestor** | Downstream (Sink) | The sole receiver for simulated data. |

## 5. TDD Convergence Boundaries

Any modifications to this service must satisfy these "Physical Red Walls":

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Extraction Accuracy** | Verify that the Productor precisely extracts data points for a given date with correct column mapping. | `test/unit/` |
| **Time Travel Validity** | Ensure "future" or "out-of-range" dates trigger the correct domain exceptions. | `test/unit/` |
| **Concurrency Throttling** | Verify that the sender does not exceed the configured Semaphore threshold during high-volume data bursts. | `test/unit/` |
| **HTTP Reliability** | Ensure the Sender handles Keep-Alive correctly and logs downstream 5xx errors without stopping the process. | `test/integration/` |
| **Endpoint Validation** | Verify that trigger parameters (e.g., end date before start date) return standard 400/422 codes. | `test/integration/` |

## 6. Architecture Decision Records (ADR)

*   **[v0.3.1] Python Microservice Scaffold Integration**
    *   **Decision**: Refactored the legacy `pipeline/` module into the `services/` and `api/` layers.
    *   **Why**: Standardizes the directory structure to align with the `analytics-api` development model.

*   **[v0.2.1] Concurrency Control (Semaphore Management)**
    *   **Decision**: Introduced `asyncio.Semaphore` in the `data_sender.py`.
    *   **Why (Trade-off)**: Prevents the Simulator from exhausting system file descriptors (FD) when sending thousands of data points, while providing "Back-pressure" protection for downstream services.

*   **[v0.2.0] API Trigger Pattern**
    *   **Decision**: Abandoned internal CronJobs in favor of REST API triggers from the Control Plane (CLI/TimeServer).
    *   **Why**: Increases controllability and supports manual replay for any time point, centralizing scheduling logic.

## 7. External Links
*   **Data Source**: `SafeZone/data/covid_data.csv`
*   **Trigger Tool**: [SafeZone CLI (szcli)](safechord.safezone.toolkit.cli.md)
