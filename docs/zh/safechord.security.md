# 安全架構與治理

> *「安全不是事後補救，而是信任的基礎。」*

SafeChord 採行 **Security-by-Design**（安全內建設計），在混合雲環境中構建 **縱深防禦（Defense in Depth）** 系統。從實體基礎設施到應用層，我們確保多層防護。

---

## 🔐 1. 機密管理（SecretOps 策略）

我們採用 **原生 GitOps** 的機密管理策略，解決將敏感憑證納入版本控制的挑戰。

### 核心技術：SealedSecrets
我們使用 Bitnami **SealedSecrets** 實作非對稱加密，確保機密只能在目標 Kubernetes 叢集中解密：
*   **工作流程**：開發人員在本機加密機密；ArgoCD 同步加密後的 `SealedSecret` 資源清單；叢集端的控制器在執行階段將其解密為標準的 Kubernetes `Secret`。
*   **相依性管理**：透過 `argocd.argoproj.io/sync-wave: "-1"` 確保所有機密在應用程式啟動前已就緒。

---

## 👤 2. 身分與存取控制（IAM & RBAC）

我們嚴格遵循**最小權限原則（Principle of Least Privilege, PoLP）**，並透過 CI/CD 管線中的精細 RBAC 政策來實現。

### CI/CD 權限隔離
*   **限域的 Workload Identity**：每個環境（Preview、Staging）都有專屬的 `ServiceAccount`，僅被授權管理其特定命名空間內的資源。禁止跨命名空間操作。
*   **動態憑證**：CI 工作流程請求短期令牌（TTL 2 小時）與叢集互動，將潛在憑證外洩的影響降至最低。

### 應用層存取
*   **認證**：內部公用工具（例如測試 mock 或 echo server）透過 **Basic Authentication** 保護，憑證由 SealedSecrets 管線管理。

---

## 🌐 3. 網路安全與 Ingress 強化

SafeChord 採用**三重鎖定防禦（Triple-Lock Defense）**策略，在網路層達成實體與邏輯隔離。詳細設定請參閱 [K3han Ingress 指南](safechord.chorde.k3han.ingress.md)。

### 3.1 基礎設施強化
*   **源站強化（GCP Firewall）**：設定 GCP VPC 防火牆規則，限制進站流量僅能到達 `ingress-public` 節點，且**僅允許**來自 **Cloudflare IP 範圍**的請求。
*   **影響**：防止攻擊者繞過 Cloudflare 的 WAF 與 DDoS 防護，直接連線至源站的公開 IP。

### 3.2 傳輸層安全（TLS）
*   **Cloudflare Full (Strict) 模式**：我們強制端到端（E2E）TLS 加密。
*   **源站 CA 憑證**：在 K3s 叢集中部署 Cloudflare 簽發的源站 CA 憑證，確保代理與源站之間連線的完整性。

### 3.3 邊界政策
*   **公開區域**：流量必須經過 Cloudflare Proxy。實作方式：`IngressClass: nginx-public`。
*   **私有區域**：僅限透過 **Tailscale Overlay VPN** 存取。實作方式：`IngressClass: nginx-private`。

---

## ⛓️ 4. 供應鏈安全

*   **映像來源可信**：我們只信任透過經驗證的 GitHub Actions 工作流程自動建置並推送至 **GitHub Container Registry (GHCR)** 的容器映像。
*   **相依性鎖定**：所有 Helm chart 相依項目與容器基礎映像均鎖定至特定版本標籤，以避免上游更新帶來的風險。