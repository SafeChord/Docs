---
title: "Service: Dashboard v2"
doc_id: safechord.safezone.service.dashboard-v2
doc_version: 0.2.0
app_version: 0.3.7
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: Dashboard v2 is the browser interface of SafeZone. It shows case figures on a map and in charts for the simulation's current date, and follows that date as it advances.
keywords:
  - Dashboard v2
  - React
  - SPA
  - MapLibre
logical_path: "SafeChord.SafeZone.Service.DashboardV2"
related_docs:
  - safechord.safezone.service.standards.md
  - safechord.safezone.decisions.md
  - safechord.safezone.changelog.md
  - safechord.safezone.toolkit.timeserver.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - "SafeZone/services/dashboard-v2"
---

# Dashboard v2 (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](safechord.safezone.changelog.md)).

## 1. Responsibility

*   **Role**: Visualizer (browser client)
*   **Core Objective**: Shows a viewer where cases are and how they compare across cities and regions, for the date the simulation is currently at rather than the viewer's own clock.

## 2. Requirements

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](safechord.safezone.service.standards.md) and are not repeated here.

### DSH-R1: The page follows the system date
The dashboard SHALL show the system date supplied by the time server, and SHALL reload
every figure for the new date within one polling interval of that date changing.

#### Scenario: simulation advances
- GIVEN the dashboard showing figures for one system date
- WHEN the time server's system date advances
- THEN within one polling interval the dashboard shows the new date and its figures

### DSH-R2: A viewer can drill down from city to region
Selecting a city on the map SHALL show that city's regions, each with its own figure for
the selected window.

#### Scenario: select a city
- GIVEN the national map
- WHEN the viewer selects a city
- THEN the map shows that city's regions with a figure for each

### DSH-R3: A viewer chooses the window and the measure
The dashboard SHALL let the viewer choose the length of the window, and switch every map
and chart figure between case counts and cases per 10,000 residents.

#### Scenario: switch to ratio
- GIVEN figures shown as case counts
- WHEN the viewer switches to ratio
- THEN every map and chart figure shows cases per 10,000 residents

### DSH-R4: The city ranking always covers seven days
The city ranking SHALL cover the seven days ending on the system date, whatever window
the viewer has selected.

#### Scenario: viewer selects a 30-day window
- GIVEN the viewer selects a 30-day window
- WHEN the ranking is shown
- THEN it still ranks cities by the seven days ending on the system date

### DSH-R5: A failing dependency does not break the page
When the analytics API or the time server fails, the dashboard SHALL stay usable and
tell the viewer that data is unavailable.

#### Scenario: analytics API returns an error
- GIVEN the analytics API answers with an error
- WHEN the dashboard loads figures
- THEN the page still responds to the viewer
- AND it shows that data could not be loaded

### DSH-R6: Every request starts a trace
Each request the dashboard sends SHALL carry a newly created trace ID. This applies
STD-R1 to the point where a trace begins.

#### Scenario: two requests
- GIVEN two requests sent by the dashboard
- WHEN their trace IDs are compared
- THEN each carries a trace ID and the two differ

### DSH-R7: One image runs in every environment
The dashboard image SHALL contain no environment-specific routing. The same image SHALL
run unchanged in every environment, with routing supplied at deploy time.

#### Scenario: same image, two environments
- GIVEN one built image
- WHEN it is deployed locally and to the cluster with different routing supplied
- THEN it serves the dashboard in both without being rebuilt

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Analytics query API | Calls | No language-neutral contract yet. `SafeZone/utils/pydantic_model/` is authoritative and this service mirrors it by hand; no ticket yet. | None. |
| Time server API | Calls | Same as the analytics query API. | None. |
| Administrative boundaries | Reads | `SafeZone/utils/geo_data/boundaries/` | City and region names in the boundary files equal those the analytics API accepts. A check is tracked in SafeZone#55. |
