---
title: 'Service: Pandemic Simulator'
doc_id: safechord.safezone.service.pandemicsimulator
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The Pandemic Simulator is the source of the SafeZone data flow. On a trigger it replays the case records of a date or a date range from a static data file and sends them to the Data Ingestor.
keywords:
  - Pandemic Simulator
  - Data Generation
  - AsyncIO
  - Control Plane
  - System Seeding
logical_path: SafeChord.SafeZone.Service.PandemicSimulator
related_docs:
  - safechord.safezone.service.standards.md
  - safechord.safezone.decisions.md
  - safechord.safezone.changelog.md
  - safechord.safezone.toolkit.cli.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - SafeZone/services/pandemic-simulator
doc_version: 0.4.0
app_version: 0.3.8
---

# Pandemic Simulator (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](safechord.safezone.changelog.md)).

## 1. Responsibility

*   **Role**: Source / Generator
*   **Core Objective**: Turns a static file of historical case records into a live flow of data. It stands in for a real data source during development and testing, and lets the rest of the pipeline be driven for any date on demand.

## 2. Requirements

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](safechord.safezone.service.standards.md) and are not repeated here.

### SIM-R1: A daily trigger replays one date
On a daily trigger the simulator SHALL send one record for each city and region that
has cases on the requested date, with the case counts of that date, city and region
summed.

#### Scenario: date with data
- GIVEN source data holding several rows for one city and region on a date
- WHEN that date is triggered
- THEN one record for that city and region is sent, with the rows' counts summed

### SIM-R2: An interval trigger replays every date in the range
On an interval trigger the simulator SHALL send the records of every date from the start
date to the end date, both included, each built as in SIM-R1.

#### Scenario: single-day range
- GIVEN a range whose start and end are the same date
- WHEN it is triggered
- THEN the records sent equal those of a daily trigger for that date

### SIM-R3: Sending is bounded
The simulator SHALL never have more than the configured number of requests in flight to
the ingest API at once.

#### Scenario: large replay
- GIVEN a trigger that produces more records than the configured limit
- WHEN the simulator sends them
- THEN the number of requests in flight never exceeds the limit

### SIM-R4: Only valid records are sent
The simulator SHALL send only records that satisfy the ingest request rules. When any
record of a trigger breaks them, it SHALL send none and report failure.

#### Scenario: one bad record in the batch
- GIVEN a trigger whose data contains one record that breaks the ingest request rules
- WHEN it is triggered
- THEN no record is sent
- AND the trigger reports failure

### SIM-R5: Success means every record was accepted
The simulator SHALL report success for a trigger only when the ingest API accepted every
record.

#### Scenario: ingest API rejects a record
- GIVEN the ingest API answers one request with an error
- WHEN the trigger completes
- THEN the trigger reports failure

### SIM-R6: A trigger with no data fails
The simulator SHALL report failure, and send nothing, when the source holds no data for
the requested date or range.

#### Scenario: date without data
- GIVEN a date for which the source holds no rows
- WHEN that date is triggered
- THEN nothing is sent
- AND the trigger reports failure

### SIM-R7: An invalid trigger is rejected
The simulator SHALL reject a trigger whose dates are missing or malformed, or whose end
date is before its start date, and SHALL send nothing for it.

#### Scenario: end before start
- GIVEN an interval trigger whose end date precedes its start date
- WHEN it arrives
- THEN the trigger is rejected as invalid
- AND nothing is sent

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Trigger API | Serves | `SafeZone/utils/pydantic_model/request.py`, shared by its Python callers. | None. |
| Source data file | Reads | No contract file. The file is `SafeZone/data/<environment>/covid_data.csv`, mounted per environment. | One row per reported batch of cases, with a date, a city, a region and a count. The file does not change while the service runs. |
| Ingest API | Calls | `SafeZone/utils/pydantic_model/request.py`, shared with the Data Ingestor. | None. |
