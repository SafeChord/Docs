---
title: "SafeZone Toolkit: CLI (szcli)"
doc_id: safechord.safezone.toolkit.cli
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-28"
summary: "SafeZone CLI (szcli) 是系統的指揮官與控制台。它整合了 Typer (Client) 與 FastAPI (Relay)，提供統一的介面來觸發資料流模擬、執行資料庫維運、控制系統時間以及執行全系統健康檢查。"
keywords:
  - SafeZone CLI
  - szcli
  - Typer
  - Relay Pattern
  - Google OAuth
  - System Control
logical_path: "SafeChord.SafeZone.Toolkit.CLI"
related_docs:
  - "safechord.safezone.service.md"
  - "safechord.safezone.toolkit.cli.reference.md"
  - "safechord.safezone.toolkit.timeserver.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Python (Typer)
  - FastAPI (Relay)
  - Google OAuth 2.0
  - Rich (UI)
---

# SafeZone CLI (v0.2.1)

## 📌 工具定位
`szcli` 是系統的 **主要進入點 (Primary Entrypoint)**。
*   **架構模式**: **Client-Relay Pattern**。
    *   **Client (Typer)**: 運行於使用者的 Shell 環境（或 Bastion Host），負責參數解析與 UI 呈現。
    *   **Relay (FastAPI)**: 運行於 K3s 叢集內部，作為受信任的 Gateway，擁有對內部服務 (DB, Redis, API) 的直接存取權。

---

## 🛠️ 核心功能模組

### 1. Dataflow Control (`szcli dataflow`)
負責驅動與驗證資料管線。
*   **Simulate**: 觸發 [Pandemic Simulator](safechord.safezone.service.pandemicsimulator.md)。
    *   *Side Effect*: 每次模擬觸發後，Relay 會自動重置 Redis 中的 **Cache Version** (`current_cache_version`)，強制所有 Analytics API 的快取失效，確保前端能看到最新的模擬數據。
*   **Verify**: 呼叫 [Analytics API](safechord.safezone.service.analyticsapi.md) 檢查數據是否正確聚合。

### 2. System Control (`szcli system`)
*   **Time**: 呼叫 [Time Server](safechord.safezone.toolkit.timeserver.md) 控制時間流速。
*   **Health**: 提供 `target="all"` 選項，並行檢查所有微服務 (Ingestor, API, Dashboard, DB, Redis) 的健康狀態。

### 3. Database Ops (`szcli db`)
*   **Init/Reset**: 透過 SQLAlchemy 直接對 PostgreSQL 執行 Schema 初始化與清空操作。

---

## 🔐 安全機制 (Security)

### Google OAuth 2.0
所有針對 Relay 的指令請求，皆需攜帶有效的 `Bearer Token`。
1.  **Login**: 使用者執行 `szcli login`，CLI 啟動本地 Server 完成 OAuth 流程並取得 Token。
2.  **Verify**: Relay 接收請求時，驗證 Token 是否由 Google 簽發，並檢查 Email 是否在 `ROLE_MAP` 白名單中。
3.  **RBAC**: 
    *   `admin`: 允許執行 `db.reset`, `time.set`, `dataflow.simulate` 等破壞性指令。
    *   `user`: 僅允許執行 `verify`, `health`, `time.now` 等唯讀指令。

---

## 🚀 部署與使用
*   **Client**: 通常透過 `alias` 或 Docker Wrapper 執行：
    ```bash
    alias szcli='docker exec -it safezone-cli szcli'
    ```
*   **Relay**: 部署為 K8s Service (`cli-relay`)。
