# 🛠️ Chorde 平台地圖

> **類型**：地圖（基礎設施指揮中心）
> **範圍**：管理異質叢集，實作 GitOps v2 部署，並維護混合雲安全邊界。

---

## 1. 平台願景

**Chorde**（Cluster + Horde）旨在建立一個「去中心化但高度協調」的基礎設施部落。截至 v0.3.0，本平台已從簡單的 IaC 腳本轉變為 **Operator 管理**的現代架構，實現了「以程式碼為環境，以文件為源頭」的 KDD 循環。

---

## 2. 儲存庫結構

Chorde 採用**遞迴式 GitOps v2** 架構，透過單一入口點（`root.yaml`）實現自動化編排。

```text
Chorde/
├── cluster/                 # [實體] 硬體與 OS 層級定義
│   └── k3han/               
│       ├── ansible/         # 操作記錄：節點初始化與作業系統強化
│       └── k3s/             # 節點描述符：K3s 設定備份
│
├── gitops/                  # [狀態] GitOps 預期狀態（SSOT）
│   └── k3han/               
│       ├── root.yaml        # 入口點：根應用程式
│       ├── stages/          # [第 0 層：編排器] 基於階段的 ApplicationSet
│       │   ├── 00-bootstrap.yaml  # 核心：ArgoCD、SealedSecrets、Ingress
│       │   ├── 01-platform.yaml   # 維運：監控、日誌、Operator
│       │   └── 02-components.yaml # 應用：資料庫、訊息佇列、SafeZone 微服務
│       │
│       └── manifests/       # [內容] 宣告式資源（YAML/Helm）
│           ├── alloy/       # 多重來源模式
│           ├── cnpg-*/      # CloudNativePG Operator 與叢集
│           └── ...          # 20+ 平台服務
│
├── scripts/                 # [生命週期] 維運與驗證工具
│   ├── ops/                 # bootstrap-cluster.sh、seal.sh
│   └── test/                # 跨區域連線與健康檢查
│
└── legacy/                  # [歸檔] 歷史設定（v0.1.x / v0.2.x）
```

---

## 3. 核心元件導覽

### 3.1 執行時期叢集
*   [**K3han（混合 K3s）**](safechord.chorde.k3han.md) ⭐：
    *   **範圍**：高度不對稱的台灣－日本混合雲。
    *   **狀態**：運行 K3s v1.34+，利用 Tailscale SDN 掩蓋地理延遲。

---

## 4. 工程實踐（v2）

Chorde 嚴格遵循下列 SRE 原則：

1.  **ArgoCD 多重來源**：捨棄本機 `helm-charts/` 副本。直接參考上游 Helm Charts，並搭配本地 `values-custom.yaml` 覆蓋。
2.  **ApplicationSet 模式**：以 `ApplicationSet` 取代單體式的 `Application` 清單，實現自動服務發現與分層同步（Sync Waves）。
3.  **Operator 優先**：基礎服務（資料庫、Kafka、Postgres）完全由 **Operator 管理**，確保自我修復與零停機升級。
4.  **可用性層級**：利用 Taints（`PreferNoSchedule`）在本地端與雲端節點之間建立可用區域，避免關鍵工作負載落到非 HA 節點上。
5.  **測試驅動維運**：主要的設定變更必須透過 `scripts/test/` 中的腳本驗證，以符合「測試即法規」原則。

---

## 5. 快速存取

*   **叢集地圖**：[K3han 混合叢集地圖](safechord.chorde.k3han.md)
*   **排程邏輯**：[K3han 排程大腦](safechord.chorde.k3han.scheduling.md)
*   **原始碼**：[SafeChord/Chorde (GitHub)](https://github.com/SafeChord/Chorde)