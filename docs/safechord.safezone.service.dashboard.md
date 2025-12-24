---
title: "SafeZone Service: Dashboard - Safezone Data Visualization" 
doc_id: safechord.safezone.service.dashboard
version: "0.1.0" 
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16" 
summary: "本文檔詳細描述 SafeZone 的 Dashboard 服務，其核心功能是通過直觀的數據可視化（包括交互式地圖和趨勢圖表）展示 COVID-19 疫情的動態變化與區域分布風險。內容涵蓋服務需求、用戶指引、視覺化版面設計、目錄架構及本地測試案例。"
keywords:
  - SafeZone
  - Dashboard
  - data visualization
  - COVID-19
  - epidemic data
  - interactive map
  - trend chart
  - risk map
  - frontend service 
  - user interface (UI)
  - Plotly Dash 
  - service requirements
  - user guide
  - testing 
  - SafeChord
logical_path: "SafeChord.SafeZone.Service.Dashboard"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.deployment.safezone-ui.md" 
  - "safechord.safezone.service.analyticsapi.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Plotly Dash
  - Python
  - Docker
---
# SafeZoneDashboard

## **服務名稱與描述**

- **名稱**：SafeZoneDashboard。
- **描述**：通過直觀的數據可視化，展示疫情的動態變化與區域分布風險，幫助用戶快速了解疫情狀況，並進行簡單的數據分析。

---

## **服務需求**

### **頁面非互動展示內容**

1. **疫情數據總覽**
    - **功能描述**：展示全台當日、近七日新增病例的數據。
    - **需求細節**：
        - 顯示全台「新增病例數」。
        - 數據應以卡片樣式呈現。
2. **最快案例成長卡**
    - **功能描述**：展示近七日案例成長最快的城市前十名。
    - **需求細節**：
        - 資料細粒度只到城市。

### **頁面互動式展示內容**

- **可互動項目**
    
    **日期區間選擇**
    
    - **功能描述**：透過時間選擇按鈕，選擇一個日期區間，對應展示該區間內的疫情數據。
    - **需求細節**：
        - 預設可選範圍：最近 3 天、7 天、14 天、30 天。
        - 顯示用戶選定的具體日期區間（如「2023-03-01 至 2023-03-14」）。
    
    **展示方式選擇**
    
    - **功能描述**：提供兩種方式：按案例個數展示風險色塊、按人口比例展示風險色塊。
    - **需求細節**：
        - 不另提供風險計算方式，避免冒犯公衛專業。
    
    **地圖互動**
    
    - **功能描述**：可以點擊地圖區域切換地圖區域。
    - **需求細節**：
        - 在台地圖下，可以點擊城市區域轉移到該城市內區域的地圖。
        - 在區域地圖下，可以返回全台地圖。
- **展示內容**
    - **各區案例數展示（以風險色塊表示）**
        - **功能描述**：用地圖展示選定日期區間內每個鄉鎮區的病例數或人口比例，並通過色塊表示風險等級。
        - **需求細節**：
            - 基於病例數進行風險著色（利用紅色梯度展示風險）。
            - 提供滑鼠懸停功能，顯示詳細數據（如病例數、風險等級）。

---

## **用戶指引**

SafeZoneDashboard 的使用流程如下：

1. **篩選日期區間**：使用日期篩選器選擇要查看的時間範圍（如最近 7 天）。
2. **查看數據總覽**：透過總覽卡片查看當前的新增病例數、累計病例數等重要數據。
3. **分析趨勢圖表**：檢視疫情走勢，並切換展示模式（如按案例數或人口比例）。
4. **使用互動式地圖**：點擊地圖中的區域以進一步查看更詳細的疫情信息。

---

## **視覺化版面設計**

![](image.png)

此設計包含以下模組：

- **數據總覽卡片**：顯示全台或特定區域的關鍵數據。
- **趨勢圖表**：展示疫情在選定日期範圍內的變化趨勢。
- **交互式地圖**：以地圖可視化的方式展示疫情風險分布。

