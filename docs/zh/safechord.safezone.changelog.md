# SafeZone 變更日誌

本文件提供 SafeZone 應用層的語意化版本導覽，與儲存庫中的 `CHANGELOG.md` 保持同步。

---

## [0.3.2] - 2026-05-02

### 🚀 重大變更（模板傳播）
*   **模板傳播**：Python 微服務模板（v0.3.1）已成功傳播至 `data-ingestor` 與 `pandemic-simulator`。
*   **目錄重構**：
    *   `data-ingestor`：抽取出 `services/ingest_service.py`（不含任何 FastAPI 匯入），並新增 `api/dependencies.py` 處理 Kafka DI。
    *   `pandemic-simulator`：將 `pipeline/` 模組合併至 `services/` 層，並將測試目錄結構化為 `unit/` 與 `integration/`。
*   **自動化改善**：
    *   **Makefile 自動化**：`make test-*` 目標現在會自動觸發 `make build-*`，確保測試永遠針對最新映像檔執行。
    *   **清理作業**：移除舊有服務的 README，改以 `Docs/` 中的集中式 KDD 知識庫取代。

### 🧪 品質與測試
*   **測試補強**：為 `data-ingestor` 新增完整的單元測試，透過模擬 Kafka 生產者達成 87% 覆蓋率。
*   **CI/CD 對齊**：驗證完整 local-ci 管線（建置 -> 測試 -> 冒煙測試）在新模板結構下的運作。

---

## [0.3.1] - 2026-04-22

### 🏗️ 架構里程碑（模板設計）
*   **Python 微服務模板**：在 `analytics-api` 中建立標準化的 `api/core/services/exceptions` 分層架構，作為專案的設計藍圖。
*   **純 ASGI 中介軟體**：以純 ASGI 實作取代 `BaseHTTPMiddleware`，修復 `ContextVar` 隔離問題，確保 `X-Cache-Status` 標頭能正確傳遞。
*   **分層依賴注入**：將 `redis_cache` 裝飾器從 FastAPI `Request` 物件解耦，遷移至 `api/dependencies.py` 中明確的 DI 提供者。
*   **快取雪崩保護**：在快取服務中實作雙重檢查鎖定機制，防止並發快取未命中時造成資料庫過載。

---

## [0.3.0] - 2026-04-16

### 🛡️ 系統強化
*   **工作者強化（Golang）**：
    *   **記憶體洩漏修復**：修復因迴圈中 `defer cancel()` 配置不當導致的關鍵計時器 goroutine 洩漏問題。
    *   **Go 慣用語重構**：以套件層級建構函式（`NewWorker`）與基於介面的 DI 取代 Java 風格的工廠模式。
*   **容器原生冒煙測試**：
    *   從基於 Shell 的測試遷移至 Python 驅動的 CSV 引擎（`smoke_test.py`）。
    *   測試引擎現在在專屬的 `safezone-cli-ops` 容器中執行，確保 CI/CD 執行的一致性。
*   **szcli 增強功能**：新增全域 `--verbose` 支援 HTTP 標頭檢查，以及非互動式 `--yes` 標誌用於自動化流程。

---

## [0.2.1] - 2025-09-12

### 🚀 最佳化
*   **Franz-Go 遷移**：將 Kafka 客戶端從 `segmentio/kafka-go` 切換至 `twmb/franz-go`，以獲得 KRaft 支援與更好的效能。
*   **手動偏移量管理**：在 Go Worker 中停用自動提交，確保「至少一次」的傳遞語意。
*   **分割邏輯**：實作「自然鍵」分割策略（城市-區域），保證區域性資料的排序正確性。

---

## [0.2.0] - 2025-09-01

### ✨ 主要功能
*   **可觀測性基礎**：在全部服務中標準化 Trace ID 傳遞與 JSON 日誌記錄。
*   **非同步資料管線**：使用 Kafka 作為中央事件匯流排，將系統完全解耦。
*   **持久層**：引入 Golang Worker 進行批次 PostgreSQL upsert 操作，並使用 Redis 處理 API 回應快取。
*   **時間伺服器**：集中化虛擬時鐘，用於模擬控制。

---

## [0.1.0] - 2025-05-16

### 📦 MVP
*   初始同步資料流程驗證：`simulator` -> `ingestor` -> `analytics-api`。