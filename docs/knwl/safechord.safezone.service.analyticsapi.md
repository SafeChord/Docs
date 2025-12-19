---
title: "SafeZone Service: AnalyticsAPI - Data Analysis & Query"
doc_id: safechord.safezone.service.analyticsapi
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16" 
summary: "本文檔闡述 SafeZoneAnalyticsAPI 服務，該服務通過 RESTful API 提供高效的疫情數據分析與查詢功能。它支持基於地區、時間範圍和案例類型的多條件查詢，能夠返回案例計數或按人口比例計算的結構化分析結果。"
keywords:
  - SafeZone
  - SafeZoneAnalyticsAPI
  - data analysis
  - data query
  - API service
  - RESTful API
  - epidemic data
  - case data
  - population ratio
  - multi-conditional query
  - data pipeline 
  - SafeChord
logical_path: "SafeChord.SafeZone.Service.AnalyticsAPI"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.service.dashboard.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python
  - FastAPI
  - Pydantic
  - PostgreSQL
  - Docker
---
# AnalyticsAPI

## **服務名稱與描述**

- **名稱**：SafeZoneAnalyticsAPI。
- **描述**：提供高效的數據分析服務，通過定制化的查詢和數據處理，支持多種數據類型的需求，包括案例數據和人口比例分析。

---

## **服務需求**

### **API 功能需求**

1. **查詢功能**
    - **功能描述**：支持多條件數據查詢，返回結構化的分析結果。
    - **需求細節**：
        - 查詢條件包括地區（國家、城市、地區）、時間範圍和案例類型。
        - 時間區間支持 1、3、7、14、30 天。
        - 不允許某些區域層級與時間範圍的無效組合，需根據前端需求限制。
        - 查詢結果應包含統計數據（如病例總數、增長率）。
2. **數據類型支持**
    - **功能描述**：根據查詢條件提供不同類型的數據視圖。
    - **需求細節**：
        - 提供案例個數或按人口比例的數據。
        - 人口比例 = 案例個數 / 該區域總人口數，需提供精確的計算支持。

---

## **架構設計**

此服務的核心模組包括：

- **API 層**：處理用戶請求，將其路由到相應的服務。
- **數據查詢模組**：負責根據查詢條件檢索數據並校驗結果。
- **分析管道**：執行數據處理，包括統計和人口比例計算。
- **異常處理**：確保在輸入無效或服務錯誤時，提供清晰的錯誤信息和響應碼。

---

## 目錄架構

```
SafeZoneAnalyticsAPI/
├── app/
│   ├── api/                   # 定義 API 端點和數據模式
│   │   ├── endpoints.py       # API 端點
│   │   ├── schemas.py         # 數據結構和驗證
│   ├── config/                # 配置文件（如日誌、環境設置）
│   │   ├── logger.py          # 日誌配置
│   │   ├── settings.py        # 環境設置與配置
│   ├── exceptions/            # 異常處理
│   │   ├── custom.py          # 自定義異常
│   │   ├── handlers.py        # 異常處理程序
│   ├── pipeline/              # 數據處理和分析管道
│   │   ├── orchestrator.py    # 分析流程調度
│   │   ├── query_service.py   # 查詢服務邏輯
│   ├── main.py                # 主應用程序入口
├── environments/              # 環境配置
│   ├── dev/                   # 開發環境
│   ├── prod/                  # 生產環境
│   ├── shared/                # 共用配置
│   ├── test/                  # 測試環境
│   │   ├── data/              # 測試數據
│   │   │   ├── test_data.csv
│   │   ├── db/                # 測試數據庫
│   │   │   ├── test.db
│   │   ├── tests/             # 測試案例和腳本
│   │   │   ├── cases/         # 測試用例
│   │   │   │   ├── test_integration.json
│   │   │   │   ├── test_query_service.json
│   │   │   ├── integration_test/ # 整合測試腳本
│   │   │   │   ├── test_main.py
│   │   │   ├── unit_test/     # 單元測試腳本
│   │   │   │   ├── test_query.py
├── .env                         # 環境變數配置
├── Dockerfile.test              # 測試環境 Docker 配置
├── requirements.txt             # 項目依賴項
└── README.md                    # 項目說明文檔

```

---

## 使用範例

以下是 SafeZone Analytics API 的主要端點及其使用範例：

### 1. **區域數據查詢**

**端點**:

```
GET /cases/region

```

**請求參數**:

| 參數名稱 | 類型 | 必填 | 描述 |
| --- | --- | --- | --- |
| `now` | `string` | 是 | 當前日期，格式為 `YYYY-MM-DD` |
| `interval` | `int` | 是 | 查詢的日期範圍天數，例如 `7` |
| `city` | `string` | 是 | 城市名稱 |
| `region` | `string` | 是 | 區域名稱 |
| `ratio` | `bool` | 否 | 是否返回人口比例數據 |

**回應範例**:

```json
{
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-01-07",
        "city": "Taipei",
        "region": "Xinyi",
        "aggregated_cases": 150
    },
    "message": "Data returned successfully",
    "detail": "Data returned successfully for dates 2023-01-01 ~ 2023-01-07.",
    "success": true
}

```

### 2. **城市數據查詢**

**端點**:

```
GET /cases/city

```

**請求參數**:

