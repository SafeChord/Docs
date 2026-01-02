---
title: Environment Landscape & Evolution
doc_id: safechord.environment
version: 0.2.4
last_updated: "2026-01-02"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Global"
summary: "定義 SafeChord 系統的環境策略。闡述我們如何依據開發生命週期的不同階段（Local, Preview, Staging），在資源隔離與平台整合之間做出務實的架構權衡。"
keywords:
  - Environment
  - Docker Compose
  - Kubernetes
  - GitOps
  - Service Discovery
  - PaaS
  - Soak Testing
logical_path: "SafeChord.Environment"
related_docs:
  - "safechord.chorde.k3han.md"
  - "safechord.safezone.deployment.charts.md"
parent_doc: "safechord"
---

# 環境演進論 (Environment Evolution)

SafeChord 運行在 **混合雲 Kubernetes 平台 (Chorde/K3han)** 之上。考量到混合雲節點的物理限制（詳見 [K3han Cluster](safechord.chorde.k3han.cluster.md)），我們採取務實的 **MVA (Minimum Viable Architecture)** 策略。我們不追求形式上的 Production 環境，而是將資源集中於 **Staging**，將其打造為系統穩定運行的最高標準。

本文件定義了三種環境形態，以及它們如何與 Chorde 平台互動。

---

## 🌍 環境分級概覽 (The Environment Tier)

| 特徵 | 🟢 Level 1: Local (Dev) | 🟡 Level 2: Preview (CI) | 🔴 Level 3: Platform (Staging) |
| :--- | :--- | :--- | :--- |
| **定位** | **開發體驗 (DX)** | **隔離驗證 (Isolation)** | **穩定性交付 (Stability)** |
| **核心目標** | 極速迭代、熱重載、除錯 | 獨立 PR 沙盒、資料不污染 | **浸潤測試 (Soak Test)**、技術演示 |
| **基礎設施來源** | **SafeZone** (隨開隨用) | **SafeZone-Deploy** (自帶降級版 Infra) | **Chorde PaaS** (公用 SaaS 服務) |
| **配置來源** | `SafeZone/docker-compose/` | `SafeZone-Deploy/deploy/preview/infras/` | `Chorde/gitops/` |
| **配置類型** | Docker Compose | ArgoCD Application (Helm) | ArgoCD Application (Helm) |
| **資料持久性** | Bind Mounts (可重置) | **Ephemeral** (EmptyDir, 用完即丟) | **Persistent** (PVC / Cloud Volume) |
| **部署方式** | `docker compose up` | GitHub Actions 自動觸發 | 平台維運 / ArgoCD Sync |

> **提示**: 配置來源路徑的**首個區段**代表倉庫名稱（如 `SafeZone`），實際路徑請參照各倉庫結構。

---

## 🟢 Level 1: 本地開發 (The Local Origin)
> *"這是系統的最小功能集，一切從這裡開始。"*

在本地端，我們的首要目標是 **開發者體驗 (DX)**。在此階段，我們刻意屏蔽 K8s 的複雜度，讓開發者專注於業務邏輯。

### 啟動機制 (Profiles Strategy)
我們利用 Docker Compose 的 `profiles` 來管理依賴：

*   **`infra`**: 啟動本地版的 PostgreSQL, Redis, Kafka。這是開發時的標準依賴。
*   **`core/ui`**: 核心服務通常直接在 Host (IDE) 執行，透過 `localhost` 連接 Docker 內的基礎設施，以獲得最快的除錯回饋循環。

```bash
# 啟動基礎設施，核心程式碼保留在 Host 運行
docker compose --profile infra up -d
```

---

## 🟡 Level 2: 預覽沙盒 (The Preview Sandbox)
> *"為測試構建的臨時隔離區。"*

這是 **CI/CD 的核心**。為了避免並行開發的 PR 互相干擾，也不讓測試髒資料污染 Staging，Preview 環境採用 **「自給自足 (Self-Contained)」** 的隔離策略。

### 1. 降級與隔離 (Downgrade Strategy)
Preview 環境**不會**連接 Chorde 平台的公用資料庫。我們透過 GitHub Actions 安裝 `infra` 路徑下的 ArgoCD Application，在獨立的 Namespace 內快速部署一套「降級版」設施：

*   **Ephemeral Infra**: 使用單節點、無持久化 (EmptyDir) 的 Redis 與 Kafka，追求部署速度與資源回收效率。
*   **Sealed Secrets**: 使用開發用的簡易金鑰，降低管理成本。
*   **拋棄式 Namespace**: 測試結束或 PR 合併後，整個環境即刻銷毀。

### 2. 配置管理
所有 Preview 的特殊配置（如關閉持久化、使用內建 DB）都封裝在 `SafeZone-Deploy/deploy/preview/infra` 中。這確保了核心邏輯與生產環境一致，但運行成本大幅降低。

---

## 🔴 Level 3: 平台整合 (The Platform Staging)
> *"最接近真實世界的運行環境。"*

這是長期運行的展示環境。在這裡，SafeZone 從獨立運作轉型為 **Chorde 平台的租戶 (Tenant)**，以驗證系統在真實平台架構下的行為。

### 1. 核心任務：浸潤測試 (Soak Testing)
建立 Staging 的戰略目的在於：
*   **浸潤測試 (Soak Testing)**：捕捉僅在長期運行後才會浮現的問題，例如記憶體洩漏 (Memory Leak) 或連線池耗盡 (Connection Exhaustion)。
*   **技術演示 (Portfolio Showcase)**：作為對外展示技術實力的窗口，此環境需具備高可用性，並累積足夠的歷史數據以呈現真實感。

### 2. 整合 Chorde SaaS
在 Staging 環境，SafeZone 不再自建基礎設施，而是透過 `ExternalName` 或 Connection String，對接由 **Chorde** 維運團隊管理的平台級服務：

*   **PostgreSQL**: 連接具備完整備份與監控機制的 Primary DB。
*   **Kafka**: 接入共用的 Message Bus。
*   **Redis**: 使用 System Redis。

### 3. 通往 Production 的最後一哩 (The Gap to Prod)
我們目前止步於 Staging。若需升級至 Production，配置邏輯將保持一致，僅需在基礎設施層面進行強化：
*   **容錯增強**：升級為多 AZ (Availability Zone) 節點部署。
*   **參數調優**：針對 OS Kernel 與 Runtime 進行細緻的效能優化。

---

## 🗺️ 服務發現對照表 (Service Discovery Map)

開發者在切換環境時，需注意連線目標的變化：

| 服務組件 | Local (Compose) | Preview (Namespace 內自建) | Staging (跨 Namespace 呼叫 Chorde) |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | `db:5432` | `safezone-postgresql.safezone-preview.svc` | `postgresql-primary.database.svc` |
| **Redis** | `redis:6379` | `safezone-redis.safezone-preview.svc` | `redis-master.system-redis.svc` |
| **Kafka** | `kafka:9092` | `safezone-kafka.safezone-preview.svc` | `kafka.kafka.svc` |
| **Analytics API** | `localhost:8000` | `safezone-analytics-api.safezone-preview.svc:80` | `safezone-analytics-api.safezone.svc:80` |

> **注意**: Staging 環境依賴 K8s 的跨 Namespace DNS 解析 (`<svc>.<namespace>.svc`) 來存取 Chorde 資源。

---
> ⚠️ **後記**: 以上配置描述反映了當前的架構決策，具體實作細節可能會隨專案演進而調整，請以實際程式碼為準。