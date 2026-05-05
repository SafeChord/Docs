---
title: 'Service: Dashboard'
doc_id: safechord.safezone.service.dashboard
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: The Dashboard is the interactive user interface of SafeZone, built with Plotly Dash. It features "Time Awareness" to synchronize with the global system clock via the Time Server, visualizing aggregated pandemic data from the Analytics API through dynamic maps and trend charts.
keywords:
  - Dashboard
  - Plotly Dash
  - Data Visualization
  - Time Travel
  - Interactive Map
  - Time Awareness
logical_path: SafeChord.SafeZone.Service.Dashboard
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.analyticsapi.md
  - safechord.safezone.toolkit.timeserver.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/dashboard
tech_stack:
  - Python 3.13
  - Plotly Dash 2.18
  - Dash Bootstrap Components
  - Pandas
  - httpx
doc_version: 0.3.0
app_version: 0.3.1
---

# Dashboard (Service Blueprint)

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

*   **[v0.2.1] Plotly Dash Framework**
    *   **Decision**: Chose Dash over React/Vue.
    *   **Why (Trade-off)**: Empowers backend-centric engineers to maintain the full UI/Logic stack within Python, maximizing development efficiency for this administrative and visualization tool.
*   **[v0.2.1] Time-Aware Polling Architecture**
    *   **Decision**: Implemented client-side polling via `dcc.Interval` coupled with a backend `TimeManager`.
    *   **Why**: Solves the visualization drift problem in distributed simulation environments by decoupling the UI from physical time.
*   **[v0.2.0] Component-Based UI Management**
    *   **Decision**: Decoupled the layout into reusable components in `app/components/`.
    *   **Why**: Reduces the complexity of `main.py` and allows for isolated UI testing of specific widgets.

## 7. External Links
*   **Time Source**: [Time Server Toolkit](safechord.safezone.toolkit.timeserver.md)
*   **Data Source**: [Analytics API Blueprint](safechord.safezone.service.analyticsapi.md)
