---
title: 'Service: Worker (Golang)'
doc_id: safechord.safezone.service.worker
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The Worker consumes case events from Kafka and persists them to PostgreSQL. It guarantees that every valid event is stored, that the latest event for a key wins, and that committed progress never runs ahead of what is stored.
keywords:
  - Worker
  - Kafka Consumer
  - Golang
  - PostgreSQL
  - Idempotency
logical_path: SafeChord.SafeZone.Service.Worker
related_docs:
  - safechord.safezone.service.standards.md
  - safechord.safezone.decisions.md
  - safechord.safezone.changelog.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - SafeZone/services/worker-golang
doc_version: 0.4.0
app_version: 0.3.8
---

# Worker (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](safechord.safezone.changelog.md)).

## 1. Responsibility

*   **Role**: Consumer / Persister
*   **Core Objective**: Turns the stream of case events on Kafka into one stored case count per date, city and region in PostgreSQL, without losing events and without letting the consumer group's reported progress drift from what is actually stored.

## 2. Requirements

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](safechord.safezone.service.standards.md) and are not repeated here.

### WK-R1: Valid events are persisted
The worker SHALL store every valid event it reads as the case count for that event's
date, city and region. An event is valid when it satisfies the event contract and names
a city and region present in the administrative-area tables.

#### Scenario: valid event
- GIVEN a valid event on the topic
- WHEN the worker consumes it
- THEN the case table holds that count for its date, city and region

### WK-R2: The latest event for a key wins
For events sharing one date, city and region, the stored case count SHALL be that of the
latest event in topic order, however the events are batched or redelivered.

#### Scenario: two events for one key arrive together
- GIVEN two events for the same key with different case counts
- WHEN the worker persists them in a single write
- THEN the case table holds the later event's count

#### Scenario: redelivery
- GIVEN events that were already persisted
- WHEN they are delivered again
- THEN the stored counts are unchanged

### WK-R3: Progress is recorded only after persistence
The worker SHALL commit an event's offset only after that event is persisted or
deliberately skipped (WK-R5).

#### Scenario: stop before persistence
- GIVEN events read but not yet persisted
- WHEN the worker stops without persisting them
- THEN those events are delivered again after restart

### WK-R4: Committed progress never moves backwards
The consumer group's committed offset for a partition SHALL never decrease, and SHALL
reach the end of the log once every event is processed.

#### Scenario: membership changes during consumption
- GIVEN several workers consuming under load
- WHEN a worker joins or leaves the group
- THEN no partition's committed offset decreases
- AND group lag reaches zero after the last event is processed

### WK-R5: An invalid event never blocks the stream
The worker SHALL log and skip an event that is not valid (WK-R1), including one it cannot
parse, and SHALL keep consuming the events after it.

#### Scenario: invalid event between valid ones
- GIVEN an invalid event between two valid events
- WHEN the worker consumes all three
- THEN both valid events are persisted
- AND the invalid event is not delivered again

### WK-R6: Shutdown loses nothing
On SIGTERM the worker SHALL persist the events it holds and leave the consumer group
before exiting.

#### Scenario: terminate with events in hand
- GIVEN events read but not yet persisted
- WHEN the worker receives SIGTERM
- THEN those events are in the case table when the process exits
- AND the group reassigns its partitions without waiting for a session timeout

### WK-R7: Idle events are not held back
The worker SHALL persist an event within the configured flush interval even when no
further events arrive.

#### Scenario: traffic stops mid-batch
- GIVEN fewer events than a full batch
- WHEN no further events arrive for one flush interval
- THEN those events are in the case table

### WK-R8: Every handled event is traceable
Every log line the worker writes while handling an event SHALL carry that event's trace
ID, whether the event is persisted or skipped. This applies STD-R1 to a consumer.

#### Scenario: event skipped
- GIVEN an invalid event carrying a trace ID
- WHEN the worker skips it
- THEN the log line recording the skip carries the trace ID

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Case event topic | Consumes | `SafeZone/utils/contract/covid_event.json` | Events for one city and region arrive on one partition, in production order. WK-R2 depends on this. |
| Case table | Writes | No language-neutral contract yet. `SafeZone/utils/db/schema.py` is authoritative; a SQL export is tracked in SafeZone#70. | None. |
| Administrative-area tables (cities, regions) | Reads | Same as the case table. | Complete when the worker starts. Rows added later are not seen until restart. |
