---
title: 'Toolkit: CLI Command Reference (Instruction Set)'
doc_id: safechord.safezone.toolkit.cli.reference
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: '2026-04-15'
summary: SafeZone CLI 的指令操作手冊。本文件採用「意圖導向 (Intent-Driven)」結構，旨在作為人類維運者與 AI Agent 執行系統任務時的標準參考。包含環境配置要求、指令範式與預期行為。
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
doc_version: 0.3.0
app_version: 0.3.0-dev
---

# CLI Instruction Set (szcli)

> **Role**: AI Operator Manual
> 本文件定義了 `szcli` 的標準操作模式。當 Agent 被指派執行系統維運、資料模擬或健康檢查任務時，應優先參考本手冊的指令範式。

## 1. Environment Context (執行環境要求)
在調用 `szcli` 之前，必須確保執行環境 (Shell/Container) 具備以下變數：

| Variable | Required | Description |
| :--- | :--- | :--- |
| `RELAY_URL` | ✅ | Relay Service 的內部或外部入口 (e.g., `http://cli-relay:8000`). |
| `REFRESH_TOKEN` | ✅ | Google OAuth2 Refresh Token (用於 Headless Auth). |
| `CLIENT_ID` | ✅ | GCP Project Client ID. |
| `CLIENT_SECRET` | ✅ | GCP Project Client Secret. |

---

## 2. Operational Intents (維運意圖指令集)

### 🌊 Dataflow Operations (資料流控制)

#### Intent: Trigger Data Simulation (觸發模擬)
*   **Use Case**: 產生測試數據、填充歷史資料、壓力測試。
*   **Command**:
    ```bash
    szcli dataflow simulate <START_DATE> [--enddate <END_DATE>] [--dry-run]
    ```
*   **Parameters**:
    *   `START_DATE`: `YYYY-MM-DD` (Required).
    *   `--enddate`: 如果需要模擬一段區間，指定結束日期。
*   **Expected Behavior**:
    *   Success: 回傳 JSON `{"success": true, ...}`。Relay 會非同步觸發 Simulator Service。
    *   Side Effect: 系統的 Cache Version 會被重置。

#### Intent: Verify Data Integrity (驗證數據)
*   **Use Case**: Smoke Test 驗證點、檢查資料是否落盤、檢查快取命中。
*   **Command**:
    ```bash
    # 一般驗證
    szcli dataflow verify <DATE> [--city <NAME>] [--interval <DAYS>]
    
    # 觀測快取狀態 (Verbose Mode)
    szcli -o json -v dataflow verify <DATE>
    ```
*   **Verification Logic**:
    *   解析回傳的 JSON。若 `total_cases > 0` 且 `success` 為 `true`，則視為 Pipeline 運作正常。
    *   **快取檢查**: 在 `-v` 模式下，檢查 JSON 中的 `.headers.x-cache-status`。值為 `HIT` 表示命中快取，`MISS` 表示穿透至資料庫。
    *   若回傳 `404` 或 `count == 0` (且非預期)，則視為 Ingestion Lag 或 Worker 故障。

---

### ⚙️ System Control (系統控制)

#### Intent: Check System Health (健康檢查)
*   **Use Case**: 部署後的自我檢測 (Post-Deployment Check)。
*   **Command**:
    ```bash
    szcli system health [TARGET]
    ```
*   **Targets**: `all` (default), `cli-relay`, `db`, `redis-cache`, `simulator`, `ingestor`, `analytics-api`, `dashboard`.
*   **Expected Behavior**:
    *   回傳各組件的 `status: healthy`。若任一組件回傳 `unhealthy`，Agent 應標記任務失敗。

#### Intent: Manage System Time (時間控制)
*   **Use Case**: 測試「未來時間」的邏輯、重置回真實時間。
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

### 🗄️ Database Operations (資料庫維運)

> ⚠️ **Warning**: 這些是破壞性操作，僅限 `admin` 權限執行。

#### Intent: Initialize Schema (初始化)
*   **Use Case**: 全新環境建置 (Cold Start)。
*   **Command**: `szcli db init [--force]`

#### Intent: Clear Data (清空數據)
*   **Use Case**: 保留 Schema 但移除所有業務數據 (Truncate)。
*   **Command**:
    ```bash
    # 互動式執行
    szcli db clear
    
    # 自動化 / 非互動式執行
    szcli db clear --yes
    ```

#### Intent: Hard Reset (重置)
*   **Use Case**: 完整重置資料庫 (Drop & Init)。
*   **Command**: `szcli db reset`
*   **Note**: 此指令包含 `Drop Table` 操作，請謹慎使用。

---

### ℹ️ General Utilities (一般工具)

#### Global Options
*   `-o, --output [rich|json|yaml]`: 設定輸出格式 (預設: rich)。
*   `-v, --verbose`: 顯示額外的偵錯資訊（如 HTTP Headers）。

#### Intent: Check Version info
*   **Command**: `szcli version`

#### Intent: View Configuration
*   **Command**: `szcli config`


---

## 3. Error Handling (錯誤處理)

Agent 在解析 CLI 輸出時應遵循以下規則：

| Error Pattern | Interpretation | Suggested Action |
| :--- | :--- | :--- |
| `Refreshing authentication token...` | Info | 正常 Auth 流程，忽略。 |
| `401 Unauthorized` | Auth Failure | 檢查 `REFRESH_TOKEN` 是否過期或無效。 |
| `403 Forbidden` | Permission Denied | 檢查 `email` 是否在 Relay 的白名單中。 |
| `Connection refused` | Network Error | 檢查 `RELAY_URL` 是否正確，或 Relay Pod 是否 Crash。 |
