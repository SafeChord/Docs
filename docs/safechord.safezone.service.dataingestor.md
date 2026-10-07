---
title: 'Service: Data Ingestor'
doc_id: safechord.safezone.service.dataingestor
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The Data Ingestor is the single entry point for case data. It validates each incoming record and publishes it to Kafka as a case event, keyed so that events for one city and region stay in order.
keywords:
  - Data Ingestor
  - Kafka Producer
  - Gateway
  - Event Driven
  - FastAPI
  - Load Leveling
logical_path: SafeChord.SafeZone.Service.DataIngestor
related_docs:
  - safechord.safezone.service.standards.md
  - safechord.safezone.decisions.md
  - safechord.safezone.changelog.md
parent_doc: safechord.safezone
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
> ([changelog](safechord.safezone.changelog.md)).

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

### ING-R2: Published events satisfy the event contract
Every event the ingestor publishes SHALL satisfy the event contract. This applies STD-R4
to the case event.

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
the event, and SHALL report failure when it cannot publish.

#### Scenario: topic unavailable
- GIVEN the ingestor cannot reach the topic
- WHEN a valid record arrives
- THEN the request fails
- AND the caller is not told the data was published

### ING-R5: An invalid record is rejected and nothing is published
The ingestor SHALL reject a request that breaks the ingest request rules, and SHALL
publish nothing for it.

#### Scenario: record with an invalid date
- GIVEN a request whose date is not a calendar date string
- WHEN it arrives
- THEN the request is rejected as invalid
- AND no event is published

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Ingest API | Serves | `SafeZone/utils/pydantic_model/request.py`, shared by its Python callers. | None. |
| Case event topic | Produces | `SafeZone/utils/contract/covid_event.json` | None. The key rule in ING-R3 is what the contract file cannot express. |
