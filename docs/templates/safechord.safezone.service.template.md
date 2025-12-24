---
title: "Service: [Service Name]"
doc_id: safechord.safezone.service.[name]
version: "0.1.0"
status: draft
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "YYYY-MM-DD"
summary: "[一句話描述該服務的核心職責、在資料流中的位置，以及關鍵技術特性 (e.g. AsyncIO, Kafka Consumer)]"
keywords:
  - [keyword1]
  - [keyword2]
logical_path: "SafeChord.SafeZone.Service.[Name]"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - [Language/Framework]
  - [Key Library]
---

# [Service Name] (v[Version])

## 📌 服務定位
[詳細描述服務的功能目標與運作模式]
*   **角色**: [Producer / Consumer / Aggregator / Gateway]
*   **特性**: [Stateless / Stateful / Event-Driven / Passive-Triggered]

---

## 🛠️ 核心規格 (Specifications)

### 1. 介面與資料契約
本服務遵循統一的資料契約。AI Agent 應優先參考實體程式碼以獲取最新定義。
*   **Data Models**: [連結至 Pydantic Model 或 Protobuf 定義]
*   **API/Topic**: [描述 REST Endpoints 或 Kafka Topics]

### 2. 外部依賴與控制 (Dependencies & Control)
> 定義服務的啟動鏈與依賴鏈。
*   **Control Plane (Trigger)**: [誰負責喚醒或調度此服務？]
    *   *Rationale*: [為什麼這樣設計？例如：為了精確控制測試時序]
*   **Upstream**: [資料來源]
*   **Downstream**: [資料去向]

---

## 🧪 行為驗證 (Behavior Verification)

本服務採用 **Spec-as-Code** 策略。業務邏輯的正確性由以下規格檔定義：

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **邏輯單元** | `test/cases/test_logic.json` | [描述] |
| **整合測試** | `test/cases/test_integration.json` | [描述] |

---

## 🧩 設計權衡 (Design Trade-offs)
> 紀錄關鍵的架構決策 (ADR)。這是展示專業深度與引導 AI 實作的核心區域。

### 1. [決策點名稱]
*   **Why**: [選擇此方案的核心原因]
*   **Trade-off**: [犧牲了什麼 (例如：開發便利性)，換取了什麼 (例如：效能/可控性)？]

---

## 🚀 部署與維運
*   **Docker Image**: `[image-name]`
*   **環境變數**: 參考 `[path_to_env_example]`
*   **Health Check**: `[endpoint]`