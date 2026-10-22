---
title: 'SafeZone Decision Log'
status: active
archetype: brain
code_paths: []
---

# SafeZone Decision Log (Brain)

> **Type**: Brain (Decision Log)
> **Focus**: Why each decision was made, and what it traded away.
> **Constraint**: Reasons only. What a service must do today lives in its blueprint.
> What changed in a release lives in the [changelog](safechord.safezone.changelog.md).

## How this log works

*   **Append-only.** An accepted entry is never edited. When a decision changes, add a new
    entry and set the old entry's status to `Superseded by ADR-NNN`. That status line is the
    only part of an old entry that changes.
*   **One sequence.** Entries are numbered `ADR-001` upward across the whole log, in the
    order they are accepted. A number is never reused.
*   **Grouped by service.** Each entry sits in the chapter of the service it concerns.
    Decisions that bind more than one service go under Cross-service.
*   **Pointing at requirements.** `Affects` lists the requirement IDs the decision shapes.
    Blueprints do not point back.
*   **Imported entries.** ADR-001 to ADR-021 were moved here from the service blueprints on
    2026-10-07 with their original wording and version labels. Their version labels are the
    blueprints' and were not checked against the release: ADR-014's migration shipped in
    v0.2.1.

---

## Cross-service

### ADR-024: Shared contracts are language-neutral files, verified by unit tests
*   **Version**: v0.3.8 · **Status**: Superseded by ADR-031
*   **Affects**: STD-R3, STD-R4
*   **Decision**: A contract used from more than one language is defined once, as a language-neutral file under `SafeZone/utils/contract/`. Each service verifies its own implementation against that file with a unit test. Models are not generated from the contract.
*   **Why**: The case event had three hand-maintained versions (a JSON Schema, a Python model, a Go struct) that disagreed on three fields, and nothing noticed. The tables were defined only as Python code, which the Go worker could not read, so its SQL was hand-copied. Both came from never deciding how a contract crosses a language boundary. Generation was set aside because the contract file already existed and only lacked consumers, and because the ingest request model doubles as an HTTP request model with its own error messages. Decided in SafeZone#70.

### ADR-025: The case event contract records the wire as it runs
*   **Version**: v0.3.8 · **Status**: Superseded by ADR-032
*   **Affects**: ING-R2, WK-R1
*   **Decision**: `covid_event.json` is corrected to match what the Data Ingestor emits today. `version` is the contract version. The worker does not act on `version` yet.
*   **Why**: The ingestor is the only producer on the topic, so its output is the format in production; aligning the file to it changes no production code. A version check in the worker would have no effect while one version exists, and the choice between skipping and stopping on an unsupported version has no concrete case to decide against. Decided in SafeZone#70.

### ADR-026: Table definitions stay Python-sourced, with a SQL export
*   **Version**: v0.3.8 · **Status**: Superseded by ADR-033
*   **Affects**: STD-R3
*   **Decision**: `utils/db/schema.py` remains the source of the table definitions. A SQL export of it is committed as the language-neutral artifact, with a test that fails when the two differ.
*   **Why (Trade-off)**: Making SQL the source would replace how the database is initialized and rewrite the worker's persistence code while SafeZone#64 is changing it. The export gives other languages something to verify against at a fraction of that cost. The source stays a single-language implementation, which ADR-024 treats as a gap; the direction is revisited in v0.4.0, when the schema changes anyway. Decided in SafeZone#70.

### ADR-027: The Python scaffold is retired as a documentation standard
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: STD-R1, STD-R2
*   **Decision**: The Python Microservice Scaffold document is archived. Its trace and health standards move to the service standards. Its engineering principles (test-first, injected dependencies, framework-free business logic) move to `SafeZone/.ai-rules.md`. Its directory layout, layer rules, and Dockerfile patterns are no longer mandated by documentation.
*   **Why**: The scaffold fixed how code is written to the level of file names, which caps an implementer at the document author's ability and could not be reviewed for Go at all. A directory layout is also something an agent reads from the codebase directly. Keeping it in `Docs/` meant every structural refactor had to change documentation first. ADR-016, ADR-017 and ADR-018 record refactors that already happened and stay as they are.

