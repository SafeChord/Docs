---
title: "SafeZone: Application Services & Data Flow Architecture"
doc_id: safechord.safezone.service
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16" 
summary: "本文檔詳細描述 SafeZone 應用程式的內部服務組件、各模組的角色職責，以及它們之間如何協同工作以實現完整的數據處理流程——從數據模擬產生、事件注入、數據庫存儲、API 查詢到最終的圖表呈現。"
keywords:
  - SafeZone
  - service architecture
  - microservices
  - data flow
  - application components
  - data simulation 
  - data ingestion 
  - analytics API 
  - dashboard service 
  - CLI service 
  - API design
  - SafeChord
logical_path: "SafeChord.SafeZone.Service"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.service.datasimulator.md" 
  - "safechord.safezone.service.dataingestor.md"
  - "safechord.safezone.service.analyticsapi.md"
  - "safechord.safezone.service.dashboard.md"
  - "safechord.safezone.service.cli.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Python
  - FastAPI
  - Plotly Dash 
  - PostgreSQL
  - Redis
---
# SafeZone-Service

> SafeZone 的每一個模組，就像資料旅程中的一位角色。
> 
> 
> 有的負責製造，有的負責轉送，有的負責解讀與展現——它們各司其職，共同構築一條清晰的資料流線。
> 

---

## 🧪 各模組角色介紹

- coviddatasimulator：故事的起點。產生模擬資料，模擬各種災情數據。
- coviddataingestor：資料搬運工。接收模擬資料，進行結構驗證後寫入 DB。
- safezoneanalyticsapi：資料解譯者。提供資料查詢 API，讓前端或外部系統可靈活取得時間序列資訊。
- safezonedashboard：可視化舞台。透過 Plotly Dash 呈現疫情曲線圖與即時統計。
- safezonecli：指令橋接者。作為登入、token 驗證與 CLI 指令發送的中介，串起使用者與整個系統。

---

## 🖼 資料流動圖與流程階段

👇 SafeZone 模組間的資料流動如下圖所示：

資料流動步驟簡述：

1. **資料產生**：使用者透過 CLI 登入並下指令給 simulator 觸發模擬事件。
2. **事件注入**：simulator 將模擬絲料傳給 Ingestor， Ingestor 驗證並寫入資料庫。
3. **資料查詢**：dashboard 透過 analytics_api 查詢統計資料。
4. **圖表呈現**：dashboard 將結果視覺化，顯示資料走勢與異常點。

---

## 🧭 推薦閱讀順序

建議從下列順序進入，掌握各模組間的串接邏輯：

1. [coviddatasimulator.md](safechord.safezone.service.md)：了解如何啟動模擬流程
2. [coviddataingestor.md](safechord.safezone.service.md)：掌握資料寫入的結構驗證
3. [safezoneanalyticsapi.md](safechord.safezone.service.md)：熟悉查詢設計與資料來源邏輯
4. [safezonedashboard.md](safechord.safezone.service.md) ：觀察圖表邏輯如何呈現後端資料
5. [safezonecli.md](safechord.safezone.service.md)：最後補上使用者登入與驗證橋接層