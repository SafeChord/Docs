---
title: 'Toolkit: Time Server'
doc_id: safechord.safezone.toolkit.timeserver
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Time Server is the central "Time Nexus" of SafeZone. It maintains the system's singular "Virtual Date," providing Time Travel and Acceleration capabilities that untether the simulation pipeline from physical time constraints.
keywords:
  - Time Server
  - Mock Time
  - Time Travel
  - Redis
  - FastAPI
logical_path: SafeChord.SafeZone.Toolkit.TimeServer
related_docs:
  - safechord.safezone.toolkit.cli.md
  - safechord.safezone.service.dashboard.md
parent_doc: safechord.safezone.toolkit
archetype: blueprint
code_paths:
  - SafeZone/toolkit/time-server
tech_stack:
  - Python 3.13
  - FastAPI
  - Redis (State Store)
doc_version: 0.3.5
app_version: 0.3.0
---

# Time Server (Toolkit Blueprint)

The Time Server is the "Source of Truth" for temporal state within the SafeZone ecosystem. It decouples simulation events and visualization from physical wall-clock time.

## 1. Responsibility & Positioning
*   **Temporal Nexus**: Provides a single, unified system date (`system_date`) to all components, ensuring that a simulator in one container and a dashboard in another are always synchronized to the same virtual moment.
*   **Time Travel Agent**: Allows operators to "teleport" the entire system to a specific historical date (for replay) or a future date (for forecasting).
*   **Time Acceleration Engine**: Enables stress testing by accelerating the flow of time, allowing days of pandemic evolution to be simulated in minutes.

## 2. Core Logic: The Offset Algorithm

System time is not stored as a static value. Instead, the Time Server calculates it dynamically on every request to ensure continuous progression even between manual updates.

### 2.1 The Calculation Formula
The current system time is derived from the following relationship stored in Redis:

$$ SystemDate = MockDate + (CurrentTime - MockUpdateTime) \times Acceleration $$

*   **MockDate**: The user-defined starting point.
*   **MockUpdateTime**: The physical timestamp when the mock date was last set.
*   **Acceleration**: The multiplier for time progression (Default is 1).

### 2.2 Persistence & Midnight Sync
*   **State Store**: Uses Redis to ensure that time settings survive Pod restarts.
*   **Midnight Alignment**: To prevent conflicts with daily maintenance tasks, the baseline offset is designed to align with physical midnight rollovers when appropriate, ensuring virtual dates transition naturally alongside physical days.

## 3. System Integration & Observability

### 3.1 SSOT for Time
All time-aware components in SafeZone must fetch the current date from this service:
*   **Simulator**: Uses `system_date` to determine which slice of historical CSV data to inject.
*   **Dashboard**: Uses `system_date` to set the default window for trend charts and maps.

### 3.2 Traceability
*   **Standard Compliance**: Adheres to the Universal Service Standards (Traceability & Health Checks) defined in the Python Scaffold.
*   **Requirement**: Every request to `/now` or `/set` must handle and propagate `X-Trace-ID` to ensure that time-related state changes are traceable back to the originating CLI or UI command.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Redis** | Storage | State store for time offsets and acceleration factors. |
| **szcli** | Controller | The primary recommended tool for operators to adjust system time. |
| **API Consumers** | Sink | Includes the Dashboard and Pandemic Simulator. |

---
> **Agent Directive**: The Time Server is a critical dependency for data consistency. When refactoring the offset logic, ensure that the Redis data structure remains backward-compatible to prevent system-wide temporal drift.
