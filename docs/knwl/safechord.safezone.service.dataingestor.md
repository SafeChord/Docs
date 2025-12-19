---
title: "SafeZone Service: CovidDataIngestor - Data Ingestion & Validation"
doc_id: safechord.safezone.service.dataingestor
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔介紹 CovidDataIngestor 服務，其主要職責是通過 RESTful API 接收來自 CovidDataSimulator 的疫情數據，進行數據處理與驗證後，將其持久化存儲到資料庫的 'Case' 表中。"
keywords:
  - SafeZone
  - CovidDataIngestor
  - data ingestion
  - data validation
  - data processing
  - database storage
  - RESTful API
  - CovidDataSimulator
  - case_reporting database 
  - Case table
  - SafeChord
logical_path: "SafeChord.SafeZone.Service.DataIngestor"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.service.datasimulator.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python 
  - FastAPI 
  - PostgreSQL
  - Docker
---
# DataIngestor

- **服務名稱與描述**
    - **名稱**：CovidDataIngestor。
    - **描述**：蒐集從CovidDataSimulator發來的資，經過簡單的處理和驗證後，存入資料庫。
    - 目錄架構：
        
        ```notion
        	CovidDataIngestor
          |-- app
               |-- api
                    |-- endpoints.py
               |-- validators
        			      |-- api_validator.py
        			 |-- exceptions
        					  |-- custom_exceptions.py
        					  |-- handlers.py
               |-- pipeline
                    |-- data_creator.py
                    |-- date_validator.py
                    |-- orchestrator.py
               |-- config
                    |-- settings.py
        						|-- logger.py
               |-- main.py
        
          |-- environments
               |-- test
                   |-- Dockerfile.test
                   |-- requirements.txt
                   |-- db
        		           |-- test.db
                   |-- .env
                   |-- tests
                       |-- integration_test
                           |-- test_main.py
                       |-- unit_test
                           |-- test_data_creator.py
                           |-- test_data_validtor.py
        		           |-- cases
        		               |-- test_data_creator.json
        		               |-- test_data_validtor.json
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
        
- **服務需求**
    - **功能需求**：
        - 有 **RESTful API**
        - 可以接受 CovidDataCollector 發送來的資料。
        - 能處理和驗證資料
        - 將資料存入資料庫
    - **非功能需求**：
        - 暫無。
- 資料庫描述
    - 概述
        - **資料庫名稱**：`case_reporting`
        - **用途**：儲存各地區的案例數據，以支持報告和查詢操作。
    - 資料庫表格
        - **描述**：儲存每個地區的案例資料，包括發生日期、城市、地區及案例數。
        - 表格名稱：`Case`
        
        | 欄位名稱 | 類型 | 說明 | 約束 |
        | --- | --- | --- | --- |
        | `id` | INT | 自動增長的主鍵，用於唯一標識每條記錄 | `PRIMARY KEY`, `AUTO_INCREMENT` |
        | `date` | DATE | 案例發生的日期 | `NOT NULL` |
        | `city` | VARCHAR(50) | 案例發生的城市 | `NOT NULL` |
        | `region` | VARCHAR(50) | 案例發生的具體地區 | `NOT NULL` |
        | `cases` | INT | 案例的數量，必須是正數 | `NOT NULL`, `CHECK (cases > 0)` |

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