---

## 目錄架構：

```notion
SafeZoneDashboard/
├── app/
│   ├── callbacks/           # Callbacks for handling user interactions and data updates
│   │   ├── button_callbacks.py  # Button-specific interactions
│   │   ├── register.py          # Registration-related callbacks
│   │   └── risk_map_callbacks.py # Callbacks for risk map updates
│   ├── components/          # Modular Dash components for reusability and modularity
│   │   ├── basic_ui.py       # Core UI elements
│   │   ├── button.py         # Button components
│   │   ├── card.py           # Card components for summaries
│   │   ├── map_chart.py      # Map visualization component
│   │   └── trend_chart.py    # Trend chart visualization component
│   ├── config/              # Configuration files for logging and settings
│   │   ├── logger.py         # Logging configuration
│   │   ├── settings.py       # General settings and environment variables
│   ├── exceptions/          # Custom exception handling for the app
│   │   ├── custom.py         # User-defined exceptions
│   │   ├── handler.py        # Exception handlers
│   ├── layout/              # Dashboard layout definition
│   │   ├── dashboard_layout.py # Main dashboard layout structure
│   ├── services/            # Backend services and API integrations
│   │   ├── api_caller.py     # Wrapper for calling external APIs
│   │   ├── update_cases.py   # Logic for updating case data
│   ├── validators/          # Validation schemas and data integrity checks
│   │   ├── schemas.py        # JSON schemas for validation
├── environments/           # Environment configurations
│   ├── dev/                # Development environment
│   │   ├── Dockerfile.dev   # Docker configuration for development
│   │   ├── requirements.txt # Dependencies for development
│   │   └── .env             # Environment variables for development
│   ├── prod/               # Production environment
│   │   ├── Dockerfile.prod  # Docker configuration for production
│   │   ├── requirements.txt # Dependencies for production
│   │   └── .env             # Environment variables for production
│   ├── test/               # Testing environment
│   │   ├── Dockerfile.test  # Docker configuration for testing
│   │   ├── requirements.txt # Dependencies for testing
│   │   ├── .env             # Environment variables for testing
│   │   ├── tests/           # Test scripts
│   │   │   ├── unit_test/   # Unit tests
│   │   │   │   ├── test_get_city_data.py
│   │   │   │   ├── test_get_national_case.py
│   │   │   │   ├── test_get_region_data.py
│   │   │   ├── integration_test/ # Integration tests
│   │   │   │   ├── test.py       # Integration testing script
│   │   │   ├── test_ui/        # UI testing scripts
│   │   │   │   ├── test.py
│   │   ├── cases/            # Test case data
│   │   │   ├── templates.json # Template data for testing
│   │   │   ├── mock_data.json # Mock data for manual tests
│   │   │   ├── test_services/ # Service test data
│   │   │   │   ├── get_city_data/
│   │   │   │   │   ├── cases_resp_error.json
│   │   │   │   │   ├── cases_success.json
│   │   │   │   ├── get_national_case/
│   │   │   │   │   ├── cases_network_error.json
│   │   │   │   │   ├── cases_resp_error.json
│   │   │   │   │   ├── cases_success.json
│   │   │   │   ├── get_region_data/
│   │   │   │   │   ├── cases_params_error.json
│   │   │   │   │   ├── cases_success.json
├── Dockerfile            # Production Docker configuration
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation

```

---

## 本地測試

### **單元測試（Unit Test）**：

