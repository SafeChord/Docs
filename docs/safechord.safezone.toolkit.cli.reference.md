---
title: "SafeZone Toolkit: CLI Command Reference"
doc_id: safechord.safezone.toolkit.cli.reference
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-20"
summary: "SafeZone CLI (szcli) 指令參考手冊。列出所有可用的指令、參數說明及使用範例。"
keywords:
  - szcli
  - reference
  - commands
  - help
logical_path: "SafeChord.SafeZone.Toolkit.CLI.Reference"
related_docs:
  - "safechord.safezone.toolkit.cli.md"
parent_doc: "safechord.safezone.toolkit.cli"
---

# CLI 指令參考 (v0.2.1)

## 🔐 Auth Commands

### `szcli login`
啟動 OAuth 登入流程。
*   **說明**: 會在本地開啟瀏覽器進行 Google 登入。成功後 Token 儲存於 `~/.safezone/credentials.json`。

---

## 🌊 Dataflow Commands

### `szcli dataflow simulate <DATE>`
觸發模擬器產生數據。
*   **Arguments**:
    *   `DATE`: 起始日期 (YYYY-MM-DD)。
*   **Options**:
    *   `--enddate DATE`: 結束日期 (若未指定則僅模擬單日)。
    *   `--dry-run`: 僅印出將要執行的操作，不實際發送請求。
*   **範例**:
    ```bash
    # 模擬 2023-01-01 到 2023-01-31 的數據
    szcli dataflow simulate 2023-01-01 --enddate 2023-01-31
    ```

### `szcli dataflow verify <DATE>`
驗證數據是否正確寫入且可被查詢。
*   **Options**:
    *   `--city TEXT`: 指定城市。
    *   `--region TEXT`: 指定行政區。
    *   `--ratio`: 顯示確診率而非絕對數字。

---

## ⚙️ System Commands

### `szcli system time set`
控制系統模擬時間。
*   **Options**:
    *   `--mockdate DATE`: 設定虛擬的「今天」。
    *   `--acceleration INT`: 設定時間流速 (e.g., 3600 = 1小時/秒)。
    *   `--reset`: 回歸真實世界時間。

### `szcli system health [TARGET]`
檢查組件健康狀態。
*   **Arguments**:
    *   `TARGET`: `all`, `db`, `redis-cache`, `ingestor` 等 (Default: all)。

### `szcli health [TARGET]`
(Alias) 同 `szcli system health`。

---

## 🗄️ Database Commands

### `szcli db init`
初始化資料庫 Schema 與基礎數據。
*   **Options**:
    *   `--force`: 強制重置 (Drop tables)。

### `szcli db clear`
清空業務數據 (保留 Schema)。

### `szcli db reset`
完整重置資料庫 (Drop & Init)。需再次確認。
