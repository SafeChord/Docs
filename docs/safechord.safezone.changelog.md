---
title: SafeZone ChangeLog
doc_id: safechord.safezone.changelog
last_updated: '2026-04-15'
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: SafeZone Module
summary: 記錄 SafeZone 應用層的版本演進。對於 AI Agent 而言，本文件是追蹤架構變更、廢棄功能及新引入技術的重要依據，確保 Context
  的時效性。
keywords:
  - SafeZone
  - Changelog
  - Release Notes
  - v0.3.0
  - Container-Native Smoke Test
  - szcli
logical_path: SafeChord.SafeZone.ChangeLog
related_docs:
  - safechord.knowledgetree.md
  - safechord.safezone.md
parent_doc: safechord.safezone
doc_version: 0.3.0
app_version: 0.3.0-dev
---

# SafeZone 版本變更日誌

本文件同步自專案根目錄的 `CHANGELOG.md`，並為 AI 提供語意化的版本導航。

---

## [0.3.0-dev] - 2026-04-15

### 🚀 關鍵變更 (Critical Changes)
*   **容器原生煙霧測試架構 (Container-Native Smoke Test)**: 
    *   廢棄舊有的 `bash` + `jq` 腳本，改為以 Python 實作的 CSV 驅動測試引擎 (`smoke_test.py`)。
    *   測試引擎運行於獨立的 `safezone-cli-ops` 容器中，直接在 Docker Compose 網路內執行。
    *   測試案例從 `data/smoke-test/` 遷移至 `toolkit/cli/ops/test_cases/`。
*   **szcli 功能強化**:
    *   新增全域 `--verbose` / `-v` 旗標，支援顯示 HTTP Header (如 `X-Cache-Status`)。
    *   `szcli db clear` 新增 `--yes` / `-y` 旗標，支援非互動式（自動化）執行。
*   **觀測性提升**: 
    *   實現 `X-Cache-Status` 標頭的完整傳遞鏈（`analytics-api` -> `cli-relay` -> `szcli`），可用於驗證快取命中狀態。

### 🐛 修復與穩定化
*   **修復 `dev-up.sh` 啟動錯誤**: 解決了在 `set -e` 下 `((attempt++))` 導致的非預期退出。
*   **強化非同步驗證**: 在測試引擎中實作自適應輪詢與有狀態斷言 (Stateful Assertion) 機制，有效處理 Kafka 非同步延遲與最終一致性驗證。

---

## [0.2.1] - 2025-09-12

### 🚀 關鍵變更 (Critical Changes)
*   **Kafka 核心現代化**: 從 `segmentio/kafka-go` 遷移至 `twmb/franz-go`。
    *   *AI 注意*: 此變更解決了 KRaft 模式下的相容性問題，若涉及 Kafka 連線邏輯請務必參考新庫。
*   **強化消費者位移管理**: Go Worker 禁用自動提交 (Auto-commit)，改為手動管理 Offset，確保 "At-least-once" 語意。
*   **生產者分區策略優化**: 改用 "Natural Key" (如 city-region) 搭配 Murmur2 分區演算法。

### 🐛 修復與穩定化
*   **解決 KRaft 靜默失敗問題**: 修復了導致 v0.2.0 無法在 KRaft 叢集部署的關鍵 Bug。
*   **煙霧測試 (Smoke Test) 強化**: 使用輪詢機制 (`wait_for_infra_services`) 取代固定 `sleep`，消除 CI 流程中的競爭條件 (Race Conditions)。

---

## [0.2.0] - 2025-09-01

這是 SafeChord 的重大里程碑，從 MVP 進化為具備工業級觀測與自動化能力的平台。

### ✨ 新增功能
*   **觀測性基礎 (Observability)**: 引入 `Trace ID` 機制，標準化 JSON 日誌格式。
*   **非同步資料流架構 (Async Architecture)**: 
    *   以 Kafka 為核心的事件驅動架構。
    *   `Data Ingestor` 重構為 Producer。
    *   `Pandemic Simulator` 升級為 `asyncio` + `httpx`。
*   **Go Worker**: 新增 Golang 實作的消費者，負責批次寫入 PostgreSQL。
*   **API 快取機制**: `Analytics API` 整合 Redis 快取層。
*   **時間伺服器 (Time Server)**: 引入 `time-server` 進行集中時間控制。

### 🛠️ 重構與標準化
*   **服務更名**: 統一名稱空間（例如 `coviddatasimulator` -> `pandemic-simulator`），去耦合特定事件。
*   **CI/CD 重構**: 使用動態 Git SHA 作為 Tag，引入 `release.yml` 自動化發佈流程。
*   **統一資料契約 (Unified Contracts)**: 抽取共享 Pydantic 模型至 `utils` 子模組。

---

## [0.1.0] - 2025-05-16

### 📦 初始 MVP
*   驗證基礎同步資料流：`simulator` -> `ingestor` -> `analytics-api`。