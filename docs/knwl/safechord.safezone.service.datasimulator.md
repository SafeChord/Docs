---
title: "SafeZone Service: CovidDataSimulator - Epidemic Data Simulation"
doc_id: safechord.safezone.service.datasimulator
version: "0.1.0" 
status: active 
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16" 
summary: "本文檔詳細描述 CovidDataSimulator 服務，其核心功能是將現有疫情數據模擬成每日疫情回報，並提供 RESTful API 以支持批次發送特定日期或日期區間的已驗證疫情數據給 DataIngestor 服務。"
keywords:
  - SafeZone
  - CovidDataSimulator
  - data simulation
  - epidemic data
  - daily reports
  - batch processing
  - data validation
  - RESTful API
  - Cronjob
  - DataIngestor 
  - SafeChord
logical_path: "SafeChord.SafeZone.Service.DataSimulator"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.service.dataingestor.md" 
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python 
  - FastAPI 
  - Docker 
---
# CovidDataSimulator

## **服務名稱與描述：**

- **名稱**：CovidDataSimulator。
- **描述**：將現有疫情資料模擬成每日疫情回報，並提供批次發送的功能。

---

## **服務需求：**

- **功能需求**：
    - **RESTful API ：**可以供 Cronjob 要求它提供資料給 Ingestor**。**
    - **發送疫情資料給 Ingestor：**可以請求發送特定日、日區間的疫情資料。
    - **驗證疫情資料**：每筆資料確認無誤才能發送。

---

## 目錄架構：

```notion
	CovidDataSimulator
  |-- app
       |-- api
            |-- endpoints.py
		   |-- validators
					  |-- input_validator.py
					  |-- output_validator.py
       |-- pipeline
            |-- data_productor.py
            |-- date_sender.py
            |-- orchestrator.py
       |-- config
            |-- settings.py
            |-- logger.py
       |-- exceptions
            |-- custom_exceptions.py
            |-- handler.py
       |-- main.py
  |-- environments
       |-- test
           |-- Dockerfile.test
           |-- requirements.txt
           |-- .env
           |-- tests
		           |-- data
				           |-- covid_data.csv
               |-- integration_test
                   |-- test_main.py
               |-- unit_test
		               |-- test_validtor.py
                   |-- test_data_productor.py
                   |-- test_data_sender.py
		           |-- cases
				           |-- test_validtor.json
		               |-- test_data_productor.json
		               |-- test_data_sender.json
		               |-- test_integration.json
       |-- dev
           |-- Dockerfile.dev
           |-- requirements.txt
           |-- .env
       |-- prod
           |-- Dockerfile.prod
           |-- requirements.txt
           |-- .env
  |-- README.md
```

---

**單元測試（Unit Test）**：

- data_productor
    - TestCase：
        
        
        | 測試項目 | 測試模組 | 測試描述 | 預期結果 |
        | --- | --- | --- | --- |
        | Daily data producted test | `daily_data_productor` | 測試 2023-03-20 的資料生成是否正確 | 返回日期為 2023-03-20 且資料符合預期的篩選結果 |
        | Interval data producted test | `interval_data_productor` | 測試日期區間 2023-03-20 到 2023-04-01 的資料生成是否正確 | 返回指定區間內的所有資料 |
        | Daily data producted test in empty senario | `daily_data_productor` | 測試 2023-03-25 的資料生成是否正確，在無資料情況下 | 返回空的資料集 |
        | Interval data producted test in empty senario | `interval_data_productor` | 測試日期區間 2023-05-01 到 2023-06-01 的資料生成是否正確，在無資料情況下 | 返回空的資料集 |
    - 驗證待辦清單：
        - [x]  Daily data producted test
        - [x]  Interval data producted test
        - [x]  Daily data producted test in empty senario
        - [x]  Interval data producted test in empty senario
- data_sender
    - TestCase：
        
        
        | 測試項目 | 測試模組 | 測試描述 | 預期結果 |
        | --- | --- | --- | --- |
        | Daily data send test | `data_sender` | 測試在正確情境下是否成功發送 2023-03-20 的資料 | 返回狀態碼 200 並顯示 "Data sent successfully!" |
    - 驗證清單：
        
        
        - [x]  Daily data send test

整合測試**（**Integration Test**）**：

- TestCase：
    
    
    | 測試項目 | 測試模組 | 測試描述 | 預期結果 |
    | --- | --- | --- | --- |
    | Request by daily data | `/simulate/daily` | 測試日期為 2023-03-20 的資料請求是否正確 | 返回狀態碼 200 並顯示 "Data sent successfully for date 2023-03-20" |
    | Request by interval data | `/simulate/interval` | 測試日期區間 2023-03-20 到 2023-04-05 的資料請求是否正確 | 返回狀態碼 200 並顯示 "Data sent successfully for dates 2023-03-20 ~ 2023-04-05" |
    | Request by daily data in invalid date format | `/simulate/daily` | 測試日期格式不正確的情況，如 "2023/03/20" | 返回狀態碼 422 |
    | Request by interval data in invalid date format | `/simulate/interval` | 測試區間日期格式不正確的情況，如 "2023-03-20" 到 "2023-04/05" | 返回狀態碼 422 |
    | Request by daily data with no available data | `/simulate/daily` | 測試日期為 2025-03-20 的情況，當無可用資料時 | 返回狀態碼 400 |
    | Request by interval data with no available data | `/simulate/interval` | 測試日期區間為 2025-03-20 到 2026-04-05 的情況，當無可用資料時 | 返回狀態碼 400 |
    | Request by interval data with incorrect date range | `/simulate/interval` | 測試結束日期早於開始日期的情況，如 "2023-03-25" 到 "2023-03-20" | 返回狀態碼 400 |
    | Request for non-existent endpoint | `simulate/unknown` | 測試請求不存在的端點的情況 | 返回狀態碼 404 |
    | Request by daily data with missing date parameter | `/simulate/daily` | 測試缺少日期參數的情況 | 返回狀態碼 422 |
    | Request by interval data with missing parameters | `/simulate/interval` | 測試缺少必要的區間參數的情況 | 返回狀態碼 422 |
    | Request by interval data with same start and end date | `/simulate/interval` | 測試開始日期與結束日期相同的情況，如 "2023-03-20" 到 "2023-03-20" | 返回狀態碼 200 並顯示 "Data sent successfully for dates 2023-03-20 ~ 2023-03-20" |
- 驗證清單：
    - [x]  Request by daily data
    - [x]  Request by interval data
    - [x]  Request by daily data in invalid date format
    - [x]  Request by interval data in invalid date format
    - [x]  Request by daily data with no available data
    - [x]  Request by interval data with no available data
    - [x]  Request by interval data with incorrect date range
    - [x]  Request for non-existent endpoint
    - [x]  Request by daily data with missing date parameter
    - [x]  Request by interval data with missing parameters
    - [x]  Request by interval data with same start and end date