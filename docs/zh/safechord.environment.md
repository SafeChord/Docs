# 環境演進

SafeChord 運行於 **Chorde/K3han 混合雲 Kubernetes 平台**上。考量混合雲節點的物理限制（見 [K3han 叢集](safechord.chorde.k3han.cluster.md)），我們採用務實的 **MVA（最小可行架構）** 策略。不維護正式的 Production 環境，而是將資源集中於 **Staging**，將其視為系統穩定性的最高標準。

本文定義三個環境層級及其與 Chorde 平台的互動方式。

---

## 🌍 環境層級總覽

| 特性 | 🟢 Level 1: 本地開發 (Dev) | 🟡 Level 2: 預覽環境 (CI) | 🔴 Level 3: 平台環境 (Staging) |
| :--- | :--- | :--- | :--- |
| **定位** | **開發者體驗 (DX)** | **隔離與驗證** | **穩定性與交付** |
| **主要目標** | 快速迭代、熱重載與除錯 | 獨立 PR 沙箱，避免資料污染 | **Soak Testing** 與技術展示 |
| **基礎設施來源** | **SafeZone** (臨時) | **SafeZone-Deploy** (降級基礎設施) | **Chorde PaaS** (共享 SaaS) |
| **設定來源** | `SafeZone/docker-compose/` | `SafeZone-Deploy/deploy/preview/` | `Chorde/gitops/` |
| **設定類型** | Docker Compose | ArgoCD Application (Manifest) | ArgoCD ApplicationSet (Helm) |
| **持久性** | Bind Mount (可重置) | **臨時** (EmptyDir / 暫時) | **持久** (PVC / 雲端磁碟) |
| **部署方式** | `docker compose up` | GitHub Actions (自動觸發) | Platform Ops / ArgoCD Sync |

> **註**：設定路徑的第一個區段代表儲存庫名稱（例如 `SafeZone`）。

---

## 🟢 Level 1: 本地開發 (一切的起點)
> *「最小功能集合，萬事由此開始。」*

在本地層級，我們優先考量**開發者體驗 (DX)**。刻意讓開發者避開 Kubernetes 的複雜性，專注於業務邏輯。

### 設定檔策略
我們利用 Docker Compose 的 `profiles` 管理相依性：
* **`infra`**：啟動本機的 PostgreSQL、Valkey (狀態與快取) 與 Kafka。這是開發環境的標準相依集合。
* **`core/ui`**：核心服務通常在 Host (IDE) 上直接運行，並透過 `localhost` 連線到 Docker 基礎設施，以達到最快的除錯迴圈。

```bash
# 啟動基礎設施，同時保留核心程式碼在主機上執行
docker compose --profile infra up -d
```

---

## 🟡 Level 2: 預覽沙箱 (隔離緩衝區)
> *「專為測試而建立的臨時隔離區域。」*

這是 **CI/CD 的核心**。為避免平行 PR 互相干擾，或測試資料污染 Staging，Preview 環境採用 **「自給自足」** 隔離策略，必要時輔以共享資源機制。

### 1. 降級與隔離策略
Preview 環境透過 GitHub Actions 使用 `infras` 路徑中的 Manifest 進行安裝，在獨立 namespace 中部署「輕量級」套件：
* **臨時基礎設施**：使用 CNPG 部署單一 Primary 叢集，無讀寫分離。Valkey 使用 `emptyDir` 部署以加速重啟。
* **共享 Kafka 叢集**：由於 Kafka 資源密集，Preview 環境共用平台層級的 Kafka 叢集，但透過 `preview.` 主題前綴保持邏輯隔離。
* **一次性 Namespace**：PR 合併或關閉後，整個環境立即銷毀。

### 2. 設定管理
所有 Preview 特定的設定（例如停用持久化、連接共享 Kafka）都封裝在 `SafeZone-Deploy/deploy/preview/infras` 中。這確保核心邏輯與正式環境相同，同時顯著降低營運成本。

---

## 🔴 Level 3: 平台 Staging (現實的匯集處)
> *「最接近現實世界的模擬。」*

Staging 是長期運行的展示環境。在此階段，SafeZone 從獨立實體轉變為 **Chorde 平台的租戶**，在真實的平台架構中驗證系統行為。

### 1. 核心任務：Soak Testing
Staging 的策略目標是：
* **Soak Testing**：捕捉僅在長時間運行後才會出現的問題，例如記憶體洩漏或連線池枯竭。
* **技術展示**：作為技術展示的窗口，此環境需要高可用性，並擁有足夠的歷史資料以呈現真實感。

### 2. Chorde SaaS 整合
在 Staging 環境中，SafeZone 不再自行管理基礎設施層。取而代之，它透過 `ExternalName` 或連線字串連接到由 **Chorde** 營運團隊管理的平台級服務：
* **PostgreSQL**：連接到具備完整備份策略、實體隔離且受監控的資料庫叢集。
* **Kafka**：接入由 Strimzi Operator 管理的共享訊息匯流排。
* **Valkey**：利用平台層級的狀態儲存與應用程式管理的快取。

---

## ⚙️ 設定校準原則

為確保環境切換時系統穩定，我們遵循 **「意圖在文件，值在程式碼」** 的原則。具體的服務發現 DNS 位址、連線字串與主題名稱被視為高度變動的實作細節，應直接從各環境的原始碼中取得：

* **本地 (Compose)**：查閱 `SafeZone/docker-compose/` 中的 `.yml` 與 `.env` 檔案。
* **預覽 (CI)**：查閱 `SafeZone-Deploy/deploy/preview/` 中的 Kustomize patches 與 manifests。
* **Staging (平台)**：查閱 `Chorde/gitops/` 中的 Helm values 與 ArgoCD 設定。

### 服務發現機制
* **內部通訊**：服務間呼叫優先使用 K8s 內部 Service 名稱 (`<svc-name>`)。
* **跨 Namespace 存取**：存取共享的 Chorde 平台服務時，使用完全限定網域名稱 (FQDN, 例如 `<svc>.<namespace>.svc.cluster.local`)。
* **讀寫分離**：在 Staging 環境中，應用層必須區分 Primary (RW) 與 Replica (RO) 連線，以充分利用資料庫叢集的資源。

---
> ⚠️ **補充說明**：上述設定反映當前的架構決策。具體的實作細節（例如憑證、金鑰）可能隨時間演進；請務必以實際程式碼為最終依據。