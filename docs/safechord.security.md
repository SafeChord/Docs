---
title: Security Architecture & Governance
doc_id: safechord.security
version: 0.2.0
last_updated: "2026-01-02"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Global"
summary: "定義 SafeChord 的安全治理準則。涵蓋基於 SealedSecrets 的機密管理、最小權限控制 (RBAC) 以及基於 Google OAuth2 的 API 安全接入策略。"
keywords:
  - Security
  - SecretOps
  - SealedSecrets
  - OAuth2
  - IAM
  - NetworkPolicy
logical_path: "SafeChord.Security"
related_docs:
  - "safechord.environment.md"
  - "safechord.safezone.deployment.charts.md"
  - "safechord.chorde.k3han.ingress.md"
parent_doc: "safechord"
---

# 🛡️ 安全架構與治理 (Security Architecture & Governance)

> *"Security is not an afterthought; it is the foundation of trust."*

在 SafeChord 的開發流程中，安全不是外掛的功能，而是架構的基石。我們的目標是落實 **Security-by-Design**，在混合雲環境的資源限制下，構建一套符合 **縱深防禦 (Defense in Depth)** 原則的安全體系，專注於解決「機密生命週期管理」與「零信任存取控制」兩大核心議題。

---

## 🔐 1. 機密管理 (SecretOps Strategy)

我們採用 **GitOps 原生** 的機密管理策略，解決將敏感憑證納入版本控制 (Version Control) 的安全挑戰。

### 核心技術：SealedSecrets
我們選用 Bitnami SealedSecrets 實作非對稱加密機制，確保機密僅在叢集內部可見：
*   **公鑰 (Public Key)**：公開分發。開發者使用公鑰將原始 Secret 封裝為 `SealedSecret` CRD，此過程不可逆。
*   **私鑰 (Private Key)**：僅存於 K8s 控制平面的 Controller 內部，負責在運行時解密並還原 Secret。

### 部署流程 (Deployment Flow)
為降低自動化帶來的潛在曝露風險，我們採取 **受控注入 (Controlled Injection)** 模式：
1.  **加密 (Seal)**：開發者於本地環境使用 `kubeseal` 加密敏感配置。
2.  **提交 (Commit)**：將加密後的 `SealedSecret` 資源提交至 Git 倉庫。
3.  **注入 (Inject)**：透過 GitHub Actions 執行部署腳本，將 `SealedSecret` 一次性應用至目標 Namespace。
4.  **還原 (Unseal)**：叢集內的 Controller 自動解密並建立原生的 Kubernetes Secret 供應用程式掛載。

### 環境差異策略
*   **Preview 環境**：使用開發專用的 Key Pair，優先考量開發效率與輪替 (Rotation) 的便利性。
*   **Staging 環境**：實施嚴格的密鑰管控（私鑰不離群）。此外，我們在此環境強制實施 **額外的使用者帳號隔離**，確保即便基礎設施層遭受滲透，業務資料層仍保有最後一道防線。

---

## 👤 2. 身分與存取控制 (IAM & RBAC)

我們嚴格遵循 **最小權限原則 (Principle of Least Privilege)**，並透過細緻的 RBAC 策略落實於 CI/CD 流水線中。

### CI/CD 權限隔離 (Scoped Workload Identity)
我們摒棄將 Admin 權限授予 CI 系統的做法，而是為每個環境建立專用的 ServiceAccount (`*-ci-sa`)，並嚴格限制其作用域：

*   **Preview Deployer (`safezone-preview-ci-sa`)**：
    *   `gitops` Namespace：僅允許管理 ArgoCD 的 `Application` CRD。
    *   `safezone-preview` Namespace：僅允許寫入 `SealedSecret`。
    *   **權限邊界**：嚴格禁止跨 Namespace 存取或修改 Cluster 層級配置。

*   **Staging Deployer (`safezone-ci-sa`)**：
    *   `safezone` Namespace：僅允許 **讀取** `Job` 狀態（用於確認遷移任務完成），嚴禁直接修改部署配置。

### 動態憑證管理 (On-Demand Credentials)
為消除長期憑證 (Long-lived Credentials) 的洩漏風險，我們實作了動態憑證機制：
*   **即時生成**：CI 流程執行時，動態請求短時效 Token。
*   **自動過期**：Token 有效期限制為 2 小時，任務結束後憑證即刻失效。
*   **受限上下文**：生成的 Kubeconfig 僅綁定上述受限的 ServiceAccount，即使外洩，攻擊者也無法進行破壞性操作。

### 人員存取控制 (Human Access)
*   **禁止直連**：開發者原則上不直接存取 Staging Cluster。所有的變更必須透過 PR，經由代碼審查後自動化部署。
*   **緊急破窗 (Emergency Access)**：
    *   **Level 1**：透過 `cli-relay` 進行受控操作，強制要求 **Google OAuth2** 身分驗證。
    *   **Level 2**：極端情況下透過 Tailscale VPN 進行，所有操作均保留完整的 Audit Log 以供稽核。

---

## 🌐 3. 網路安全 (Network Security)

我們採用 **雙層邊界 (Dual Perimeter)** 策略，在網路層實現物理隔離。具體的 IngressClass 配置與測試矩陣，請參閱 **[K3Han Ingress Configuration](safechord.chorde.k3han.ingress.md)**。

### 邊界防護策略 (Perimeter Policy)
*   **公網層 (Public Zone)**：
    *   僅暴露面向終端使用者的必要入口（如 Dashboard）。
    *   強制流量經過 Cloudflare Proxy 進行 DDoS 防護與 SSL 卸載。
    *   **實作對應**：`IngressClass: nginx-public`

*   **內網層 (Private Zone)**：
    *   所有管理介面（ArgoCD, Grafana, Prometheus）嚴禁直接暴露於公網。
    *   存取必須經過 **Tailscale Overlay VPN** 或經由 **Cloudflare Tunnel** 驗證的通道。
    *   **實作對應**：`IngressClass: nginx-private`

### 內部網段隔離 (Internal Segmentation)
*   **Namespace 隔離**：Preview 環境使用動態生成的 Namespace，確保測試過程的資源隔離。
*   **服務發現限制**：應用程式僅能存取當前 Namespace 內的資源，或經由 `ExternalName` 明確定義的平台級服務。

---

## ⛓️ 4. 供應鏈安全 (Supply Chain Security)

*   **映像檔誠信 (Image Provenance)**：僅信任 **GitHub Container Registry (GHCR)**。所有 Image 必須由受信任的 CI 流程自動建置，嚴禁開發者從本地環境直接推送至生產倉庫。
*   **相依性鎖定 (Dependency Pinning)**：所有的 Helm 依賴（如 Redis, Kafka）均需鎖定確切版本號，防止上游意外更新引入的潛在風險或供應鏈攻擊。