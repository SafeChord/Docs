---
title: 'Toolkit: CLI Command Reference (Instruction Set)'
doc_id: safechord.safezone.toolkit.cli.reference
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-06-24'
summary: Comprehensive operation manual for the SafeZone CLI. Fully expanded with strict parameter limits, expected JSON wrapper structures, and runbooks optimized for AI Operators.
keywords:
  - szcli
  - Command Reference
  - Instruction Set
  - AI Operators
  - JSON Envelope
logical_path: SafeChord.SafeZone.Toolkit.CLI.Reference
related_docs:
  - safechord.safezone.toolkit.cli.md
parent_doc: safechord.safezone.toolkit.cli
archetype: script
code_paths:
  - SafeZone/toolkit/cli/command
doc_version: 0.4.0
app_version: 0.3.2
---

# CLI Instruction Set (szcli) - AI-Optimized Manual

> **Role**: AI Operator Reference Manual
> This document defines the exact commands, validation rules, output structures, and composite operation runbooks for `szcli`. 
> **AI Operators must strictly adhere to the schemas and command combinations defined here.**

---

## 1. Environment & Global Options

Before invoking `szcli`, ensure the following environment variables are present:
* `RELAY_URL`: Internal/external endpoint for the Relay Service (e.g., `http://cli-relay:8000`).
* `REFRESH_TOKEN`: Google OAuth2 Refresh Token for headless auth.
* `CLIENT_ID` / `CLIENT_SECRET`: GCP OAuth credentials.

### Global CLI Flags
Any command can be prefixed with these flags to modify logging and output formats:
* `-o, --output [rich|json|yaml]`: Output presentation format. **AI agents should always use `-o json` to ensure programmatically parsable outputs.**
* `-v, --verbose`: Display protocol-level metadata (e.g., HTTP headers).
* `-d, --debug`: Enable debug logs for client operations.

### 🔴 CRITICAL: Output JSON Wrapping (Envelope)
When running commands with `-o json`, the output is **wrapped** in a standard envelope by the client wrapper before rendering. 
* **Target Data**: The underlying `APIResponse` payload is always nested under the **`.response`** key.
* **Headers**: In `-v` mode, HTTP response headers from the API are present under the **`.headers`** key (keys are lowercase).
* **AI Pathing**: Always query values using `.response.<field>` (e.g., `.response.success` or `.response.data.aggregated_cases`). Querying top-level fields directly will yield `null`.

---

## 2. Command Reference & API Specifications

### 🗄️ Database Operations (`db` group)
High-privilege database maintenance operations.

#### Intent: Initialize Schema
* **Command**: `szcli db init [--force]`
* **Constraints**: 
  * `--force` clears all tables and re-seeds administrative/population data. It does not drop the database structure.
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "db.init",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Database initialized successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### Intent: Prune Data (Fact Table Only)
* **Command**: `szcli db prune [--year YYYY] [--all] [--yes/-y]`
* **Validation Rules**:
  * **XOR Requirement**: Exactly one of `--year YYYY` or `--all` **must** be specified. Providing both or neither will result in a client-side abort.
  * **Confirmation**: If `--yes` (or `-y`) is omitted, the client will prompt for confirmation. For automated scripts, always pass `--yes`.
* **Side-Effects**:
  * Targets the **`covid_cases` fact table only**. Dimensions (`cities`, `regions`, `populations`) survive.
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "db.prune",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Covid cases pruned successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### Intent: Database Reset (Truncate All Tables)
* **Command**: `szcli db reset`
* **Confirmation**: Always prompts for confirmation interactively. (Non-interactive flags are not supported for safety).
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "db.reset",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Database reset successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

---

### 🌊 Dataflow Operations (`dataflow` group)
Controls the ingestion simulator and verifies persisted data.

#### Intent: Trigger Simulation
* **Command**: `szcli dataflow simulate <DATE> [--enddate YYYY-MM-DD] [--dry-run]`
* **Constraints**:
  * `<DATE>`: Ingestion start date (Argument, required, format: `YYYY-MM-DD`).
  * `--enddate`: Optional end date for interval generation.
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "dataflow.simulate",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Simulation triggered successfully.",
      "detail": "Data ingestion process initiated.",
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### Intent: Verify Data Integrity
* **Command**: `szcli dataflow verify <DATE> [--interval INT] [--city NAME] [--region NAME] [--ratio]`
* **Constraints**:
  * `<DATE>`: Target verification date (Argument, required, format: `YYYY-MM-DD`).
  * `--interval`: Period in days (Default: `1`).
  * `--city` / `--region`: Optional string filters (validated downstream to be 1–50 characters).
  * `--ratio`: Returns population ratio instead of raw case counts if set.
