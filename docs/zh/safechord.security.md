---
title: Security Architecture & Governance
doc_id: safechord.security
last_updated: '2026-03-09'
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: Global
summary: 定義 SafeChord 的多層級安全治理準則。涵蓋基於 SealedSecrets 的機密管理、最小權限控制 (RBAC)、GCP 防火牆硬化以及端到端加密策略。
keywords:
  - Security
  - SecretOps
  - SealedSecrets
  - Cloudflare Full (Strict)
  - Origin Hardening
  - Basic Auth
  - IAM
  - NetworkPolicy
logical_path: SafeChord.Security
related_docs:
  - safechord.environment.md
  - safechord.safezone.deployment.md
  - safechord.chorde.k3han.ingress.md
parent_doc: safechord
doc_version: 0.2.2
archetype: brain
---

# 🛡️ 安全架構與治理 (Security Architecture & Governance)

> *"Security is not an afterthought; it is the foundation of trust."*

在 SafeChord 的開發流程中，我們落實 **Security-by-Design**，在混合雲環境中構建一套 **縱深防禦 (Defense in Depth)** 體系，確保從基礎設施到應用層均具備多重防護機制。

---

## 🔐 1. 機密管理 (SecretOps Strategy)

我們採用 **GitOps 原生** 的機密管理策略，解決將敏感憑證納入版本控制 (Version Control) 的安全挑戰。

### 核心技術：SealedSecrets
我們選用 Bitnami SealedSecrets 實作非對稱加密機制，確保機密僅在叢集內部可見：
*   **SealedSecrets**: 確保敏感憑證（如資料庫密碼、Basic Auth 認證）能安全地儲存於公有 Git 倉庫。
*   **部署流程**：開發者於本地加密，ArgoCD 於運行時解密。透過 `argocd.argoproj.io/sync-wave: "-1"` 確保 Secret 在應用程式啟動前就緒。

---

## 👤 2. 身分與存取控制 (IAM & RBAC)

我們嚴格遵循 **最小權限原則 (Principle of Least Privilege)**，並透過細緻的 RBAC 策略落實於 CI/CD 流水線中。

### CI/CD 權限隔離 (Scoped Workload Identity)
*   **環境 SA 隔離**：每個環境建立專用的 ServiceAccount，僅允許管理該 Namespace 內的資源，嚴禁跨 Namespace 操作。
*   **動態憑證**：CI 流程執行時請求短時效 Token (2 小時)，過期自動失效。

### 應用層存取控制
*   **人機識別**：針對內部測試工具 (如 `echo-server`) 實施 **Basic Authentication**，並將機密納入 SealedSecrets 管理。

---

## 🌐 3. 網路安全與入口硬化 (Network Security)

我們採用 **三維防禦 (Triple-Lock Defense)** 策略，在網路層實現物理與邏輯隔離。具體的 Ingress 配置請參閱 **[K3Han Ingress Configuration](safechord.chorde.k3han.ingress.md)**。

### 3.1 基礎設施硬化 (Infrastructure Layer)
*   **Origin Hardening (GCP Firewall)**：
    *   透過 GCP VPC 防火牆規則，限制只有來自 **Cloudflare 已知 IP 網段** 的流量能進入 `ingress-public` 節點。
    *   **防護效果**：防止攻擊者繞過 WAF 與 DDoS 防護直連 Origin IP。

### 3.2 傳輸層加密 (Transport Layer)
*   **Cloudflare Full (Strict) Mode**：
    *   強制實施端到端 (E2E) TLS 加密。
    *   **Origin CA 憑證**：於 K3s 叢集內部部署 Cloudflare 簽發的 Origin CA，確保連線對象的誠信。

### 3.3 邊界防護策略 (Perimeter Policy)
*   **公網層 (Public Zone)**：強制流量經過 Cloudflare Proxy。實作對應：`IngressClass: nginx-public`。
*   **內網層 (Private Zone)**：存取必須經過 **Tailscale Overlay VPN**。實作對應：`IngressClass: nginx-private`。

---

## ⛓️ 4. 供應鏈安全 (Supply Chain Security)

*   **映像檔誠信 (Image Provenance)**：僅信任由 GitHub Actions 自動建置並推送至 **GHCR** 的映像檔。
*   **相依性鎖定 (Dependency Pinning)**：所有的 Helm 依賴均需鎖定確切版本號，防止上游更新引入風險。
