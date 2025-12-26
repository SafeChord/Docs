---
title: Security Architecture & Governance
doc_id: safechord.security
version: 0.1.0
last_updated: "2025-12-26"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Global"
summary: "定義 SafeChord 全域的安全架構準則。涵蓋 GitOps 機密管理 (SecretOps)、身分存取控制 (IAM)、網路邊界防護與供應鏈安全策略。"
keywords:
  - Security
  - SecretOps
  - SealedSecrets
  - RBAC
  - IAM
  - NetworkPolicy
logical_path: "SafeChord.Security"
related_docs:
  - "safechord.environment.md"
  - "safechord.safezone.deployment.charts.md"
parent_doc: "safechord"
---

# 🛡️ 安全架構與治理 (Security Architecture & Governance)

> *"Security is not an afterthought; it is the foundation of trust."*

本文件定義了 SafeChord 生態系中跨 Repo (App & Infra) 共同遵守的安全準則。我們的目標是建立一個 **Security-by-Design** 的系統，在保持開發速度的同時，確保「機密不外洩」與「權限最小化」。

---

## 🔐 1. 機密管理 (SecretOps Strategy)

我們採用 **GitOps 友善** 的機密管理策略，解決 "如何在公開/私有的 Git 倉庫中安全地儲存密碼" 這一經典難題。

### 核心技術: SealedSecrets
*   **工具**: Bitnami SealedSecrets
*   **機制**: 非對稱加密 (Asymmetric Encryption)。
    *   **公鑰 (Public Key)**: 開放給所有開發者。用於將敏感資訊 (Secret) 加密成 `SealedSecret` CRD。
    *   **私鑰 (Private Key)**: 僅存在於 K8s Cluster 的 Controller 內部。用於解密並還原 Secret。

### 操作流程
1.  **加密**: 開發者在本地使用 `kubeseal` 工具將 `db-password.yaml` 加密為 `sealed-db-secret.yaml`。
2.  **提交**: 將 `sealed-db-secret.yaml` 提交至 Git 倉庫 (`SafeZone-Deploy` 或 `Chorde`)。
3.  **部署**: ArgoCD 同步 CRD 到叢集。
4.  **解密**: 叢集內的 SealedSecrets Controller 自動解密並建立原生的 Kubernetes Secret。

### 環境差異
*   **Preview 環境**: 使用開發專用的 Key Pair (安全性較低，方便輪替)。
*   **Staging 環境**: 使用嚴格管控的 Key Pair (僅由管理員持有私鑰備份)。

---

## 👤 2. 身分與存取控制 (IAM & RBAC)

我們遵循 **最小權限原則 (Principle of Least Privilege)**，嚴格限制「人」與「程式」的權限。

### Workload Identity (程式的權限)
*   **預設關閉**: 所有 Helm Chart 的 `automountServiceAccountToken` 預設設為 `false`。應用程式不應無故取得 K8s API 存取權。
*   **例外管理**: 僅有特定的管理工具 (如 `cli-relay`) 會被賦予明確定義的 RBAC Role (例如 `edit` 或 `view` 特定 Namespace)。

### Human Access (人的權限)
*   **No Direct Access**: 原則上，開發者不直接操作 Staging Cluster。所有的變更都必須透過 Git PR 經由 ArgoCD 同步。
*   **Emergency Access**:
    *   **Level 1**: 透過 `cli-relay` 提供的受限 API 進行操作。
    *   **Level 2**: 透過 Tailscale VPN 進行 Break-glass (緊急破窗) 操作，所有操作皆留有 Audit Log。

---

## 🌐 3. 網路安全 (Network Security)

### 邊界防護 (Perimeter)
*   **Ingress**: 僅暴露必要的 HTTP/HTTPS 入口 (如 Dashboard)。所有 Ingress 資源必須綁定 TLS Certificate。
*   **API Gateway**: `cli-relay` 作為內網服務的統一入口，負責驗證請求者的身分 (Authentication)。

### 內部隔離 (Internal Segmentation)
*   **Namespace Isolation**: Preview 環境透過動態生成的 Namespace 進行完全隔離。
*   **Service Discovery**: 應用程式僅能透過 K8s DNS 解析同一 Namespace 或明確允許的 External Name 服務。

---

## ⛓️ 4. 供應鏈安全 (Supply Chain Security)

### 映像檔來源 (Image Provenance)
*   **Trusted Registry**: 僅信任 **GitHub Container Registry (GHCR)**。
*   **CI Build**: 所有 Docker Image 必須由 GitHub Actions 自動建置，禁止開發者從本地電腦直接 Push Image 到生產倉庫。

### 依賴管理
*   **Helm Dependencies**: 所有的 Chart 依賴 (如 Redis, Kafka) 均鎖定版本號 (Pinned Version)，防止上游更新導致供應鏈攻擊。
