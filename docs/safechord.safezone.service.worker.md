---
title: 'Service: Worker (Golang)'
status: active
archetype: blueprint
code_paths:
  - SafeZone/services/worker-golang
doc_version: 0.5.0
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
date, city and region. An event is valid when the worker can store it. Every event that
satisfies the event contract and names a city and region present in the
administrative-area tables is valid.

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

#### Scenario: another partition's writes succeed
- GIVEN an event whose write keeps failing, and events on another partition whose writes succeed
- WHEN the worker commits the other partition's progress
- THEN the failing event's offset is not committed
- AND that event is delivered again after restart

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

### WK-R9: Health reflects the consume loop
The worker SHALL report healthy (STD-R2) only while its consume loop has turned within
the configured liveness window. While the loop still turns, it SHALL stay healthy whether
or not the topic has events, and whether or not Kafka or the database is reachable.

#### Scenario: idle topic
- GIVEN a worker with no events to consume
- WHEN `/health` is requested
- THEN the response status is 200

#### Scenario: loop stalled
- GIVEN a worker whose consume loop has not turned for longer than the liveness window
- WHEN `/health` is requested
- THEN the response is not a success status

#### Scenario: database unreachable
- GIVEN a worker that cannot reach the database but whose loop is still turning
- WHEN `/health` is requested
- THEN the response status is 200

### WK-R10: The worker honours the contracts it depends on
The worker SHALL honour every contract its Dependencies table names, as STD-R4
requires. It accepts every event the event contract allows, and its reads and writes
fit the tables as the table contract defines them.

#### Scenario: event the contract allows
- GIVEN an event that satisfies the event contract
- WHEN the worker reads it
- THEN the worker parses it and does not reject it for its shape

#### Scenario: tables as the contract defines them
- GIVEN tables created from the table contract
- WHEN the worker reads the administrative areas and writes a case count
- THEN both succeed

### WK-R11: An unreachable dependency does not end the worker
While Kafka or the database is unreachable, the worker SHALL keep its consume loop turning
and SHALL NOT exit. Once the dependency is back, it SHALL resume from its committed progress
without a restart. A write or an offset commit that gets no answer within the configured
dependency timeout counts as failed.

#### Scenario: Kafka unreachable
- GIVEN a running worker
- WHEN Kafka stops answering and later comes back
- THEN the worker has not exited
- AND events produced after Kafka is back are persisted and committed

#### Scenario: database unreachable
- GIVEN events on the topic and a database that refuses writes, or takes them and never answers
- WHEN the database comes back
- THEN every event is persisted, by the same worker
- AND the committed offset did not move while the database was down

#### Scenario: offset commit fails
- GIVEN events already persisted
- WHEN Kafka refuses the offset commit, or takes it and never answers, and later answers again
- THEN the worker has not exited
- AND the committed offset reaches the end of the log

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Case event topic | Consumes | `SafeZone/contract/covid_event.json` | Events for one city and region arrive on one partition, in production order. WK-R2 depends on this. |
| Case table | Writes | `SafeZone/contract/schema.sql` | None. |
| Administrative-area tables (cities, regions) | Reads | Same as the case table. | Complete when the worker starts. Rows added later are not seen until restart. |
