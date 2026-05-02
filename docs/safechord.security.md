---
title: Security Architecture & Governance
doc_id: safechord.security
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Global
summary: Defines the multi-layered security governance principles for SafeChord. Covers GitOps-native secret management using SealedSecrets, Principle of Least Privilege (RBAC), GCP firewall hardening, and end-to-end encryption strategies.
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
doc_version: 0.3.5
archetype: brain
---

# Security Architecture & Governance

> *"Security is not an afterthought; it is the foundation of trust."*

SafeChord implements **Security-by-Design**, constructing a **Defense in Depth** system within a hybrid-cloud environment. We ensure multiple layers of protection from the physical infrastructure to the application layer.

---

## 🔐 1. Secret Management (SecretOps Strategy)

We employ a **GitOps-native** secret management strategy, addressing the challenge of including sensitive credentials in version control.

### Core Technology: SealedSecrets
We use Bitnami **SealedSecrets** to implement asymmetric encryption, ensuring that secrets are only decryptable within the target Kubernetes cluster:
*   **Workflow**: Developers encrypt secrets locally; ArgoCD synchronizes the encrypted `SealedSecret` manifests; the cluster-side controller decrypts them into standard Kubernetes `Secrets` at runtime.
*   **Dependency Management**: We use `argocd.argoproj.io/sync-wave: "-1"` to ensure all secrets are ready before the application starts.

---

## 👤 2. Identity & Access Control (IAM & RBAC)

We strictly follow the **Principle of Least Privilege (PoLP)**, implemented through fine-grained RBAC policies within our CI/CD pipelines.

### CI/CD Permission Isolation
*   **Scoped Workload Identity**: Every environment (Preview, Staging) has a dedicated `ServiceAccount` authorized only to manage resources within its specific namespace. Cross-namespace operations are strictly prohibited.
*   **Dynamic Credentials**: CI workflows request short-lived tokens (2-hour TTL) for cluster interaction, minimizing the impact of potential credential leaks.

### Application Layer Access
*   **Authentication**: Internal utility tools (e.g., test mocks or echo servers) are protected via **Basic Authentication**, with credentials managed through the SealedSecrets pipeline.

---

## 🌐 3. Network Security & Ingress Hardening

SafeChord utilizes a **Triple-Lock Defense** strategy to achieve physical and logical isolation at the network layer. For detailed configuration, refer to the [K3han Ingress Guide](safechord.chorde.k3han.ingress.md).

### 3.1 Infrastructure Hardening
*   **Origin Hardening (GCP Firewall)**: GCP VPC firewall rules are configured to restrict ingress traffic to the `ingress-public` nodes, allowing ONLY requests originating from **Cloudflare IP ranges**.
*   **Impact**: Prevents attackers from bypassing Cloudflare's WAF and DDoS protection by connecting directly to the origin's public IP.

### 3.2 Transport Layer Security (TLS)
*   **Cloudflare Full (Strict) Mode**: We enforce end-to-end (E2E) TLS encryption.
*   **Origin CA Certificates**: Cloudflare-issued Origin CA certificates are deployed within the K3s cluster, ensuring the integrity of the connection between the proxy and the origin.

### 3.3 Perimeter Policy
*   **Public Zone**: Traffic must transit through the Cloudflare Proxy. Implementation: `IngressClass: nginx-public`.
*   **Private Zone**: Access is restricted to the **Tailscale Overlay VPN**. Implementation: `IngressClass: nginx-private`.

---

## ⛓️ 4. Supply Chain Security

*   **Image Provenance**: We only trust container images automatically built and pushed to the **GitHub Container Registry (GHCR)** via verified GitHub Actions workflows.
*   **Dependency Pinning**: All Helm chart dependencies and container base images are pinned to specific version tags to prevent risks introduced by upstream updates.
