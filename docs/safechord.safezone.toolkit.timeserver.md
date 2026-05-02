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

> **Type**: Blueprint (Technical Specification)
> **Focus**: Why it exists, what it must do, and how correctness is verified.
> **Constraint**: Implementation details (schemas, test cases) live in the codebase.

---

## 1. Responsibility & Positioning
*(Required)*
*   **Role**: Time Nexus / Source of Truth (Time)
*   **Core Objective**:
    *   **Time Decoupling**: Ensures system components (Dashboard, Simulator) rely on this service for the "current system date" rather than physical system clocks.
    *   **Time Travel**: Supports setting a "virtual today," facilitating historical data testing or future scenario forecasting.
    *   **Time Acceleration**: Supports accelerating the flow of system time (e.g., 1 physical second = 1 virtual hour) for stress testing.
*   **Characteristics**: Stateless calculation logic, Stateful persistence (Redis).

## 2. File Structure
*(Recommended — directory-level only)*
```text
SafeZone/toolkit/time-server/
├── app/
│   ├── main.py                   # Entry Point (FastAPI Factory)
│   ├── api/
│   │   └── endpoints.py          # REST Interface (/now, /set, /status)
│   └── config/
│       └── settings.py           # App Settings (Redis Config)
├── Dockerfile                    # Production Image Builder
└── requirements.txt              # Service Dependencies
```

## 3. Business Requirements
*(Required)*

### Functional Logic (The Time Algorithm)
The system time (`system_date`) is calculated dynamically via an offset algorithm rather than stored statically:

$$ SystemDate = MockDate + (CurrentTime - MockUpdateTime) \times Acceleration $$

> **⚠️ Implementation Status**:
> *   ✅ **Time Travel (Mock Date)**: Fully implemented. The system locks onto the configured date.
> *   ✅ **Midnight Sync**: Implemented. The baseline time automatically aligns with physical midnight, ensuring virtual date rollovers synchronize with physical days to prevent CronJob conflicts.
> *   🚧 **Acceleration**: The API interface and DB schemas have reserved fields, but the calculation logic is not fully implemented. The default multiplier remains `1`.

### Non-Functional
*   **State Persistence**: The configured time state must survive container restarts.

## 4. Dependencies & Control
*(Required)*

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Redis** | Storage | Persists the time configuration. Sim time progresses from the last offset even if the Pod restarts. |
| **szcli** | Controller | The primary recommended client for configuring simulation parameters. |
| **Dashboard** | Consumer | Relies on this service to determine chart starting points and the "Today" marker. |

## 5. TDD Convergence Boundaries
*(Required)*

> ⚠️ **KDD Notice**: As an internal toolkit, this component historically relied on manual verification. To comply with KDD 2.0 AI-collaboration standards, any future feature development MUST establish the following automated test boundaries.

| Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **Time Algorithm Accuracy** | Verify that setting a mock date and querying `/now` accurately reflects the offset calculations (including Midnight Sync behavior). | `test/integration/` (Future Backfill Required) |
| **State Persistence** | Ensure that `POST /set` correctly modifies the underlying Redis hash structure. | `test/integration/` (Future Backfill Required) |
| **Endpoint Contracts** | Validate that parameter parsing for `mock_date` and `acceleration` functions correctly and throws standard 422 errors for invalid formats. | `test/integration/` (Future Backfill Required) |

## 6. Architecture Decision Records (ADR)
*(Optional — append as the component evolves)*

*   **[v0.1.0] Rapid Prototyping without TDD**
    *   **Decision**: Deployed the initial Time Server without automated test coverage.
    *   **Why**: Prioritized development speed for internal tooling during the MVP phase. However, this creates a severe regression risk during AI-driven refactoring. Future modifications MUST backfill integration tests to establish a "Physical Red Wall."
