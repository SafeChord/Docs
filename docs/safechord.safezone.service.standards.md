---
title: 'SafeZone Service Standards'
doc_id: safechord.safezone.service.standards
doc_version: 0.1.0
app_version: 0.3.8
status: active
authors:
  - bradyhau
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The promises every SafeZone service makes to the rest of the system - trace propagation, a health endpoint, and how a contract shared between services is defined and verified. Service blueprints link here instead of repeating them.
keywords:
  - Service Standards
  - Traceability
  - Health Check
  - Contract
logical_path: SafeChord.SafeZone.Service.Standards
related_docs:
  - safechord.safezone.md
  - safechord.safezone.decisions.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - SafeZone/services
  - SafeZone/utils/contract
---

# SafeZone Service Standards (Blueprint)

> **Type**: Blueprint (Cross-service)
> **Focus**: What every SafeZone service promises to the rest of the system.
> **Constraint**: Current state only, and only promises that bind more than one service.
> No coding conventions (`SafeZone/.ai-rules.md`). No field-level shape (contract files).
> No reasons ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](safechord.safezone.changelog.md)).

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

### STD-R2: An HTTP service reports its health
Every HTTP service SHALL answer `GET /health` with a success status while it is able to
serve requests.

#### Scenario: service is up
- GIVEN a running HTTP service
- WHEN `/health` is requested
- THEN the response status is 200

### STD-R3: A shared contract has one definition
A contract that more than one service depends on SHALL have exactly one definition.
When the services on either side are written in different languages, that definition
SHALL be a language-neutral file under `SafeZone/utils/contract/`. Each service's own
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
contract allows, and may accept more.

#### Scenario: producer drifts
- GIVEN a service that produces to a contract
- WHEN it would emit something the contract forbids
- THEN a unit test in that service fails

#### Scenario: consumer drifts
- GIVEN a service that consumes from a contract
- WHEN it cannot accept something the contract allows
- THEN a unit test in that service fails

## 2. Contracts

The contracts shared between SafeZone services, and where each is defined. Service
blueprints point at these files from their Dependencies table.

| Contract | Definition | Languages using it | State |
| :--- | :--- | :--- | :--- |
| Case event (Kafka topic) | `SafeZone/utils/contract/covid_event.json` | Python, Go | Language-neutral. Tests per STD-R4 tracked in SafeZone#70. |
| Database tables | `SafeZone/utils/db/schema.py` | Python, Go | Python-only definition. A SQL export under `SafeZone/utils/contract/` is tracked in SafeZone#70. |
| Service request and response models | `SafeZone/utils/pydantic_model/` | Python, TypeScript | Python-only definition. The dashboard mirrors it by hand. No ticket yet. |
| Administrative boundaries and region names | `SafeZone/utils/geo_data/` | Python, TypeScript | Language-neutral. A check of the dashboard's map data against it is tracked in SafeZone#55. |
| Cache version key | None | Python | The key name is duplicated between the relay CLI and the Analytics API. No ticket yet. |