* **Expected Wrapped Response (with -v verbose enabled)**:
  ```json
  {
    "task": {
      "name": "dataflow.verify",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Verification completed.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "data": {
        "start_date": "1970-01-01",
        "end_date": "1970-01-01",
        "city": "台北市",
        "region": "信義區",
        "aggregated_cases": 1500,
        "cases_population_ratio": 0.015
      }
    },
    "headers": {
      "content-type": "application/json",
      "x-cache-status": "HIT"
    }
  }
  ```
* **Cache Assertion**: In `-v` mode, check if the response was cached by inspecting the `.headers["x-cache-status"]` lowercase key in the wrapped JSON output (values: `HIT` or `MISS`).

---

### ⚙️ Time Control (`system time` sub-group)
Controls the virtual system clock. All active components query this clock.

#### Intent: Get Virtual Date
* **Command**: `szcli system time now`
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "time.now",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Current virtual time retrieved.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "system_date": "2000-01-01"
    }
  }
  ```

#### Intent: Get Virtual Time Configuration
* **Command**: `szcli system time status`
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "time.status",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Mock time config retrieved.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "data": {
        "mock": true,
        "mock_date": "2000-01-01",
        "mock_update_time": "2026-06-24T01:00:00Z",
        "launch_time": "2026-06-24T00:00:00Z",
        "acceleration": 5,
        "system_date": "2000-01-01"
      }
    }
  }
  ```

#### Intent: Set Virtual Time
* **Command**: `szcli system time set [--reset] [--mockdate YYYY-MM-DD] [--acceleration INT]`
* **Validation Rules**:
  * **Mock Constraint**: Unless `--reset` is specified, you **must** provide at least one of `--mockdate` or `--acceleration`.
  * **Acceleration Bounds**: `--acceleration` must be an integer between **`1` and `10`** (inclusive).
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "time.set",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "System time configured successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

---

### 🩺 Health Checks (`health` group)
Checks component status across the cluster. Note: This is an independent group (`szcli health`), not under `system`.

#### Intent: Component Diagnosis
* **Command**: `szcli health <COMPONENT>`
* **Valid Components**: 
  * `all`, `cli-relay`, `db`, `redis-state`, `redis-cache`, `simulator`, `ingestor`, `analytics-api`, `dashboard`.
* **Expected Wrapped Response**:
  ```json
  {
    "task": {
      "name": "health.all",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Health check completed successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "status": {
        "db": "healthy",
        "redis-state": "healthy",
        "simulator": "healthy"
      }
    }
  }
  ```

---

## 3. Standard Failure Scopes

When a command fails on the client, relay, or downstream levels, the response parses `errors` structures:

### Common Validation Error (e.g. invalid date format)
```json
{
  "task": {
    "name": "time.set",
    "trace_id": "8f2b3c1a-..."
  },
  "response": {
    "success": false,
    "message": "Validation failed.",
    "detail": "Invalid input format.",
    "errors": {
      "field": "mock_date",
      "summary": "Invalid value",
      "detail": "Invalid date format. Expected 'YYYY-MM-DD'."
    },
    "timestamp": "2026-06-24T01:00:00Z"
  }
}
```

---

## 4. AI Runbook Recipes (Scenario Patterns)

### Recipe A: Clean Cold-Start Seeding and Verification
Used by test agents to start from a clean slate, travel to a target time, ingest data, and verify.

1. **Perform Database Reset**:
   ```bash
   szcli db reset
   # (Interactive confirmation required; execute manually)
   ```
2. **Configure Target Timeline**:
   ```bash
   szcli -o json system time set --mockdate 2000-01-01 --acceleration 5
   # Assert .response.success == true
   ```
3. **Verify Empty State**:
   ```bash
   szcli -o json dataflow verify 2000-01-01
   # Assert .response.success == true AND .response.data.aggregated_cases == null
   ```
4. **Trigger Generation**:
   ```bash
   szcli -o json dataflow simulate 2000-01-01
   # Assert .response.success == true
   ```
5. **Poll and Assert Persistence**:
   ```bash
   szcli -o json dataflow verify 2000-01-01
   # Assert .response.success == true AND .response.data.aggregated_cases > 0
   ```
