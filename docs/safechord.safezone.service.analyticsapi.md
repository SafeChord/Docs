---
title: 'Service: Analytics API'
doc_id: safechord.safezone.service.analyticsapi
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5.5
last_updated: '2026-10-07'
summary: The Analytics API answers how many cases occurred in a time window for the nation, a city, or a region, as a count or as a rate per 10,000 residents. It serves repeated queries from a cache that is invalidated when the data set changes.
keywords:
  - Analytics API
  - FastAPI
  - Redis Cache
  - Global Invalidation
  - Cache Versioning
logical_path: SafeChord.SafeZone.Service.AnalyticsAPI
related_docs:
  - safechord.safezone.service.standards.md
  - safechord.safezone.decisions.md
  - safechord.safezone.changelog.md
parent_doc: safechord.safezone
archetype: blueprint
code_paths:
  - SafeZone/services/analytics-api
doc_version: 0.4.0
app_version: 0.3.7
---

# Analytics API (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](safechord.safezone.decisions.md)). No history
> ([changelog](safechord.safezone.changelog.md)).

## 1. Responsibility

*   **Role**: Reader / Aggregator
*   **Core Objective**: Acts as the read side of the system. It aggregates stored case counts over a time window at national, city or region level, and shields the database from repeated identical queries.

## 2. Requirements

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](safechord.safezone.service.standards.md) and are not repeated here.

### API-R1: A query returns the cases in a window
For a requested date and window length, the API SHALL return the sum of stored case
counts over the days ending on that date, both ends included, for the whole nation, for
one city, or for one region of a city.

#### Scenario: seven-day city query
- GIVEN stored case counts for a city across ten days
- WHEN the seven days ending on the last of them are queried for that city
- THEN the result is the sum of that city's counts over those seven days

### API-R2: A ratio query returns cases per 10,000 residents
When a ratio is requested for a city or a region, the API SHALL return the window's
cases per 10,000 residents of that city or region in place of the count.

#### Scenario: ratio for a region
- GIVEN a region with a known population and cases in the window
- WHEN a ratio is requested for it
- THEN the result is the cases divided by the population, times 10,000

### API-R3: A window without cases is zero
The API SHALL return zero, not an error, when no cases are stored for the requested
window and place.

#### Scenario: no data in the window
- GIVEN a valid city with no stored cases in the window
- WHEN it is queried
- THEN the result is zero

### API-R4: An unknown place is rejected
The API SHALL reject a query naming a city that does not exist, or a region that does
not belong to the named city.

#### Scenario: region of another city
- GIVEN a region that exists under a different city
- WHEN it is queried under the wrong city
- THEN the query is rejected as invalid

### API-R5: A repeated query is served from the cache
While the cache version is unchanged, the API SHALL answer a query it has already
answered without querying the database.

#### Scenario: same query twice
- GIVEN a query that has been answered once
- WHEN the same query arrives again under the same cache version
- THEN the answer is returned without a database query

### API-R6: A new cache version retires old answers
After the cache version changes, the API SHALL stop serving answers cached under the
previous version within one polling interval.

#### Scenario: data set replaced
- GIVEN an answer cached under one cache version
- WHEN the cache version changes and one polling interval passes
- THEN the same query is answered from the database again

### API-R7: Every answer says whether it came from the cache
Every aggregation response SHALL state, in a response header, whether it was served
from the cache or computed.

#### Scenario: first and second request
- GIVEN a query not yet cached
- WHEN it is sent twice
- THEN the first response is marked as computed and the second as served from the cache

### API-R8: Concurrent identical misses cost one query
Within one instance, identical queries that arrive together and miss the cache SHALL
result in a single database query.

#### Scenario: burst on a cold key
- GIVEN a query not yet cached
- WHEN many identical requests arrive at one instance at the same moment
- THEN the database is queried once

## 3. Dependencies

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| Query API | Serves | No language-neutral contract yet. `SafeZone/utils/pydantic_model/` is authoritative and the dashboard mirrors it by hand; no ticket yet. | None. |
| Case table | Reads | No language-neutral contract yet. `SafeZone/utils/db/schema.py` is authoritative; a SQL export is tracked in SafeZone#70. | One row per date, city and region. |
| Administrative-area and population tables | Reads | Same as the case table. | Complete when the API starts. Rows added later are not seen until restart. |
| Cache version key | Reads | No contract file. The key name is duplicated between the relay CLI and this service; no ticket yet. | Its value changes after every simulation trigger that adds data. |
| Response cache | Reads / Writes | Private to this service. | None. |
