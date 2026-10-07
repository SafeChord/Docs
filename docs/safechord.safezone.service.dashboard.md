---
title: 'Service: Dashboard (v1)'
doc_id: safechord.safezone.service.dashboard
status: legacy
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The Legacy Dashboard (v1) is the original interactive user interface of SafeZone, built with Plotly Dash. Succeeded by Dashboard v2.
keywords:
  - Dashboard
  - Plotly Dash
  - Legacy
logical_path: SafeChord.SafeZone.Service.Dashboard
related_docs:
  - safechord.safezone.service.dashboard-v2.md
  - safechord.safezone.service.analyticsapi.md
  - safechord.safezone.toolkit.timeserver.md
  - safechord.safezone.decisions.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - SafeZone/services/dashboard
doc_version: 0.3.1
app_version: 0.3.1
---

# Legacy Dashboard v1 (Service Blueprint)

> [!WARNING]
> **LEGACY SERVICE**: This document outlines the original Python Plotly Dash implementation (v1). It has been succeeded by the new React SPA implementation (v2) for improved performance and modular design.
> - **New Service Blueprint**: [Dashboard v2](safechord.safezone.service.dashboard-v2.md)
> - **Format**: This blueprint keeps the pre-v0.3.8 layout. It was not migrated to the requirement format because the service is no longer developed.

## 1. Responsibility & Positioning
*   **Role**: Client / Visualizer
*   **Characteristics**: Stateless, Time-Aware, Component-Based, Read-Only
*   **Core Objective**: Acts as the system's primary visualization window. It transforms complex time-series data into intuitive heatmaps and trend lines. A key differentiator is its **"Time Awareness"**: the Dashboard does not rely on the browser's local time; instead, it renders the simulation state (past or future) based on the global clock provided by the `Time Server`.

## 2. File Structure
```text
SafeZone/services/dashboard/
├── app/
│   ├── main.py                   # Dash App Factory & Entry Point
│   ├── layout/                   # UI Skeleton: Global Layout Container
│   ├── components/               # UI Layer: Reusable components (Map, Trend Charts, Stat Cards)
│   ├── callbacks/                # Logic Layer: Event handlers for UI interactions and time sync
│   ├── services/                 # Infrastructure Layer: External API clients (Analytics API & Time Server)
│   └── config/                   # Configuration & Environment management
├── test/                         # Integration & Logic verification
├── Dockerfile                    # Production Image Builder
└── requirements.txt              # Production Dependencies
```
*(Note: UI interaction logic and component implementations are located in the codebase.)*

## 3. Business Requirements

The dashboard's core intent is to provide a user-friendly view of pandemic trends while maintaining strict synchronization with the backend simulation.

### 3.1 Visualization & Interaction (Functional)
*   **Interactive Risk Map**: Renders heatmaps based on geographic tiers (National/City/Region) with zoom and hover capabilities for detailed metrics.
*   **Pandemic Trend Analysis**: Displays time-series charts for infections, recoveries, and other key indicators.
*   **"Time Travel" Control**: The UI must display the current system date in real-time and ensure all charts re-render automatically when the system clock changes.

### 3.2 Resilience & Synchronization
*   **Clock Polling Strategy**: Must poll the `Time Server` at regular intervals to maintain synchronization with the rest of the pipeline.
*   **Degraded Mode (Fallback)**: If the `Time Server` is unreachable, the dashboard must fallback to the server's local date and indicate "Local Time Mode" in the UI.
*   **API Error Handling**: Displays user-friendly messages (e.g., "Data Loading" or "Data Unavailable") instead of crashing when the Analytics API returns errors or timeouts.

### 3.3 User Experience
*   **Asynchronous Loading**: Leverages Dash's async capabilities to ensure that map loading does not block other UI interactions.

### 3.4 Observability
*   **Traceability (Genesis)**: Every request sent to the Analytics API generates a new `uuid4` as a `trace_id` within the `api_caller` service. This ID is injected into the outgoing `X-Trace-ID` header and recorded in the structured logs, serving as a primary origin point for UI-driven dataflows.
*   **Health Checks**: Must provide standard Kubernetes probes:
    *   **Liveness**: `/healthz` (Process status)
    *   **Readiness**: `/readyz` (Traffic readiness, including dependency health)

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Analytics API** | Upstream | Primary data source. |
| **Time Server** | Upstream | Global clock source. |
| **User Browser** | Client | Renders Plotly.js charts and maintains WebSocket/HTTP connection. |

## 5. TDD Convergence Boundaries

The following constraints must be satisfied through automated testing:

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Request Accuracy** | Verify that `api_caller` sends the correct URL and headers based on UI selections. | `test/unit/` |
| **Time Synchronization** | Ensure internal state updates correctly when the Time Server returns a new date. | `test/unit/` |
| **Component Robustness** | Ensure critical components (e.g., Map) do not throw JS exceptions when passed empty or malformed data. | `test/unit/` |
| **API Integration** | Validate end-to-end connectivity and data parsing with the Analytics API. | `test/integration/` |

## 6. Architecture Decision Records (ADR)

Moved to the [SafeZone Decision Log](safechord.safezone.decisions.md#dashboard-v1-legacy) (ADR-008, ADR-011, ADR-012).

## 7. External Links
*   **Time Source**: [Time Server Toolkit](safechord.safezone.toolkit.timeserver.md)
*   **Data Source**: [Analytics API Blueprint](safechord.safezone.service.analyticsapi.md)
