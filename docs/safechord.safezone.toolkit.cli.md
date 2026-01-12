---
title: 'Toolkit: SafeZone CLI (szcli)'
doc_id: safechord.safezone.toolkit.cli
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: '2026-01-08'
summary: SafeZone CLI (szcli) 是系統的指揮官與控制台。採用 Client-Relay 架構，Client 端提供 Typer CLI
  介面，Relay 端則作為 K8s 內部的受信任 Gateway，負責執行特權操作並驗證 Google OAuth 憑證。
keywords:
  - SafeZone CLI
  - szcli
  - Client-Relay Pattern
  - Typer
  - FastAPI
  - Headless OAuth
logical_path: SafeChord.SafeZone.Toolkit.CLI
related_docs:
  - safechord.safezone.toolkit.cli.reference.md
  - safechord.safezone.md
  - safechord.security.md
parent_doc: safechord.safezone.toolkit
archetype: blueprint
code_paths:
  - SafeZone/toolkit/cli
tech_stack:
  - Python 3.13
  - Typer (CLI Framework)
  - FastAPI (Relay Server)
  - Google OAuth 2.0 (Headless)
  - Rich (Terminal UI)
doc_version: 0.2.0
app_version: 0.2.1
---

# SafeZone CLI (Toolkit Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `szcli` toolkit.
> *繼承自 `archetype.blueprint.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Orchestrator / Gateway / Ops Tool
*   **特性**: Client-Relay Architecture, Stateful Auth (Local Token Cache)
*   **核心目標**:
    *   **統一入口**: 作為系統的單一控制點，屏蔽 K8s 內部的複雜連線資訊。
    *   **安全邊界**: 透過 Relay 模式，允許外部使用者（開發者）在不直接暴露 DB/Redis 端口的情況下，執行受控的維運指令。
    *   **驗證驅動**: 負責觸發並驗證 End-to-End 資料流（Smoke Test 核心組件）。

## 2. 設計哲學 (Design Philosophy)
> **"Utility First, Purity Second"**

本工具性質屬於 **開發輔助 (Dev Enabler)**，其開發模式具有高度的 **探索性 (Exploratory)**。
*   **動態需求**: 功能常因應臨時的 Debug 需求或架構調整而新增（例如臨時需要重置 Time Server）。
*   **權衡 (Trade-off)**: 我們選擇 **犧牲單元測試覆蓋率**，以換取功能的即時交付。
*   **緩解 (Mitigation)**: 不強制 TDD，而是依賴 **Smoke Test** 覆蓋最關鍵的 Happy Path，確保核心資料流操作正常。

## 3. 檔案結構 (File Structure)
專案結構明確劃分為 `command` (Client) 與 `relay` (Server) 兩大部分。

```text
SafeZone/toolkit/cli/
├── command/                      # [Client] Typer App (Run on Host/Bastion)
│   ├── main.py                   # Entry Point & Command Registry
│   ├── bin/
│   │   ├── client.py             # HTTP Client with Auto-Refresh Auth
│   │   └── command.py            # Command Decorators
│   ├── scripts/                  # [Macros] 各環境初始化與資料預熱腳本 (init, seed)
│   └── config/settings.py        # Client Config (Secrets from Env)
├── relay/                        # [Server] FastAPI App (Run inside Cluster)
│   ├── main.py                   # Entry Point
│   ├── api/endpoints.py          # REST Interface & RBAC Logic
│   ├── bin/                      # Business Logic Helpers
│   │   ├── db_helper.py          # SQLAlchemy Ops
│   │   └── time_helper.py        # Redis Config Ops
│   └── config/settings.py        # Server Config (Secrets from Env)
└── Dockerfile                    # Multi-stage build for both components
```

## 4. 接口規範 (Interfaces)

### 輸入 (Ingress)
*   **User Interface (Client)**:
    *   `szcli dataflow {simulate, verify}`
    *   `szcli system {time, health}`
    *   `szcli db {init, reset}`
    *   **詳細操作範式**: 請參閱 **[CLI Instruction Set (szcli)](safechord.safezone.toolkit.cli.reference.md)**。
*   **API Interface (Relay)**:
    *   **Endpoint**: `POST /dataflow/simulate`, `GET /system/health`, etc.
    *   **Auth**: `Authorization: Bearer <ID_TOKEN>` (Google OAuth2).

### 輸出 (Egress)
*   **Client Output**: 使用 `Rich` 函式庫渲染的格式化終端輸出 (JSON/Table)。
*   **Relay Actions**:
    *   **Database**: 直接連線 PostgreSQL 執行 DDL/DML。
    *   **Redis**: 寫入 Time Server 配置或讀取 Cache 狀態。
    *   **Internal API**: 呼叫 `pandemic-simulator` 或 `analytics-api`。

## 5. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Google Identity** | Auth Provider | Relay 依賴 Google Public Keys 驗證 Token 簽章；Client 依賴 Token Endpoint 換取 ID Token。 |
| **Internal Services** | Downstream | Relay 需能解析並連線至叢集內的 DB, Redis, Simulator Service。 |
| **Environment** | Configuration | Client 必須注入 `REFRESH_TOKEN` 才能運作 (Headless Mode)。 |

## 6. 安全機制 (Security Architecture)

### Headless OAuth 2.0 Flow
鑑於 CLI 通常在 CI Runner 或 Docker 容器中執行，我們棄用了互動式登入，改採 **Refresh Token** 機制。

1.  **Token Injection**: `REFRESH_TOKEN` 作為環境變數注入 Client 容器。
2.  **Auto-Refresh**: `bin/client.py` 偵測到 Token 過期或不存在時，自動向 Google 換取新的 `ID_TOKEN`。
3.  **Relay Verification**:
    *   **Signature**: 驗證 Token 是否由 Google 簽發。
    *   **RBAC**: 解析 Token 中的 `email`，並比對 `relay/roles.example.yml` 中的白名單 (Admin/User)。

## 7. 行為驗證 (Behavior Verification)

> **⚠️ Note on Quality Assurance**:
> 本工具定位為「快速開發原型 (Rapid Prototype)」，優先追求開發速度與維運便利性。目前 **未實作** 完整的單元測試 (TDD)，主要依賴 **手動驗證** 與 **全系統煙霧測試**。

| 範疇 | 驗證策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **Auth Flow** | `Manual` | 移除 `TOKEN_FILE` 後執行指令，觀察 Log 是否顯示 `Refreshing authentication token...` 且指令執行成功。 |
| **RBAC** | `Manual` | 使用非白名單 Email 的 Token 執行指令，確認 Relay 回傳 `403 Forbidden`。 |
| **Dataflow** | `Smoke Test` | 依賴 `scripts/smoke-test.sh` 的 E2E 流程：`simulate` -> `verify` (返回值為 0) -> `wait` -> `verify` (有返回值)。 |

## 8. 部署與配置 (Deployment & Config)

*   **Docker Image**: `safezone-cli` (Client) / `safezone-cli-relay` (Server)
*   **Configuration**:
    *   **Client Env**: `RELAY_URL`, `CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`.
    *   **Relay Env**: `DB_URL`, `REDIS_HOST`, `ROLE_FILE`.

## 9. 技術債與未來展望 (Tech Debt & Roadmap)

雖然本工具採取 MVA 策略，但隨著系統演進，以下關鍵組件將優先納入修復計畫：

*   **Security Hardening (資安補強)**:
    *   **Observation**: 目前 Relay 的 RBAC 邏輯 (`endpoints.py`) 缺乏測試保護，若修改錯誤可能導致權限旁路。
    *   **Action**: 開立 **[Issue #25: Hardening CLI Relay Security](https://github.com/SafeChord/SafeZone/issues/25)**，針對 Auth Middleware 補上嚴格的單元測試。
*   **Legacy Cleanup**:
    *   **Observation**: 代碼庫中仍殘留舊版互動式 Login 邏輯。
    *   **Action**: 開立 **[Issue #26: Cleanup Legacy Auth Code](https://github.com/SafeChord/SafeZone/issues/26)**，規劃在下一次重構中移除 `client.py` 中的 Legacy Auth Code。