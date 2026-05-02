---
title: 'Toolkit: CLI Command Reference (Instruction Set)'
doc_id: safechord.safezone.toolkit.cli.reference
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Comprehensive operation manual for the SafeZone CLI. This document follows an "Intent-Driven" structure, serving as the standard reference for human operators and AI agents when executing system tasks, including environment setup, command paradigms, and expected behaviors.
keywords:
  - szcli
  - Command Reference
  - Instruction Set
  - Cheat Sheet
  - AI Prompts
logical_path: SafeChord.SafeZone.Toolkit.CLI.Reference
related_docs:
  - safechord.safezone.toolkit.cli.md
parent_doc: safechord.safezone.toolkit.cli
archetype: script
code_paths:
  - SafeZone/toolkit/cli/command
doc_version: 0.3.5
app_version: 0.3.2
---

# CLI Instruction Set (szcli)

> **Role**: AI Operator Manual
> This document defines the standard operating procedures for `szcli`. When an agent is assigned to perform system maintenance, data simulation, or health checks, it should prioritize the command paradigms defined in this manual.

---

## 1. Environment Context
Before invoking `szcli`, ensure the execution environment (Shell/Container) is equipped with the following variables:

| Variable | Required | Description |
| :--- | :--- | :--- |
| `RELAY_URL` | ✅ | Internal or external entry point for the Relay Service (e.g., `http://cli-relay:8000`). |
| `REFRESH_TOKEN` | ✅ | Google OAuth2 Refresh Token used for headless authentication. |
| `CLIENT_ID` | ✅ | GCP Project Client ID. |
| `CLIENT_SECRET` | ✅ | GCP Project Client Secret. |

---

## 2. Operational Intents (Instruction Set)

### 🌊 Dataflow Operations

#### Intent: Trigger Data Simulation
*   **Use Case**: Generate test data, backfill historical records, or perform stress tests.
*   **Command**:
    ```bash
    szcli dataflow simulate <START_DATE> [--enddate <END_DATE>] [--dry-run]
    ```
*   **Parameters**:
    *   `START_DATE`: `YYYY-MM-DD` (Required).
    *   `--enddate`: Optional end date for interval simulation.
*   **Expected Behavior**:
    *   Success: Returns JSON `{"success": true, ...}`. The Relay asynchronously triggers the Simulator Service.
    *   Side Effect: Resets the system's global Cache Version.

#### Intent: Verify Data Integrity
*   **Use Case**: Smoke test verification point, check data persistence, or observe cache hits.
*   **Command**:
    ```bash
    # Standard Verification
    szcli dataflow verify <DATE> [--city <NAME>] [--interval <DAYS>]
    
    # Observe Cache Status (Verbose Mode)
    szcli -o json -v dataflow verify <DATE>
    ```
*   **Verification Logic**:
    *   Parse the returned JSON. If `total_cases > 0` and `success` is `true`, the pipeline is considered operational.
    *   **Cache Check**: In `-v` mode, inspect `.headers.x-cache-status` in the JSON output. `HIT` indicates a cache hit; `MISS` indicates database penetration.
    *   If `404` or `count == 0` (unexpectedly), assume Ingestion Lag or Worker failure.

---

### ⚙️ System Control

#### Intent: Check System Health
*   **Use Case**: Post-deployment self-check.
*   **Command**:
    ```bash
    szcli system health [TARGET]
    ```
*   **Targets**: `all` (default), `cli-relay`, `db`, `redis-cache`, `simulator`, `ingestor`, `analytics-api`, `dashboard`.
*   **Expected Behavior**:
    *   Returns `status: healthy` for each component. If any component returns `unhealthy`, the agent should flag the task as failed.

#### Intent: Manage System Time
*   **Use Case**: Test future-time logic or reset back to real-time.
*   **Command**:
    ```bash
    # Set Mock Time
    szcli system time set --mockdate <YYYY-MM-DD> --acceleration <INT>
    
    # Reset to Real Time
    szcli system time set --reset
    
    # Check Current Status
    szcli system time status
    
    # Get Current System Date
    szcli system time now
    ```

---

### 🗄️ Database Operations

> ⚠️ **Warning**: These are destructive operations restricted to `admin` level access.

#### Intent: Initialize Schema
*   **Use Case**: Fresh environment setup (Cold Start).
*   **Command**: `szcli db init [--force]`

#### Intent: Clear Data
*   **Use Case**: Retain schema but remove all business data (Truncate).
*   **Command**:
    ```bash
    # Interactive execution
    szcli db clear
    
    # Automated / Non-interactive execution
    szcli db clear --yes
    ```

#### Intent: Hard Reset
*   **Use Case**: Full database reset (Drop & Init).
*   **Command**: `szcli db reset`

---

### ℹ️ General Utilities

#### Global Options
*   `-o, --output [rich|json|yaml]`: Set output format (Default: rich).
*   `-v, --verbose`: Display extra debugging info (e.g., HTTP Headers).

#### Intent: Check Version info
*   **Command**: `szcli version`

#### Intent: View Configuration
*   **Command**: `szcli config`

---

## 3. Error Handling

Agents parsing CLI output must follow these rules:

| Error Pattern | Interpretation | Suggested Action |
| :--- | :--- | :--- |
| `Refreshing authentication token...` | Info | Normal Auth flow; ignore. |
| `401 Unauthorized` | Auth Failure | Check if `REFRESH_TOKEN` is expired or invalid. |
| `403 Forbidden` | Permission Denied | Check if the authenticated `email` is on the Relay whitelist. |
| `Connection refused` | Network Error | Verify `RELAY_URL` or check if the Relay Pod has crashed. |
