---
title: "SafeZone Toolkit: CLI，SafeZone 系統管理工具"
doc_id: safechord.safezone.toolkit.cli
version: "0.1.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-28"
summary:
  本文檔說明 SafeZone CLI 工具的核心功能、技術選型與設計思路。內容涵蓋指令操作說明、模組結構、執行環境，及 CLI 與 K3Han 系統中 Relay 互動的全流程。SafeZone CLI 是串聯各微服務與資料流、協助系統維運、測試與自動化的核心管理介面，兼顧人員友善與 AI 可解析結構。
keywords:
  - SafeZoneToolkit
  - CLI
  - command line interface
  - system management
  - FastAPI
  - SQLAlchemy
  - Docker
  - shell script
  - Google OAuth
  - K3Han relay
  - data flow control
  - database operations
  - SafeChord
logical_path: "SafeChord.SafeZone.Toolkit.CLI"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.toolkit.cli.reference.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Python
  - FastAPI
  - SQLAlchemy
  - Docker
  - Shell Script
  - Google OAuth
  - Typer
---
# SafeZone CLI

## 簡介

SafeZone CLI（szcli）是一套專為 SafeZone 系統打造的命令列管理工具，提供從資料流控制、資料庫操作、系統維運到測試驗證的完整操作入口。它設計的目標是讓開發者、維運人員、測試者能以一致、簡單的介面對整個 SafeZone 系統進行自動化操作或日常維護。

技術棧：FastAPI、SQLAlchemy、Docker、Shell Script、Google OAuth、Python Typer
---

## 各模組說明

### Command（命令列指令入口）

主要角色是讓使用者能直接在 shell 下執行 szcli 指令，不需關心底層的網路或認證細節。

每一條指令（如 `szcli dataflow simulate`）實際會透過 docker exec 執行於 daemon container 內，封裝環境依賴、提升安全性。

指令覆蓋 SafeZone 各核心業務，包括資料模擬、查詢、資料庫初始化、健康檢查等。

#### 操作前認證規則（強制登入）

* **所有與 relay 溝通的 szcli 指令，在執行前必須先主動執行 **************\`\`************** 完成用戶認證。**
* 登入成功後，CLI 工具會保存 access token，後續所有 relay 操作才會通過 Google OAuth 驗證。
* 若未登入或 access token 失效，所有 relay 互動相關的 CLI 指令（如 dataflow、db、system 等）都會拒絕執行，並提示「請先登入」。

### Relay（中繼與服務協調）

* 於 K3Han 叢集內部署，作為所有 CLI 指令的統一入口與 API 轉發中心。
* 接收外部 CLI 的 RESTful 請求，負責 Google OAuth 認證、權限控管，並分派請求給系統各內部服務（如 DataSimulator, DataIngestor, DB, TimeServer 等）。
* 內部服務間（relay → core services, db, redis 等）採無認證設計，簡化內網流程。
* 作為安全閘道，隔離外部威脅並利於日後微服務擴充。

---

## 實作描述

* Command 端所有操作均透過 alias 或腳本（如 `docker exec -it daemon_container szcli ...`）實際執行於專用 container，確保環境一致與依賴隔離。
* Relay 部署於 K3Han，接收 CLI 請求後依據指令類型分派到適合的後端服務。

  * 對外請求（如登入驗證）會強制經過 Google OAuth 安全驗證。
  * 對內 RESTful 請求（資料模擬、查詢、資料庫操作等）則透過 relay 快速協調並執行。
* Relay 透過 FastAPI 實現，並整合 SQLAlchemy 處理資料庫存取、requests 套件與各微服務溝通。

---

## 互動流程說明

### CLI 操作資料庫（以初始化為例）


1. 使用者執行 `szcli db init`（實際為 docker exec -it daemon_container szcli db init）

2. CLI relay 於 K3Han 接收 RESTful 請求，先通過 OAuth 驗證

3. relay 呼叫內部 SQLAlchemy 邏輯，對 PostgreSQL 執行初始化

4. 結果回傳 CLI，成功時回應 success，錯誤則回傳結構化錯誤訊息


### CLI 與 core services 互動（以模擬資料為例）


1. 使用者執行 `szcli dataflow simulate <date>`（或日期區間）

2. CLI relay 收到指令與 OAuth 驗證後，轉發至 DataSimulator 微服務

3. DataSimulator 根據日期參數產生模擬資料並寫入資料庫

4. 結果回傳 CLI，顯示 success 或異常訊息


---

## CLI 全流程圖（示意）

```
User (shell)
   │
   ▼
[docker exec into daemon container]
   │
   ▼
szcli (parsing command)
   │
   ├─── if login:
   │         │
   │         ▼
   │    [OAuth authentication]
   │         │
   │         ▼
   │  Relay API (K3Han FastAPI)
   │         │
   │         ▼
   │   [Google OAuth verification]
   │         │
   │         ▼
   │   [Command type dispatch]
   │         │
   │         ├── db init ─────────────► Database Init (SQLAlchemy → PostgreSQL) ──────
   │         │                                                                        │
   │         │                                                                        │
   │         │                                                                        │
   │         │                                                                        │
   │         │                                                                        │
   │         └── dataflow simulate ───► DataSimulator microservice                    │
   │                                       │                                          │
   │                                       │                                          ▼
   │                                        ─────────────────────────────────────► [Result]
   │                                                                                  │   │                                                                                  │                                     
   ▼                                                                                  ▼ 
                                  [Return result to CLI]
```

---

## 🧭 推薦閱讀順序

1. [service.md](safechord.safezone.service.md)：SafeZone 各核心服務總覽，理解 CLI 指令背後的業務邏輯
2. [cli.reference.md](safechord.safezone.toolkit.cli.reference.md)：完整 CLI 指令集、用法與範例

---