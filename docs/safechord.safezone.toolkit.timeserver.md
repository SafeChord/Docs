---
title: "SafeZone Toolkit: Time server，Safezone 時間中樞"
doc_id: safechord.safezone.toolkit.timeserver
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-19" 
summary: "本文件說明 SafeZone Time-server 工具，包含其核心功能與存取方式。Time-server 作為 SafeZone 的時間中樞，負責統一系統時間的取得、控制與同步，並支援 mock 模式與時間加速等進階操控，以提升系統測試與模擬的彈性。"
keywords:
  - SafeZoneToolkit
  - time manager
  - time control
  - fastapi 
  - SafeChord
logical_path: "SafeChord.SafeZone.Toolkit.Timeserver"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.service.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Python
  - FastAPI
---
| 功能類型 | Endpoint | 使用方式 | 說明 |
| --- | --- | --- | ----------------------------- |
| time | get | `GET /now` | 查詢目前系統時鐘（經 mock layer 計算後的結果） |
| time | set | `POST /set` | 設定 mock layer 參數 |
| time | status | `GET /status` | 查詢mock layer 參數 |

