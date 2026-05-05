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

## 2. Structural Design
*   **Directory Layout**: Adheres to the standardized structure defined in the [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md).
*   **Tech Stack**: Python 3.13, Plotly Dash 2.18, Dash Bootstrap Components.

## 3. Business Requirements

The dashboard's core intent is to provide a user-friendly view of pandemic trends while maintaining strict synchronization with the backend simulation.

### 3.1 Visualization & Interaction (Functional)
*   **Interactive Risk Map**: Renders heatmaps based on geographic tiers (National/City/Region).
*   **Pandemic Trend Analysis**: Displays time-series charts for key indicators.
*   **"Time Travel" Control**: Ensures all charts re-render automatically when the system clock changes.

### 3.2 Resilience & Synchronization
*   **Clock Polling Strategy**: Polls the `Time Server` at regular intervals to maintain synchronization.
*   **Degraded Mode (Fallback)**: Fallback to local time if the Time Server is unreachable.

### 3.3 User Experience
*   **Asynchronous Loading**: Leverages Dash's async capabilities to prevent blocking UI interactions.

### 3.4 Observability
*   **Technical Standards**: Adheres to the Universal Service Standards (Traceability & Health Checks) defined in the [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md).

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
