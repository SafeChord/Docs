---
title: "Service: [Service Name]"
doc_id: safechord.safezone.service.[name]
doc_version: [Document Version]
app_version: [Target Application Version]
status: draft
authors:
 - [Author Name]
last_updated: "YYYY-MM-DD"
summary: "[一句話描述：核心職責、資料流位置、技術特性]"
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

> ⚠️ **Scope Warning**: This template is **STRICTLY** for microservices within `safechord.safezone.service.*`. Do not use for generic infrastructure or libraries.
> *繼承自 `archetype.blueprint.md`，並針對容器化服務進行特化。*

## 1. 職責與定位 (Responsibility)
*(必選)*
*   **角色**: [Producer / Consumer / Aggregator / Gateway]
*   **特性**: [Stateless / Stateful / Event-Driven / Passive-Triggered]
*   **核心目標**: [解決了什麼業務問題？]

## 2. 檔案結構 (File Structure)
*(必選 - 分層展開)*
```text
/services/[service-name]
├── src/
│   ├── main.py           # Entry Point
│   └── api/              # Route Definitions
├── tests/                # Unit/Integration Tests
├── Dockerfile
└── requirements.txt
```

## 3. 接口規範 (Interfaces)
*(必選)*

### 資料契約 (Contracts)
*   **Data Models**: [連結至 Pydantic Model 或 Protobuf 定義]

### 輸入 (Ingress)
> 定義服務如何接收外部訊號。若為 API 服務則列出 Endpoints；若為 Worker 則列出 Topic。
*   **Type**: [API | Worker Consumer]
*   **Source**: `POST /endpoint` OR `Topic: topic-name`

### 輸出 (Egress)
*   **Dest**: `Topic: topic-name` (Producer) OR `DB: TableName`

## 4. 依賴與控制 (Dependencies & Control)
*(必選)*

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Control Plane** | Trigger | [誰負責喚醒？ e.g., CLI] |
| **Upstream** | Source | [資料來源] |
| **Downstream** | Sink | [資料去向] |

## 5. 行為驗證 (Behavior Verification)
*(必選 - Spec-as-Code)*
本服務採用 JSON Test Cases 作為邏輯真理來源。

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **邏輯單元** | `test/cases/test_logic.json` | [描述核心算法驗證點] |
| **整合測試** | `test/cases/test_integration.json` | [描述邊界驗證點] |

## 6. 實作決策 (Implementation Decisions)
*(可選 - Local Trade-offs)*
*   **[決策點名稱]**:
    *   **Why**: [原因]
    *   **Trade-off**: [權衡]

## 7. 部署與維運 (Deployment & Ops)
*(必選)*
*   **Docker Image**: `safezone-[service-name]`
*   **Health Check**: `GET /health` (或 Worker 的 Liveness Probe 機制)
*   **Configuration**:
    *   詳細變數請參閱代碼庫中的 [.env.example]([link_to_env_example])。
    *   **Key Settings**:
        *   `MODE`: [Critical Flag] - [Description]