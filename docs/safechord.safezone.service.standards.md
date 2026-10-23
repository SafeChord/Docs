---
title: 'SafeZone Service Standards'
doc_version: 0.2.0
app_version: 0.3.8
status: active
archetype: blueprint
code_paths:
  - SafeZone/services
  - SafeZone/contract
  - SafeZone/utils
---

# SafeZone Service Standards (Blueprint)

> **Type**: Blueprint (Cross-service)
> **Focus**: What every SafeZone service promises to the rest of the system.
> **Constraint**: Current state only, and only promises that bind more than one service.
> No coding conventions (`SafeZone/.ai-rules.md`). No field-level shape (contract files).
> No reasons ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](https://github.com/SafeChord/SafeZone/blob/main/CHANGELOG.md)).

## 1. Requirements

Each requirement applies to every service unless it names a narrower set. A test that
enforces one carries its ID.

### STD-R1: A request is traceable end to end
A service SHALL carry the trace ID it receives through its own log lines and into every
request or event it sends on. A service that receives no trace ID SHALL create one.

#### Scenario: trace ID supplied over HTTP
- GIVEN a request carrying a trace ID in the `X-Trace-ID` header
- WHEN an HTTP service handles it
- THEN the response carries the same trace ID
- AND every request or event the service sends while handling it carries that trace ID

#### Scenario: no trace ID supplied
- GIVEN a request without a trace ID
- WHEN an HTTP service handles it
- THEN the response carries a newly created trace ID

#### Scenario: trace ID carried by an event
- GIVEN an event carrying a trace ID
- WHEN a consumer handles it
- THEN each log line the consumer writes for that event carries the trace ID

### STD-R2: A service reports its health
Every service SHALL answer `GET /health` with a success status while it is able to do
its work. A service that serves no other HTTP traffic still serves this endpoint.

#### Scenario: service is up
- GIVEN a running service
- WHEN `/health` is requested
- THEN the response status is 200

#### Scenario: service has stopped working
- GIVEN a service whose process is running but no longer doing its work
- WHEN `/health` is requested
- THEN the response is not a success status

### STD-R3: A shared contract has one definition
A contract that more than one service depends on SHALL have exactly one definition.
When the services on either side are written in different languages, that definition
SHALL be a language-neutral file under `SafeZone/contract/`. Each service's own
model, struct, or table definition is an implementation of it.

#### Scenario: two services in one language
- GIVEN a contract used only by Python services
- WHEN either service needs its shape
- THEN both import the same definition from `SafeZone/utils/`

#### Scenario: services in different languages
- GIVEN a contract used by services in different languages
- WHEN a service needs its shape
- THEN it implements the language-neutral file, not another service's code

### STD-R4: A service proves it honours each contract it touches
For every contract a service produces to or consumes from, the service SHALL have a
unit test that fails when its implementation and the contract definition disagree.
A producer emits only what the contract allows. A consumer accepts everything the
contract allows, and may accept more. An implementation that several services share
carries this test itself.

#### Scenario: producer drifts
- GIVEN a service that produces to a contract
- WHEN it would emit something the contract forbids
- THEN a unit test in that service fails

#### Scenario: consumer drifts
- GIVEN a service that consumes from a contract
- WHEN it cannot accept something the contract allows
- THEN a unit test in that service fails

#### Scenario: shared implementation drifts
- GIVEN an implementation of a contract under `SafeZone/utils/` that several services import
- WHEN it disagrees with the contract definition
- THEN a unit test of `SafeZone/utils/` fails

## 2. Contracts

The contracts shared between SafeZone services, and where each is defined. Service
blueprints point at these files from their Dependencies table.

| Contract | Definition | Languages using it | State |
| :--- | :--- | :--- | :--- |
| Case event (Kafka topic) | `SafeZone/contract/covid_event.json` | Python, Go | Language-neutral. |
| Database tables | `SafeZone/contract/schema.sql` | Python, Go | Language-neutral; `SafeZone/utils/db/schema.py` is its Python implementation. |
| Service request and response models | `SafeZone/utils/pydantic_model/` | Python, TypeScript | Python-only definition. The dashboard mirrors it by hand. No ticket yet. |
| Administrative boundaries and region names | `SafeZone/utils/geo_data/` | Python, TypeScript | Language-neutral. A check of the dashboard's map data against it is tracked in SafeZone#55. |
| Cache version key | None | Python | The key name is duplicated between the relay CLI and the Analytics API. No ticket yet. |
