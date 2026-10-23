---
title: 'Service: Data Ingestor'
status: active
archetype: blueprint
code_paths:
  - SafeZone/services/data-ingestor
doc_version: 0.4.0
app_version: 0.3.8
---

# Data Ingestor (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](https://github.com/SafeChord/SafeZone/blob/main/CHANGELOG.md)).

## 1. Responsibility

*   **Role**: Gateway / Producer
*   **Core Objective**: Acts as the single entry point for case data. It turns each accepted HTTP request into one case event on Kafka, so that bursts of incoming traffic are absorbed by the topic and never reach the database directly.

## 2. Requirements

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](safechord.safezone.service.standards.md) and are not repeated here.

### ING-R1: An accepted record becomes one event
For every request it accepts, the ingestor SHALL publish exactly one event to the case
event topic, carrying the request's date, city, region and case count unchanged.

#### Scenario: valid record
- GIVEN a request with a valid record
- WHEN the ingestor accepts it
- THEN one event with the same date, city, region and case count is on the topic

### ING-R2: The ingestor honours the contracts it depends on
The ingestor SHALL honour every contract its Dependencies table names, as STD-R4
requires. Every event it publishes satisfies the event contract.

#### Scenario: event checked against the contract
- GIVEN any record the ingestor accepts
- WHEN the event built from it is validated against the contract file
- THEN validation passes

### ING-R3: Events for one city and region share a key
Events for the same city and region SHALL carry the same message key, and events for
different cities or regions SHALL carry different keys.

#### Scenario: same city and region
- GIVEN two records for the same city and region on different dates
- WHEN both are published
- THEN both events carry the same message key

### ING-R4: Success means the topic has the event
The ingestor SHALL report success for a request only after the topic has acknowledged
the event, and SHALL report failure within 4 seconds when it cannot publish.

#### Scenario: topic unavailable
- GIVEN the ingestor cannot reach the topic
- WHEN a valid record arrives
- THEN the request fails
- AND the caller is not told the data was published

#### Scenario: topic stops acknowledging
- GIVEN the topic stops acknowledging events after the ingestor has started
- WHEN a valid record arrives
- THEN the request fails within 4 seconds
- AND the event may still reach the topic once it recovers

### ING-R5: An invalid record is rejected and nothing is published
The ingestor SHALL reject a request that breaks the ingest request rules, and SHALL
publish nothing for it.

#### Scenario: invalid record
- GIVEN a request that breaks an ingest request rule
- WHEN it arrives
- THEN the request is rejected as invalid
- AND no event is published

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Ingest API | Serves | `SafeZone/utils/pydantic_model/request.py`, shared by its Python callers. | None. |
| Case event topic | Produces | `SafeZone/contract/covid_event.json` | None. The key rule in ING-R3 is what the contract file cannot express. |
