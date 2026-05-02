---
title: "Service: [Service Name]"
doc_id: safechord.safezone.service.[name]
doc_version: [Document Version]
app_version: [Target Application Version]
status: draft
authors:
  - [Author Name]
last_updated: "YYYY-MM-DD"
summary: "[One sentence: core role, data flow position, key characteristic]"
keywords:
  - [keyword1]
  - [keyword2]
logical_path: "SafeChord.SafeZone.Service.[Name]"
related_docs:
  - "safechord.safezone.md"
parent_doc: "safechord.safezone.service"
archetype: blueprint
code_paths:
  - "SafeZone/services/[service-name]"
tech_stack:
  - [Language/Framework]
  - [Key Library]
---

# [Service Name] (Service Blueprint)

> Inherits from `archetype.blueprint.md`. Specialized for containerized
> microservices within `safechord.safezone.service.*`.

## 1. Responsibility
*(Required)*
*   **Role**: [Producer / Consumer / Aggregator / Gateway]
*   **Characteristics**: [Stateless / Stateful / Event-Driven / Read-Heavy]
*   **Core objective**: [What business problem does this service solve?]
*   **Architecture reference**: [Link to scaffold or pattern doc, if applicable]

## 2. File Structure
*(Required — directory-level with layer roles)*
```text
SafeZone/services/[service-name]/
├── app/
│   ├── main.py                   # App factory & lifespan
│   ├── api/                      # Routing layer: HTTP handling & dependency injection
│   ├── services/                 # Business logic (zero framework imports)
│   ├── core/                     # Settings, lifecycle, shared state
│   └── exceptions/               # Domain exceptions & global handlers
├── test/                         # TDD convergence boundary (unit, integration)
├── Dockerfile
└── requirements.txt
```
*(Pydantic models, test cases, and configuration details live in the codebase.)*

## 3. Business Requirements
*(Required)*
Describe **what** the service must do and **why**. Do NOT specify endpoint
paths, request/response schemas, or Kafka topic names — those are implementation
details owned by the codebase.

### Functional
*   [Core capability 1]
*   [Core capability 2]

### Performance
*   [Throughput, latency, or caching requirements]

### Consistency
*   [Data integrity or invalidation requirements]

### Observability
*   [Monitoring, tracing, or health check requirements]

> *Implementation reference: `app/api/endpoints.py`, `app/services/` in codebase.*

## 4. Dependencies & Control
*(Required)*

| Dependency | Type | Description |
| :--- | :--- | :--- |
| **Upstream** | Source | [Where data comes from] |
| **Downstream** | Sink | [Where data goes] |
| **Control Plane** | Trigger | [What initiates this service's work] |

## 5. TDD Convergence Boundaries
*(Required)*
Define the **constraint intents** that automated tests must enforce as
"physical red walls". Do NOT enumerate specific test cases or file paths.

| Verification Dimension | Constraint Intent | Test Scope |
| :--- | :--- | :--- |
| **[Dimension]** | [What invariant must hold?] | `test/unit/` or `test/integration/` |

> *Test cases and fixtures live exclusively in the codebase.*

## 6. Architecture Decision Records (ADR)
*(Optional — append as the service evolves)*
*   **[vX.Y] [Decision Name]**:
    *   **Decision**: [What was decided]
    *   **Why**: [Motivation and trade-offs]

## 7. External Links
*(Optional)*
*   **GitHub Issues**: [Links to relevant issues or discussions]