- services
    - TestCase：
        
        
        | 測試項目 | 測試模組 | 測試描述 | 預期結果 |
        | --- | --- | --- | --- |
        | national cases: success | `get_national_case` | 在 mock api 的場景下，確認回傳資料 | 返回正確的案例個數 |
        | national cases: response error | `get_national_case` | 在 mock api 的場景下，錯誤回傳被攔截 | 產生 validation error |
        | national cases: network error | `get_national_case` | 當 resquest 無法連到時，產生正確行為 | 產生正確的 exception |
        | city data: success | `get_city_data` | 在 mock api 的場景下，確認回傳資料 | 返回正確的案例個數 |
        | city data: response error | `get_city_data` | 在 mock api 的場景下，錯誤回傳被攔截 | 產生 validation error |
        | region data: success | `get_region_data` | 在 mock api 的場景下，確認回傳資料 | 返回正確的案例個數 |
        | region data: response error | `get_region_data` | 在 mock api 的場景下，錯誤回傳被攔截 | 產生 validation error |
        | region data: parameter error | `get_region_data` | 在 mock api 的場景下，錯誤回傳被攔截 | 產生 validation error |
    - 驗證待辦清單：
        - [x]  national cases: success
        - [x]  national cases: response error
        - [x]  national cases: network error
        - [x]  city data: success
        - [x]  city data: response error
        - [x]  region data: success
        - [x]  region data: response error
        - [x]  region data: parameter error
- test_ui (手動測試)
    - TestCase
        
        以下測試都是 mock service 回傳結果
        
        | 測試項目 | 測試描述 | 測試步驟 | 預期結果 |
        | --- | --- | --- | --- |
        | **Dashboard 初始化** | 確認儀表板在無數據狀態下是否正常渲染 | 1. 啟動應用程序2. 進入 Dashboard 頁面 | 儀表板正常顯示空狀態界面，無報錯或異常。 |
        | **更新全國數據** | 確認全國案例數據更新是否正確 | 1. 點擊「更新數據」按鈕2. 等待 API 響應並刷新儀表板 | 數據正確更新至最新數據，並正確顯示在卡片上。 |
        | **更新趨勢圖表** | 驗證趨勢圖表在數據更新後是否正確繪製 | 1. 輸入特定區域2. 點擊「更新趨勢」按鈕 | 趨勢圖顯示正確且匹配所選區域的數據。 |
        | **風險地圖顯示** | 測試風險地圖是否能正常加載並更新 | 1. 點擊「風險地圖」Tab2. 確認地圖顯示3. 更改地圖縮放/中心位置 | 地圖正常渲染，交互功能正常。 |
    - 驗證待辦清單：
        - [x]  Dashboard 初始化
        - [x]  更新全國數據
        - [x]  更新趨勢圖表
        - [x]  風險地圖顯示

### 整合測試**（手動測試）**：

- TestCase
    
    以下測試都是 mock API 回傳結果
    
    | 測試項目 | 測試描述 | 測試步驟 | 預期結果 |
    | --- | --- | --- | --- |
    | **Dashboard 初始化** | 確認儀表板在無數據狀態下是否正常渲染 | 1. 啟動應用程序2. 進入 Dashboard 頁面 | 儀表板正常顯示空狀態界面，無報錯或異常。 |
    | **更新全國數據** | 確認全國案例數據更新是否正確 | 1. 點擊「更新數據」按鈕2. 等待 API 響應並刷新儀表板 | 數據正確更新至最新數據，並正確顯示在卡片上。 |
    | **更新趨勢圖表** | 驗證趨勢圖表在數據更新後是否正確繪製 | 1. 輸入特定區域2. 點擊「更新趨勢」按鈕 | 趨勢圖顯示正確且匹配所選區域的數據。 |
    | **風險地圖顯示** | 測試風險地圖是否能正常加載並更新 | 1. 點擊「風險地圖」Tab2. 確認地圖顯示3. 更改地圖縮放/中心位置 | 地圖正常渲染，交互功能正常。 |
    | **極端情況測試** | 測試極端數據情況下的應用穩定性 | 1. 輸入大範圍數據（如全國所有城市）2. 切換數據顯示模式 | 應用正常運行，無報錯，性能可接受。 |
- 驗證待辦清單：
    - [x]  Dashboard 初始化
    - [x]  更新全國數據
    - [x]  更新趨勢圖表
    - [x]  風險地圖顯示
    - [x]  極端情況測試