---
title: 'Blueprint: K3han Monitoring Stack'
doc_id: safechord.chorde.k3han.monitoring
status: active
authors:
  - bradyhau
  - Gemini 3.5 Pro (Architecture Architect)
context_scope: Chorde/gitops/k3han/manifests/monitoring
summary: 定義 K3han 混合雲叢集的可觀測性架構。本規範詳細說明了指標堆疊、日誌加密存儲與異質化採集代理的設計決策與安全規範。
keywords:
  - Monitoring Architecture
  - Observability
  - Prometheus Operator
  - Loki S3
  - Grafana
  - Zero Trust
logical_path: SafeChord.Chorde.K3han.Monitoring
related_docs:
  - safechord.chorde.k3han.md
  - safechord.security.md
parent_doc: safechord.chorde.k3han
archetype: blueprint
code_paths:
  - Chorde/gitops/k3han/manifests/prometheus
  - Chorde/gitops/k3han/manifests/loki
  - Chorde/gitops/k3han/manifests/alloy
  - Chorde/gitops/k3han/manifests/fluent-bit
doc_version: 0.3.2
app_version: 0.3.0
---

# 📊 Monitoring Stack (Architecture Specification)

> **Blueprint (藍圖型)**：定義 K3han 混合雲叢集的可觀測性 (Observability) 實作標準。
> *核心理念：分散式採集、雲端化存儲、零信任存取。*

## 1. 架構決策與設計願景 (Design Rationale)
在跨國、異質節點的混合雲環境中，傳統的單體監控面臨資料一致性與本地 IO 瓶頸。K3han 採用以下策略達成 **MVA (Minimum Viable Architecture)**：

*   **雲端化日誌後端 (S3-Offloading)**：為了解決邊緣節點硬碟 I/O 限制與長期留存成本，日誌數據被非同步推送至物件存儲 (Object Storage)，實現地端節點的「零留存 (Zero-Local-Footprint)」目標。
*   **異質採集代理 (Heterogeneous Agents)**：
    *   **Alloy (Power Agent)**：部署於高效能節點，利用其強大的邏輯處理能力進行複雜的 Relabeling 與多維度標籤提取。
    *   **Fluent-bit (Lightweight Agent)**：部署於資源受限節點，確保在極低資源消耗下完成日誌推送。
*   **GitOps 驅動與分層部署**：利用 ArgoCD `ApplicationSet` 與 `sync-wave` 確保監控基礎設施 (Operators) 優先於服務實例 (Instances) 啟動。

## 2. 指標監控：Prometheus Stack (Metrics)
基於 `kube-prometheus-stack` 構建的自動化監控體系。

### 部署與可靠性規範
*   **Namespace**: `monitoring` (受網路隔離策略保護)。
*   **Storage Strategy**: 採用 10Gi Local PV 作為快取，設定 7 天 (7d) 的指標留存，平衡運維除錯需求與存儲開銷。
*   **Orchestration**: `sync-wave: "1"`。確保 Prometheus Operator 在所有應用部署前已完成 CRD 註冊。

### Grafana 存取與入口安全性 (Edge Gating)
*   **Ingress Class**: `nginx-private` (僅限內網/VPN 存取)。
*   **Zero-Trust Layer**: 強制整合 Cloudflare Access (OIDC/MFA)，確保管理介面完全不暴露於公網。
*   **Sub-path Configuration**: 啟用 `serve_from_sub_path: true`，將 Grafana 隱蔽於 `${GRAFANA_ROOT_URL}/grafana/` 下，增加探針掃描難度。

## 3. 日誌分析：Loki (Logs)
採用 `SingleBinary` 模式並搭配雲端物件存儲，達成高擴展性與低維護成本。

### 存儲架構：冷熱分離 (Cloud-Native Storage)
*   **Ingestion Path**: 
    1. Agent 採集 -> 2. Loki (Single Binary) -> 3. Object Storage (S3)。
*   **Object Store**: 使用 Amazon S3 (`${LOKI_S3_REGION}`)。
*   **Credential Masking**: 所有 S3 存取憑證均透過 `SealedSecrets` 加密，並以 `SecretKeyRef` 注入 Pod 環境變數，落實 **Credential-less Configuration**。

## 4. 採集代理標準 (Collection Standard)
所有日誌必須結構化為具備可檢索性的標籤。

### 標籤正規化 (Label Normalization)
採集代理必須自動提取並格式化以下標籤：
*   `namespace`: K8s 命名空間。
*   `pod`: Pod 名稱。
*   `container`: 容器名稱。
*   `node_name`: 具體物理節點 ID。
*   `job`: 採集源分類 (例如 `alloy` 或 `fluent-bit`)。

### 安全清理規則 (Log Sanitization)
*   **Sensitive Data Dropping**: 採集代理層級配置正則過濾規則，自動丟棄包含 `password`, `bearer token`, `api_key` 等敏感關鍵字的日誌行。

## 5. 可觀測性運維 (Operations)
*   **LogCLI**: 提供 SRE 命令行式的日誌檢索能力。
*   **ServiceMonitor / PodMonitor**: 應用程式監控對象由 `SafeZone-Deploy` 定義，`Chorde` 負責提供基礎設施。
*   **Auditability**: 監控配置的每一次變更均需經過 GitOps 審核，並記錄於 [Changelog](safechord.chorde.k3han.changelog.md)。
