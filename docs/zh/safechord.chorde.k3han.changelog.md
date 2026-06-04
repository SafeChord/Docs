# K3han 平台版本更新記錄

本文件記錄 K3han 叢集的重要架構變動，作為技術債分析與決策追溯的歷史參考。

---

## 🔖 [v0.3.6] - 2026-06-04

### 🌐 NGINX Gateway Fabric & Gateway API 遷移 (Issue #4, #6)
*   **Ingress 引擎轉換**：退役 EOL `kubernetes/ingress-nginx` (CVE-2026-42945)，全面標準化採用 **NGINX Gateway Fabric (NGF v2.6.3)** 與 **Kubernetes Gateway API (v1.5)**。
*   **控制與資料平面解耦**：
    *   統一將控制平面（Control Plane）綁定至日本主節點 (`ct-serv-jp`)。
    *   私有資料平面 (`private-gateway`) 以 `ClusterIP` 服務方式運行於 `ct-serv-jp`。
    *   公開資料平面 (`public-gateway`) 透過節點標籤 `chorde.io/purpose=proxy-only` 綁定至台灣 GCE 邊緣節點，並啟用 `hostPort 80/443`，嚴格限制其記憶體資源以保護 1GB RAM 的邊緣節點。
*   **零信任私有通道**：將原本由主機 systemd 管理的 Cloudflare Tunnel 以及 Tailscale 虛擬網卡綁定，遷移為**叢集內 `cloudflared` 部署 (Deployment)**，將流量安全轉發至私有閘道的 `ClusterIP`。
*   **閘道過濾器安全強化**：
    *   在 Gateway Listener 層級統一以泛域名憑證進行 SSL 終端。
    *   套用 Gateway API 過濾器：`AuthenticationFilter` (基礎認證)、`URLRewrite` (路徑重寫)、`ResponseHeaderModifier` (剝除 `X-Powered-By`)。
    *   在台灣邊緣節點強制執行單一 IP `RateLimitPolicy` (HTTP 429)。
    *   配置 `NginxProxy.rewriteClientIP` 還原真實用戶 IP（並與 GCP VPC 防火牆規則同步）。

---

## 🔖 [v0.3.5] - 2026-05-02

### 🏗️ 文件現代化
*   **原型轉換**：正式將所有 Infrastructure 規格從 `Blueprint` 原型遷移至 `Brain` 原型。
*   **英文優先 SSOT**：完成 Chorde 文件堆疊的全文英文重寫，將根目錄 `/docs/` 建立為單一事實來源（SSOT）。
*   **策略整併**：將高層級路線圖與演化指南合併至核心平台地圖中。

---

## 🔖 [v0.3.0] - 2026-03-07

### 🚀 GitOps v2 重構
*   **遞迴編排**：引入 ArgoCD `ApplicationSet` 取代單體式 `Application` 清單，實現動態服務註冊與分層相依性管理。
*   **三階段同步（Stages）**：實施強制同步波策略：
    *   `00-bootstrap`：安全性、Ingress 與 Controllers。
    *   `01-platform`：監控、日誌與 Operators。
    *   `02-components`：資料庫、佇列與 SafeZone 服務。
*   **全域入口點**：建立 `root.yaml` 作為整個叢集的集中編排器。

### 🛡️ Operator 優先遷移
*   **資料庫**：從 Bitnami 風格的 Helm charts 遷移至 **CloudNativePG (CNPG)**，實現自動故障轉移與原生 Kubernetes 備份整合。
*   **訊息佇列**：將 Kafka 從標準 charts 遷移至 **Strimzi Operator**，簡化 broker 與 topic 的生命週期管理。
*   **ArgoCD 多來源**：採用 Multiple Sources 模式引用上游官方 Helm charts，同時覆蓋本地 `values-custom.yaml`，大幅減少儲存庫膨脹。
*   **棄用**：正式退役 Chorde 儲存庫中的本地 `helm-charts/` 目錄。

### 📊 可觀測性強化
*   **S3 日誌卸載**：成功將 Loki 儲存後端遷移至 Amazon S3（日本區域），實現零本機儲存足跡的日誌保留。
*   **遙測強化**：最佳化 Prometheus 刮取規則，濾除來自 Grafana 與 sidecar 探針的雜訊。

---

## 🔖 [v0.2.0] - 2024-05-09

### 🏗️ 拓撲穩定化
*   **單一控制平面**：將控制平面整合至 `ct-serv-jp`（Contabo 日本）。
*   **邊緣閘道**：將 `gce-agent-tw` 建立為台灣流量的唯一公開 ingress 點，防止內部 UI 模組直接暴露。
*   **資料本地化**：將顯示模組與 PostgreSQL 副本集中於 `acer-agent`（台灣家中），充分利用本地高速 I/O。
*   **網格強化**：重新設計節點標籤與污點，反映可靠性分層（雲端 vs. 本地）。

---

## 🏁 [v0.1.0] - 2024-05-04

### 📦 初始 MVP（概念驗證）
*   驗證使用新加坡（Hetzner）與台灣（GCP）節點的混合雲可行性。
*   實作初始 Tailscale 覆蓋網路，用於 NAT 穿越。
*   建立跨地理區域的基本主從 PostgreSQL 同步。