| 參數名稱 | 類型 | 必填 | 描述 |
| --- | --- | --- | --- |
| `now` | `string` | 是 | 當前日期，格式為 `YYYY-MM-DD` |
| `interval` | `int` | 是 | 查詢的日期範圍天數，例如 `7` |
| `city` | `string` | 是 | 城市名稱 |
| `ratio` | `bool` | 否 | 是否返回人口比例數據 |

**回應範例**:

```json
{
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-01-07",
        "city": "Taipei",
        "aggregated_cases": 500
    },
    "message": "Data returned successfully",
    "detail": "Data returned successfully for dates 2023-01-01 ~ 2023-01-07.",
    "success": true
}

```

### 3. **全國數據查詢**

**端點**:

```
GET /cases/national

```

**請求參數**:

| 參數名稱 | 類型 | 必填 | 描述 |
| --- | --- | --- | --- |
| `now` | `string` | 是 | 當前日期，格式為 `YYYY-MM-DD` |
| `interval` | `int` | 是 | 查詢的日期範圍天數，例如 `7` |

**回應範例**:

```json
{
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-01-07",
        "aggregated_cases": 10000
    },
    "message": "Data returned successfully",
    "detail": "Data returned successfully for dates 2023-01-01 ~ 2023-01-07.",
    "success": true
}

```

---

## 本地測試

**單元測試（Unit Test）**：

- query_service
    - TestCase：
        
        
        | 測試項目 | 測試模組 | 測試描述 | 預期結果 |
        | --- | --- | --- | --- |
        | query region aggregated cases: success | `query_service_region_test` | 在參數正確的場景下，查詢指定區域的累積案例 | 返回正確的案例個數 |
        | query region with invalid region | `query_service_region_test` | 提供無效的區域名稱進行查詢 | 拋出 `InvalidTaiwanRegionException` |
        | query region with invalid city | `query_service_region_test` | 提供無效的城市名稱進行查詢 | 拋出 `InvalidTaiwanCityException` |
        | query city aggregated cases: success | `query_service_city_test` | 在參數正確的場景下，查詢指定城市的累積案例 | 返回正確的案例個數 |
        | query city with invalid city | `query_service_city_test` | 提供無效的城市名稱進行查詢 | 拋出 `InvalidTaiwanCityException` |
        | query national aggregated cases: success | `query_service_national_test` | 在參數正確的場景下，查詢全國累積案例 | 返回正確的案例個數 |
        | query region cases with ratio: success | `query_service_region_test` | 查詢區域案例數據，返回人口比例 | 返回正確的人口比例 |
        | query region cases with date range out of bounds | `query_service_region_test` | 查詢超出有效日期範圍的區域案例 | 返回 0 案例 |
    - 驗證待辦清單：
        - [x]  query region aggregated cases: success
        - [x]  query region with invalid region
        - [x]  query region with invalid city
        - [x]  query city aggregated cases: success
        - [x]  query city with invalid city
        - [x]  query national aggregated cases: success
        - [x]  query region cases with ratio: success
        - [x]  query region cases with date range out of bounds

整合測試**（**Integration Test**）**：

- TestCase：
    
    
    | 測試項目 | 測試端點 | 測試描述 | 預期結果 |
    | --- | --- | --- | --- |
    | Request to /cases/region in correct scenario | `/cases/region` | 測試正確區域參數的查詢結果 | 返回狀態碼 200 和正確的累積案例數 |
    | Request to /cases/region with ratio in correct scenario | `/cases/region` | 測試區域查詢時返回人口比例的正確性 | 返回狀態碼 200 和正確的人口比例 |
    | Request to /cases/region with invalid city | `/cases/region` | 測試無效城市名稱的處理 | 返回狀態碼 422 和詳細的錯誤信息 |
    | Request to /cases/region with region not belonging to city | `/cases/region` | 測試區域與城市不匹配的場景 | 返回狀態碼 422 和詳細的錯誤信息 |
    | Request to /cases/region no data found | `/cases/region` | 測試無數據的日期範圍查詢結果 | 返回狀態碼 200 和空案例結果 |
    | Request to /cases/city in correct scenario | `/cases/city` | 測試正確城市參數的查詢結果 | 返回狀態碼 200 和正確的累積案例數 |
    | Request to /cases/city with invalid city | `/cases/city` | 測試無效城市名稱的處理 | 返回狀態碼 422 和詳細的錯誤信息 |
    | Request to /cases/city with invalid now value | `/cases/city` | 測試未來日期的處理 | 返回狀態碼 200 和空案例結果 |
    | Request to /cases/national in correct scenario | `/cases/national` | 測試全國數據的查詢結果 | 返回狀態碼 200 和正確的累積案例數 |
    | Request to /cases/national with invalid now value | `/cases/national` | 測試未來日期的處理 | 返回狀態碼 200 和空案例結果 |
- 驗證待辦清單：
    - [x]  Request to /cases/region in correct scenario
    - [x]  Request to /cases/region with ratio in correct scenario
    - [x]  Request to /cases/region with invalid city
    - [x]  Request to /cases/region with region not belonging to city
    - [x]  Request to /cases/region no data found
    - [x]  Request to /cases/city in correct scenario
    - [x]  Request to /cases/city with invalid city
    - [x]  Request to /cases/city with invalid now value
    - [x]  Request to /cases/national in correct scenario
    - [x]  Request to /cases/national with invalid now value