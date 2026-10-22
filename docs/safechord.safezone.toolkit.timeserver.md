---
title: 'Toolkit: Time Server'
status: active
archetype: blueprint
code_paths:
  - SafeZone/toolkit/time-server
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

System time is not stored as a static value. Instead, the Time Server calculates it dynamically on every request to ensure continuous progression even between manual updates. It advances from the date an operator last set, at the set acceleration (1 by default).

### 2.1 Persistence & Midnight Sync
*   **Persistence**: Time settings survive Pod restarts.
*   **Midnight Alignment**: To prevent conflicts with daily maintenance tasks, the baseline offset is designed to align with physical midnight rollovers when appropriate, ensuring virtual dates transition naturally alongside physical days.

## 3. System Integration & Observability

### 3.1 SSOT for Time
All time-aware components in SafeZone must fetch the current date from this service:
*   **Simulator**: Uses `system_date` to determine which slice of historical CSV data to inject.
*   **Dashboard**: Uses `system_date` to set the default window for trend charts and maps.

### 3.2 Traceability
*   **Standard Compliance**: Follows the [service standards](safechord.safezone.service.standards.md): STD-R1 (traceability) and STD-R2 (health).
*   **Requirement**: Every request to `/now` or `/set` must handle and propagate `X-Trace-ID` to ensure that time-related state changes are traceable back to the originating CLI or UI command.

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Valkey** | Storage | State store for time offsets and acceleration factors. |
| **szcli** | Controller | The primary recommended tool for operators to adjust system time. |
| **API Consumers** | Sink | Includes the Dashboard and Pandemic Simulator. |

---
> **Agent Directive**: The Time Server is a critical dependency for data consistency. When refactoring the offset logic, ensure that the Valkey data structure remains backward-compatible to prevent system-wide temporal drift.
