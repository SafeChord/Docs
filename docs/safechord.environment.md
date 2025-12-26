---
title: Environment Landscape & Evolution
doc_id: safechord.environment
version: 0.2.0
last_updated: "2025-12-26"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Global"
summary: "定義 SafeChord 系統的環境策略。描述系統如何從本地開發 (Local) 的輕量級形態，演進至預覽環境 (Preview) 的隔離沙盒，最終到達平台環境 (Staging) 進行整合展示。"
keywords:
  - Environment
  - Docker Compose
  - Kubernetes
  - GitOps
  - Service Discovery
  - PaaS
logical_path: "SafeChord.Environment"
related_docs:
  - "safechord.chorde.k3han.md"
  - "safechord.safezone.deployment.charts.md"
parent_doc: "safechord"
---

# 環境演進論 (Environment Evolution)

SafeChord 是一個運行在 **混合雲 Kubernetes 平台 (Chorde/K3han)** 上的應用程式。受限於實體節點的網路拓撲與容錯能力（詳見 [K3han Cluster](safechord.chorde.k3han.cluster.md)），我們目前不定義 Production 環境，而是將 **Staging** 作為最高級別的長期運行環境。

本文件定義了三種環境形態，以及它們如何與 Chorde 平台互動。

---

## 🌍 環境分級概覽 (The Environment Tier)

| 特徵 | 🟢 Level 1: Local (Dev) | 🟡 Level 2: Preview (CI) | 🔴 Level 3: Platform (Staging) |
| :--- | :--- | :--- | :--- |
| **定位** | **開發 (Development)** | **驗證 (Verification)** | **展示 (Demo / Staging)** |
| **核心目標** | 快速迭代、除錯、熱重載 | PR 隔離測試、不污染主庫 | 長期穩定運行、真實數據整合 |
| **基礎設施來源** | Docker Compose (Local) | **SafeZone-Deploy** (自帶降級版 Infra) | **Chorde PaaS** (共用 SaaS 服務) |
| **配置來源** | `docker-compose.yml` | `deploy/preview/values.yaml` | `deploy/staging/values.yaml` |
| **資料持久性** | Bind Mounts (可重置) | **Ephemeral** (EmptyDir, 用完即丟) | **Persistent** (PVC / Cloud Volume) |
| **部署方式** | `docker compose up` | CI 觸發 `helm install` | CI 觸發 ArgoCD Sync |

---

## 🟢 Level 1: 本地開發 (The Local Origin)
> *"這是系統的最小功能集。一切從這裡開始。"*

在本地開發階段，我們追求的是**極致的啟動速度**與**開發者體驗 (DX)**。我們移除了所有 K8s 的複雜度，專注於邏輯本身。

### 啟動機制 (Profiles Strategy)
我們使用 Docker Compose 的 `profiles` 功能來管理依賴鏈：

*   **`infra`**: 啟動本地版的 PostgreSQL, Redis, Kafka。這是開發時的標配。
*   **`core/ui`**: 核心服務通常直接在 IDE (Host) 執行，透過 `localhost` 連接 Docker 內的 Infra。

```bash
# 典型開發場景：只啟動 Infra，程式碼在 Host 跑
docker compose --profile infra up -d
```

---

## 🟡 Level 2: 預覽沙盒 (The Preview Sandbox)
> *"為了測試，我們在 K8s 裡蓋了一座臨時城堡。"*

這是 **CI/CD 流程** 的核心。為了確保測試的獨立性，並避免測試數據污染 Staging 環境，Preview 環境採用 **「自給自足 (Self-Contained)」** 策略。

### 1. 降級與隔離 (Downgrade Strategy)
Preview 環境**不使用** Chorde 平台提供的共用資料庫。相反，它會在 `helm install` 時，透過 `safezone-infra` Chart 順便部署一套「降級版」的基礎設施：

*   **Ephemeral Infra**: 部署單節點、無持久化 (EmptyDir) 的 Redis 與 Kafka。
*   **Sealed Secrets**: 使用開發用的簡易密碼，快速解鎖。
*   **獨立 Namespace**: 每個 PR 都有自己的 Namespace，測試完即銷毀。

### 2. 配置管理
所有 Preview 的特殊配置（如關閉持久化、使用內建 DB）都定義在 `SafeZone-Deploy/deploy/preview` 中。這確保了應用程式邏輯不變，但依賴的資源變輕了。

---

## 🔴 Level 3: 平台整合 (The Platform Staging)
> *"這是系統目前最高級別的真實世界。"*

這是長期運行的展示環境。在這裡，SafeZone 不再自己管理基礎設施，而是轉型為 **Chorde 平台的租戶 (Tenant)**。

### 1. 使用 Chorde SaaS
在此環境下，SafeZone 的 Helm Chart **不會部署** `safezone-infra` 中的 DB 或 Kafka。而是透過 `ExternalName` Service 或直接配置 Connection String，去連接由 **Chorde** (維運 Repo) 統一管理的平台級服務：

*   **PostgreSQL**: 連接 Chorde 的 Primary DB (具備備份與監控)。
*   **Kafka**: 連接 Chorde 的共用 Message Bus。
*   **Redis**: 連接 Chorde 的 System Redis。

### 2. 部署與晉升
*   **GitOps**: 透過 ArgoCD 監控 `SafeZone-Deploy/deploy/staging` 分支。
*   **晉升 (Promotion)**: 當 Preview 驗證通過後，CI 流程會更新 Staging 的 Image Tag，ArgoCD 隨即將新版本同步至叢集。

---

## 🗺️ 服務發現對照表 (Service Discovery Map)

開發者在切換環境時，需注意連線目標的變化：

| 服務組件 | Local (Compose) | Preview (Namespace 內自建) | Staging (跨 Namespace 呼叫 Chorde) |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | `db:5432` | `safezone-postgresql.safezone-preview.svc` | `postgresql-primary.database.svc` |
| **Redis** | `redis:6379` | `safezone-redis.safezone-preview.svc` | `redis-master.system-redis.svc` |
| **Kafka** | `kafka:9092` | `safezone-kafka.safezone-preview.svc` | `kafka.kafka.svc` |
| **Analytics API** | `localhost:8000` | `safezone-analytics-api:80` | `safezone-analytics-api:80` |

> **注意**: Staging 環境依賴 K8s 的跨 Namespace DNS 解析 (`<svc>.<namespace>.svc`) 來存取 Chorde 資源。