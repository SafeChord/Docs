---
title: "Service: Dashboard v2"
doc_id: safechord.safezone.service.dashboard-v2
doc_version: 0.1.0
app_version: 0.3.5
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: "2026-05-26"
summary: "High-performance React SPA for pandemic simulation visualization, interactive risk mapping, and real-time state synchronization."
keywords:
  - Dashboard v2
  - React
  - SPA
  - MapLibre
  - Nginx Decoupling
logical_path: "SafeChord.SafeZone.Service.DashboardV2"
related_docs:
  - "safechord.safezone.md"
  - "safechord.safezone.service.analyticsapi.md"
  - "safechord.safezone.toolkit.timeserver.md"
parent_doc: "safechord.safezone.service"
archetype: blueprint
code_paths:
  - "SafeZone/services/dashboard-v2"
tech_stack:
  - React 19
  - TypeScript
  - MapLibre GL
  - Recharts
  - Nginx (Alpine)
---

# Dashboard v2 (Service Blueprint)

> Inherits from `archetype.blueprint.md`. Specialized for containerized
> microservices within `safechord.safezone.service.*`.

---

## 1. Responsibility

*   **Role**: Aggregator / Visualizer (SPA Client)
*   **Characteristics**: Stateless, Read-Heavy, Time-Aware
*   **Core objective**: We designed the dashboard to provide an interactive geospatial user interface for visualizing active pandemic simulation runs. It enables users to drill down into city-level and region-level metrics in real time.
*   **Architecture reference**: [Dashboard v1 Blueprint](safechord.safezone.service.dashboard.md) (Legacy Successor)

---

## 2. File Structure

```text
SafeZone/services/dashboard-v2/
├── src/
│   ├── components/               # UI presentation layer (Layout, Map, Scoreboard, Charts)
│   ├── services/                 # Infrastructure layer: External API clients (fetch logic)
│   ├── hooks/                    # Domain logic & state management (Time sync, case queries)
│   ├── config/                   # Dynamic parameters (base URLs, poll intervals)
│   └── types/                    # Domain data contracts and TS types
├── test/                         # TDD verification boundary (unit tests)
├── Dockerfile                    # Multi-stage image build settings (no runtime server)
└── package.json                  # Dependencies & execution scripts
```

---

## 3. Business Requirements

### Functional
*   **Multi-Tier Drill-down**: The interface must support seamless geographic drill-down states (National -> Selected City -> Selected Region/District) with hover highlights and interactive legends.
*   **Metric Representation**: The map and charts must support toggling between raw active cases and population-normalized ratios (e.g., active cases per 10,000 residents) to avoid geographic density bias.
*   **7-Day Scoreboard Lock**: The scoreboard displaying the Top 10 cities must be locked to a 7-day rolling aggregate window. This metric behaves independently, remaining unaffected by the global dashboard date interval filter.
*   **Centralized Time Tracking**: The UI must display the current system date and update all data components when the central virtual clock advances.

### Performance
*   **Zero Node.js Runtime**: Production containers must serve the pre-compiled static assets using Nginx, eliminating server-side rendering overhead.
*   **Hardware-Accelerated Rendering**: We leverage MapLibre GL to render vector maps on the client GPU, guaranteeing fluid interactions even with complex geospatial boundaries.

### Consistency
*   **Environment-Agnostic Artifacts**: We decouple the Nginx server configuration from the container image. The image remains stateless, allowing configuration injection (via volumes or Kubernetes ConfigMaps) at runtime.
*   **Cache Stale Fallback**: When external services suffer from latency, the UI must gracefully fallback to loading placeholders without blocking user input or throwing JS exceptions.

### Observability
*   **End-to-End Traceability**: Every outbound API request must inject a unique, client-generated Trace ID into the headers. This trace ID acts as the root origin for tracking frontend-driven data requests through the logs.
*   **Standard Health Probes**: The server must expose a static health probe endpoint returning HTTP 200.

---

## 4. Dependencies & Control

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Analytics API** | Upstream (Source) | Provides aggregated pandemic cases, regional ratios, and trend series. |
| **Time Server** | Upstream (Source) | Supplies the central virtual clock date to synchronize the UI timeline. |
| **User Browser** | Downstream (Sink) | Renders vector maps, SVG analytical charts, and manages polling states. |
| **Global Date Poller** | Control Plane (Trigger) | Periodically queries the Time Server to drive dashboard state updates. |

---

## 5. TDD Convergence Boundaries

We define the following verification boundaries to guarantee correctness at the client's integration interfaces. These constraints act as "red walls" enforced by the Vitest suite:

| Verification Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Request Traceability** | Outbound requests must inject a correctly formatted trace ID (matching `/^dash-\d+-[a-z0-9]+$/`) in the custom header. | `test/unit/apiClient` |
| **Query Parameter Assembly** | The case client must strip empty values and construct valid query strings containing correct intervals, cities, regions, and ratios. | `test/unit/caseService` |
| **Virtual Clock Parsing** | The clock service must validate the Time Server JSON response format, throwing explicit errors on missing date values. | `test/unit/timeService` |

---

## 6. Architecture Decision Records (ADR)

### [v0.1.0] [Nginx Decoupling]
*   **Decision**: We removed the `COPY nginx.conf` directive from the `Dockerfile`. The production container image compiles the TypeScript files and outputs static files to the public root. The configuration file `nginx.conf` must be injected externally.
*   **Why**: We adopted this approach to support both local development (using Docker Compose read-only volume mounts) and Kubernetes production (using K8s ConfigMap mounts) without rebuilding or maintaining separate Docker images for different environments.

### [v0.1.0] [TopCities 7-Day Window Isolation]
*   **Decision**: We extracted a dedicated React hook `useTopCities` that hardcodes the query parameter `interval="7"` for all city aggregation calls, completely bypassing the global interval state.
*   **Why**: This enforces the system requirement that the Top 10 scoreboard always represents the 7-day rolling aggregates, preventing confusion when users dynamically switch the main trend charts to other aggregates.
