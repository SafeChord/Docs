---
title: "SafeZone Toolkit: CLI 指令參考"
doc_id: safechord.safezone.toolkit.cli.reference
version: "0.1.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-20"
summary: "本文檔提供 SafeZone CLI (szcli) 的主要指令、使用範例及簡要功能說明。此工具旨在協助使用者透過命令列介面管理 SafeZone 系統的資料流模擬、資料驗證、資料庫維護以及系統時間控制等核心操作。"
keywords:
  - SafeZone CLI
  - command line interface
  - CLI reference
  - system management
  - data flow control
  - database operations
  - time management
  - SafeChord
logical_path: "SafeChord.SafeZone.Toolkit.CLI.reference"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.toolkit.cli.md"
  - "safechord.safezone.service.md"
parent_doc: "safechord.safezone.toolkit.cli"
tech_stack:
  - Python
  - Typer
---
## CLI 指令表格
| 工具類型 | 具體指令| 使用方式 | 說明 |
| --- | --- | --- | --- |
|| login | [`szcli login`](#login) | 登入系統開啟功能 |
| dataflow | simulate | [`szcli dataflow simulate <date>`](#simulate) | 模擬日期資料並寫入資料庫 |
| dataflow | verify | [`szcli dataflow verify <date>`](#verify) | 查詢特定日期的全國資料 |
| db | init | [`szcli db init`](#init) | 初始化資料庫 |
| db | clear | [`szcli db clear`](#clear) | 清空資料庫內容 |
| system | health | [`szcli system health...`](#health) | 組件健康檢查（多 target） |
| system | time | [`szcli system time...`](#time) | 時間查詢與調整（多指令）|

---
## login
* **用途**：
* **用法**：
* **參數**：
* **範例**：

## dataflow

### simulate

* **用途**：模擬指定日期（或區間）資料，並寫入資料庫
* **用法**：`szcli dataflow simulate <start_date> [--enddate <end_date>]`
* **參數**：
  * `<start_date>` (`DATE`): 指定模擬的起始日期 (格式: YYYY-MM-DD)
  * `--enddate <end_date>` (`DATE`, 選填): 模擬至指定結束日期 (格式: YYYY-MM-DD)
* **範例**：

  * `szcli dataflow simulate 2023-03-01`
  ```  
    success
  ```
  * `szcli dataflow simulate 2023-03-01 --enddate=2023-03-05`
  ```  
    success
  ```

### verify

* **用途**：查詢特定日期的全國或特定城市資料
* **用法**：`szcli dataflow verify <date> [--city <city_name>] [--region <region_name>] [--ratio]`
* **參數**：
  * `<date>` (`DATE`): 指定查詢的日期 (格式: YYYY-MM-DD)
  * `--city <city_name>` (`STRING`, 選填): 指定城市 (例如：台北市)
  * `--region <region_name>` (`STRING`, 選填): 指定區域 (例如：中山區)
  * `--ratio` (`BOOLEAN`, 選填): 數據顯示模式。若提供此 flag，則以比例（萬分之幾）顯示；否則以純數值顯示 (預設為純數值)。
* **範例**：
  * `szcli dataflow verify 2023-03-01 --ratio`
  ```  
    0.13
  ```
  * `szcli dataflow verify 2023-03-01 --city=台北市 --region=中山區`
  ```  
    25
  ```
---

## db

### init

* **用途**：初始化資料庫（建立必要表格與結構）
* **用法**：`szcli db init [--interval <days>]`
* **參數**：
  * `--interval <days>` (`INTEGER`, 選填): 指定包含初始資料的天數 (預設為 30)。
* **範例**：
  * `$ szcli db init --interval=30`
  ```  
    success
  ```

### clear

* **用途**：清空資料庫內容，選擇是否重置主鍵
* **用法**：`szcli db clear [--resetid]`
* **參數**：
  * `--resetid` (`BOOLEAN`, 選填): 若提供此 flag，會同時重置主鍵計數器。
* **範例**：
  * `$ szcli db clear --resetid`
  ```  
    success
  ```

---

## system

### health

* **用途**：檢查單一組件或所有組件健康狀態
* **用法**：`szcli system health [<target> | --all]`
* **參數**：
  * `<target>` (`STRING`, 選填): 指定要檢查的單一組件。可能的值：`db`, `redis`, `<api_name>`, `mkdoc`。
  * `--all` (`BOOLEAN`, 選填): 檢查所有組件的健康狀態。此參數與 `<target>` 互斥。
* **範例**：
  * `$ szcli system health db`
  ```  
    success
  ```
  * `$ szcli system health redis`
  ```  
    success
  ```
  * `$ szcli system health --all`
  ```  
    cli relay: success
    db: success
    redis: success
    data simulator: success
    data ingestor: success
    analytics api: success
    dashboard: success
    mkdoc: success
  ```

### time
**用途**：查詢、調整及顯示系統時鐘狀態（支援 mock 模式與實際時間模式的切換）
#### now
* **用途**：抓取當下時間
* **用法**：`szcli system time now`
* **參數**：無
* **範例**：
  * `$ szcli system time now`
  ```  
    current_time = 2023-03-23 
  ```
#### set
* **用途**：設定系統時間相關參數
* **用法**：`szcli system time set [--mocktime <date>] [--accelerate <rate>]`
* **參數**：
  * `--mocktime <date>` (`DATE`, 選填): 設定模擬時間，將系統時間設置為指定的日期 (格式：YYYY-MM-DD)。
  * `--accelerate <rate>` (`INTEGER`, 選填): 設定時間流速的加速倍率 (例如：2 表示時間流速加倍)。
* **範例**：
  * `$ szcli system time set --mocktime=2023-03-23`，
  ```  
    success 
    current_time = 2023-03-23 
  ```
  * `$ szcli system time set --accelerate=2`，
  ```  
    success 
    the speed of time flow *= 2 
  ```
#### status
* **用途**：查詢系統時間設定狀態
* **用法**：`szcli system time status`
* **參數**：無
* **範例**：
  * `$ szcli system time status`
  ```  
    mock = true
    current_time = 2023-03-23 
    accelerate = 2
  ```
---