### ADR-031: Contracts live in `SafeZone/contract/`, apart from any language's code
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: STD-R3, STD-R4
*   **Decision**: A contract used from more than one language is defined once, as a language-neutral file under `SafeZone/contract/`, at the top of the repository. `SafeZone/utils/` holds shared Python code only, including the Python implementations of contracts. Each implementation is verified against the contract file by a unit test: a service's own implementation in that service, a shared one in `utils/`. Models are not generated from the contract. Supersedes ADR-024.
*   **Why**: ADR-024 put the contract files inside `utils/`, the shared library of the Python services. The Go worker had to reach into another language's library for its contract, and the directory did not show which file was the definition and which an implementation of it. `utils/` stopped being a separate repository in SafeZone#66, so nothing ties the contract files to it any longer. The rest of ADR-024 stands. Decided in SafeZone#70.

### ADR-032: The case event contract is strict, and the services follow it
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: ING-R2, ING-R5, WK-R1, WK-R5
*   **Decision**: `covid_event.json` states what a case event must be, not what the Data Ingestor happens to emit: a fixed `event_type` and `version`, every field required, no field beyond those listed, a date that is a real calendar date, and a case count the table can hold. A service that accepts more than the contract is brought in line in its own ticket. `version` is the contract version, and adding a field takes a new one. The worker may still accept more than the contract allows, and does not act on `version` yet. Supersedes ADR-025.
*   **Why (Trade-off)**: Recording the wire as it ran would have written two gaps into the contract: the ingest API and the worker both let through a date that is no calendar date and a case count the table cannot hold. Settling the contract first and aligning the services to it costs the production changes ADR-025 avoided (SafeZone#82, SafeZone#85). In return the contract is something a new consumer can rely on. A value is adjusted when development shows it to be wrong. Decided in SafeZone#70.

### ADR-033: The table contract is a SQL file, and the Python schema implements it
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: STD-R3, STD-R4
*   **Decision**: `SafeZone/contract/schema.sql` is the definition of the tables. `utils/db/schema.py` is the Python implementation of it, and a test in `utils/` fails when the two differ. The database is still created from `schema.py`. Supersedes ADR-026.
*   **Why (Trade-off)**: ADR-026 kept the Python code as the source and the SQL as a copy of it, which left the one definition bound to one language. Its two reasons no longer hold: SafeZone#64 is merged, and a SQL definition does not require rewriting the worker's persistence code, only checking it. Initializing the database from the SQL file is the part with a real cost, and it stays for v0.4.0. Until then the test compares the SQL that `schema.py` generates with the file, so the file has to keep the form SQLAlchemy emits. Decided in SafeZone#70.

---

## Pandemic Simulator

### ADR-002: API Trigger Pattern
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: SIM-R1, SIM-R2
*   **Decision**: Abandoned internal CronJobs in favor of REST API triggers from the Control Plane (CLI/TimeServer).
*   **Why**: Increases controllability and supports manual replay for any time point, centralizing scheduling logic.

### ADR-009: Concurrency Control (Semaphore Management)
*   **Version**: v0.2.1 · **Status**: Accepted
*   **Affects**: SIM-R3
*   **Decision**: Introduced `asyncio.Semaphore` in the `data_sender.py`.
*   **Why (Trade-off)**: Prevents the Simulator from exhausting system file descriptors (FD) when sending thousands of data points, while providing "Back-pressure" protection for downstream services.

### ADR-016: Python Microservice Scaffold Integration
*   **Version**: v0.3.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Refactored the legacy `pipeline/` module into the `services/` and `api/` layers.
*   **Why**: Standardizes the directory structure to align with the `analytics-api` development model.

---

## Data Ingestor

### ADR-003: Evolution: From Sync DB to Event-Driven Ingestion
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: ING-R1
*   **Decision**: Removed direct PostgreSQL write logic in favor of a Kafka Producer.
*   **Why (Load Leveling)**: The previous synchronous model coupled Ingestor throughput to DB IOPS. Decoupling via Kafka provides a buffer for traffic bursts and allows the database to be taken offline for maintenance without stopping data ingestion.

### ADR-004: Natural Key Partitioning
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: ING-R3, WK-R2
*   **Decision**: Switched to using `city-region` as the Kafka Partition Key.
*   **Why (Trade-off)**: While it might lead to partition skew, it guarantees strict chronological order for regional data, which is a prerequisite for accurate backend statistics.

### ADR-010: Asynchronous Production (aiokafka)
*   **Version**: v0.2.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Integrated `aiokafka` into the FastAPI event loop.
*   **Why**: Resolved HTTP thread blocking issues caused by synchronous Kafka writes, significantly increasing gateway throughput.

### ADR-017: Python Microservice Scaffold Integration
*   **Version**: v0.3.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Refactored the flat directory structure into the `api/core/services/exceptions` layered pattern.
*   **Why**: Standardizes development across all SafeZone services to reduce cognitive load for both AI and human engineers.

### ADR-034: A publish the topic does not acknowledge fails after 4 seconds
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: ING-R4
*   **Decision**: The ingestor waits at most 4 seconds for the topic to acknowledge an event, then answers the request with a failure. The event is not taken back: the producer keeps what it has accepted and delivers it once the topic recovers, so a request reported as failed may still have been published.
*   **Why (Trade-off)**: With the broker lost after startup, the producer retries without ever raising, and the request hung for over two minutes; the caller was never told the publish failed. 4 seconds sits below the simulator's 5-second client timeout, so the simulator sees the failure rather than its own timeout. The timeout does not take the event back from the producer, and that cost is accepted: in review, all 21 requests answered with a failure during an outage were delivered after it, and a caller that retries publishes the record twice. Duplicates are not new to the pipeline; the worker already consumes at least once (ADR-022). Decided in SafeZone#82.

---

## Worker

### ADR-005: At-Most-Once Lean Strategy
*   **Version**: v0.2.0 · **Status**: Superseded by ADR-022
*   **Affects**: None
*   **Decision**: Implemented an aggressive offset commit strategy coupled with DB Upserts.
*   **Why (Trade-off)**: Prioritizes throughput over strict exactly-once guarantees. In non-financial scenarios like SafeZone, this trade-off simplifies state management while remaining recoverable via upstream replays.

### ADR-013: Batch-First Persistence
*   **Version**: v0.2.5 · **Status**: Superseded by ADR-029
*   **Affects**: WK-R7
*   **Decision**: Set default batch size to 1000 records.
*   **Why**: Individual SQL inserts are the primary bottleneck for DB performance. Shifting pressure from DB IOPS to memory allows the system to handle simulator bursts effectively.

### ADR-014: Franz-Go Client Migration
*   **Version**: v0.3.0 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Switched from `segmentio/kafka-go` to `twmb/franz-go`.
*   **Why**: Superior performance and full KRaft protocol support, reducing CPU overhead during peak consumption.

### ADR-015: Idiomatic Go Refactor
*   **Version**: v0.3.0 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Replaced Java-style factories with package-level constructors and interface injection.
*   **Why**: Simplifies the code hierarchy and adheres to Go conventions, making mocking adapters for unit tests significantly easier.

### ADR-022: At-Least-Once Consumption
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: WK-R3, WK-R4, WK-R5, WK-R6
*   **Decision**: Offsets are committed only after the events are persisted, once per write, and the committed position follows the last event read so that skipped events are committed past. Supersedes ADR-005.
*   **Why**: Committing on read lost up to one batch on a crash, and commits sent after a rebalance by a consumer that no longer owned the partition rewound the group's progress, leaving lag that never drained and pinned the autoscaler. The at-most-once behavior was a library default carried over from the first worker, and ADR-005 was written afterwards to justify it. The idempotent upsert already makes redelivery harmless, and one commit per write is cheaper than one per event. Decided in SafeZone#64.

### ADR-023: The later event wins within a single write
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: WK-R2
*   **Decision**: When one write holds several events for the same date, city and region, the latest one is kept.
*   **Why**: Across writes the upsert already keeps the latest event, but within a write the first was kept, so the stored result depended on where batch boundaries fell. At-least-once consumption (ADR-022) regroups batches on redelivery and must not change the result. Upstream is not expected to send differing values for one key; this is a defensive guard, not a response to observed data. Decided in SafeZone#64.

### ADR-028: The worker reports health over HTTP, as the turning of its loop
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: WK-R9, STD-R2
*   **Decision**: The worker serves `GET /health` like every other service. It is healthy while its consume loop keeps turning, whatever the lag and whether or not Kafka and the database are reachable.
*   **Why (Trade-off)**: The worker was designed as an event-driven consumer, not an API, so it had no health signal and Kubernetes could not tell a stuck worker from a working one. An HTTP endpoint was chosen over a heartbeat file checked by an exec probe so that all services are checked the same way, and so that metrics can later share the port. Health deliberately ignores lag, which is the autoscaler's concern, and ignores dependencies: if an unreachable broker or database failed the check, every worker would be restarted at once and come back to the same outage. The cost is that a worker cut off from its dependencies still reports healthy; that condition shows up as lag instead. Decided in SafeZone#71.

### ADR-029: One write and one commit per poll
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: WK-R2, WK-R3, WK-R4, WK-R7
*   **Decision**: The worker persists what a poll returned and commits its offsets before it polls again, and keeps no event from one poll to the next. A batch is whatever one poll returns, up to the configured batch size. Supersedes ADR-013.
*   **Why (Trade-off)**: An event held between polls can outlive the worker's ownership of its partition. Gathering events across polls, as ADR-013 had it, led either to a worker that stopped for good when the group rebalanced under light traffic, or to a worker that had lost a partition writing its older events over what the new owner had since stored. Holding nothing removes both, and it lets the client hold a rebalance back for exactly as long as one write and one commit take. The price is the one ADR-013 set out to avoid: under light traffic a poll returns a single event, so each event gets its own database transaction. Under a backlog a poll fills and the writes are batched as before, which is when batching matters. Offset commits are no more frequent than they were. Decided in SafeZone#64.

### ADR-030: A failed offset commit ends the worker
*   **Version**: v0.3.8 · **Status**: Superseded by ADR-035
*   **Affects**: WK-R3
*   **Decision**: When an offset commit fails, the worker stops and the process exits with a non-zero status after logging the cause. It does not log the failure and carry on, and it adds no retry of its own.
*   **Why (Trade-off)**: Stopping loses nothing: the events are already stored, the next owner reads again from the last committed offset, and the idempotent upsert makes the repeat harmless. The Kafka client already retries the coordinator errors that clear by themselves, so a failure that reaches the worker is unlikely to pass by waiting, and one that repeats on every attempt must be visible. The exit has to be loud because it is the only signal the worker gives whatever runs it. Two costs are accepted: while the broker is unreachable the worker restarts in a loop, and consumption resumes only after the restart backoff once the broker is back; and when several workers fail together, their leaving and rejoining keeps the group rebalancing. Decided in SafeZone#64.

### ADR-035: The worker rides out an unreachable dependency instead of exiting
*   **Version**: v0.3.8 · **Status**: Accepted
*   **Affects**: WK-R3, WK-R9, WK-R11
*   **Decision**: A failed poll, a failed write and a failed offset commit no longer end the worker. After a failed write the worker drops the events that poll returned, moves its position back to the first of them, and reads them again on a later turn. After a failed commit it carries on, and the next commit that succeeds covers it. It waits between failed attempts. A write or a commit that gets no answer within a configured timeout, set below the liveness window, counts as failed. Failures are not sorted into transient and permanent: every one of the three is ridden out. Supersedes ADR-030.
*   **Why (Trade-off)**: ADR-028 kept dependencies out of the health check so that an outage would not restart every worker at once into the same outage, and the error handling did exactly that: against an in-process broker, the worker exited 0.7 seconds after the broker was lost and 0.3 seconds after a commit failed. Exiting bought nothing: either way nothing unstored is committed, and in the same reproduction the Kafka client, polled again, recovered by itself about two seconds after the broker came back. Retrying a failed write in place was set aside because it holds the group's rebalance back for as long as the database is down; reading the events again keeps ADR-029's rule that no event outlives its poll. ADR-030 reasoned that a commit failure reaching the worker is unlikely to pass by waiting, which does not hold for an unreachable broker, the common case of a failed commit; keeping it would have left a broker outage ending the worker or not depending on which call it hit. The timeout exists because a database or broker that takes a call and never answers stalls the loop instead of failing it: a commit sent to a silent broker waited 46 seconds, long enough for the liveness probe to restart the worker. Sorting failures was set aside because it buys visibility, not correctness. The cost is that a failure that never clears by itself, such as wrong credentials, a missing table or a batch the database rejects for its content, leaves a worker that reports healthy and makes no progress. That shows only as lag and repeated error logs, the condition ADR-028 already accepted for a worker cut off from its dependencies. Decided in SafeZone#98.

---

## Analytics API

### ADR-001: In-Memory Static Data Preloading
*   **Version**: v0.1.0 · **Status**: Accepted
*   **Affects**: API-R1, API-R2
*   **Decision**: Preload low-frequency data (City/Region mappings, population benchmarks) into memory during startup.
*   **Why**: Reduced complex SQL JOINs to simple fact-table aggregations, significantly improving query performance.

### ADR-006: Response Caching
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: API-R5, API-R6
*   **Decision**: Implemented Redis-based response caching for all aggregation endpoints.
*   **Why**: Minimizes API latency and provides a defensive layer for the PostgreSQL backend in a read-heavy environment.

### ADR-007: Cache Versioning & Stampede Protection
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: API-R6, API-R8
*   **Decision**: Implemented `asyncio.Lock` for Double-Check Locking within the `@redis_cache` decorator.
*   **Why**: Prevents "Cache Stampede" where concurrent requests hit the DB simultaneously during a cache miss.

### ADR-018: Layered Dependency Injection
*   **Version**: v0.3.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Replaced `request.app.state` access with explicit DI in `api/dependencies.py`.
*   **Why**: Sacrificed slight development speed for significant testability, allowing business logic in `services/` to remain framework-agnostic.

### ADR-019: Pure ASGI Middleware
*   **Version**: v0.3.1 · **Status**: Accepted
*   **Affects**: API-R7
*   **Decision**: Switched from `BaseHTTPMiddleware` to a pure ASGI interface for `TraceAndCacheMiddleware`.
*   **Why**: Resolved isolation issues where `ContextVar` (e.g., for `X-Cache-Status`) failed to propagate across task groups, ensuring consistent observability.

---

## Dashboard (v1, legacy)

### ADR-008: Component-Based UI Management
*   **Version**: v0.2.0 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Decoupled the layout into reusable components in `app/components/`.
*   **Why**: Reduces the complexity of `main.py` and allows for isolated UI testing of specific widgets.

### ADR-011: Plotly Dash Framework
*   **Version**: v0.2.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Chose Dash over React/Vue.
*   **Why (Trade-off)**: Empowers backend-centric engineers to maintain the full UI/Logic stack within Python, maximizing development efficiency for this administrative and visualization tool.

### ADR-012: Time-Aware Polling Architecture
*   **Version**: v0.2.1 · **Status**: Accepted
*   **Affects**: None
*   **Decision**: Implemented client-side polling via `dcc.Interval` coupled with a backend `TimeManager`.
*   **Why**: Solves the visualization drift problem in distributed simulation environments by decoupling the UI from physical time.

---

## Dashboard v2

### ADR-020: Nginx Decoupling
*   **Version**: v0.1.0 (dashboard-v2) · **Status**: Accepted
*   **Affects**: DSH-R7
*   **Decision**: We removed the `COPY nginx.conf` directive from the `Dockerfile`. The production container image compiles the TypeScript files and outputs static files to the public root. The configuration file `nginx.conf` must be injected externally.
*   **Why**: We adopted this approach to support both local development (using Docker Compose read-only volume mounts) and Kubernetes production (using K8s ConfigMap mounts) without rebuilding or maintaining separate Docker images for different environments.

### ADR-021: TopCities 7-Day Window Isolation
*   **Version**: v0.1.0 (dashboard-v2) · **Status**: Accepted
*   **Affects**: DSH-R4
*   **Decision**: We extracted a dedicated React hook `useTopCities` that hardcodes the query parameter `interval="7"` for all city aggregation calls, completely bypassing the global interval state.
*   **Why**: This enforces the system requirement that the Top 10 scoreboard always represents the 7-day rolling aggregates, preventing confusion when users dynamically switch the main trend charts to other aggregates.
