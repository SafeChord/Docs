---
title: Security Architecture & Governance
status: active
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
*   **Dependency Management**: Each sealed secret carries `argocd.argoproj.io/sync-wave: "-1"`, a resource's wave inside its Application, so the secrets are ready before the workloads beside them start.
*   **Sealing Keys**: Automatic key renewal is disabled, so the controller's key set stays fixed. The set is backed up by hand, so one off-cluster backup has to cover every key a `SealedSecret` in Git may be sealed with. That holds only while renewal stays off. The renewal setting itself lives in the controller's Helm values in Chorde.
*   **Key Backup & Restore**: The key Secrets (label `sealedsecrets.bitnami.com/sealed-secrets-key` in the `bootstrap` namespace) are backed up in the Architect's Bitwarden vault, off the cluster and out of Git. Whoever holds this backup and can read the repositories can decrypt every secret. A rebuilt cluster gets the backed-up key Secrets applied into `bootstrap` before the controller starts, or the controller is restarted after they are applied. Otherwise it generates a fresh key, and none of the `SealedSecret`s in Git can be unsealed.

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
*   **Origin Hardening (GCP Firewall)**: GCP VPC firewall rules are configured to restrict ingress traffic to the public edge node (`gce-agent-tw`), allowing ONLY requests originating from **Cloudflare IP ranges**.
*   **Impact**: Prevents attackers from bypassing Cloudflare's WAF and DDoS protection by connecting directly to the origin's public IP.

### 3.2 Transport Layer Security (TLS)
*   **Cloudflare Full (Strict) Mode**: We enforce end-to-end (E2E) TLS encryption.
*   **Origin CA Certificates**: Cloudflare-issued Origin CA certificates are deployed within the K3s cluster, ensuring the integrity of the connection between the proxy and the origin.

### 3.3 Perimeter Policy
*   **Public Zone**: Traffic must transit through the Cloudflare Proxy. Implementation: the `public-gateway` data plane, with routes bound to it as Gateway API `HTTPRoute`s.
*   **Private Zone**: Access goes through an in-cluster Cloudflare Tunnel behind Cloudflare Access; the Tailscale mesh is the break-glass path only. Implementation: the `private-gateway` data plane, a `ClusterIP` Service.

---

## ⛓️ 4. Supply Chain Security

*   **Image Provenance**: We only trust container images automatically built and pushed to the **GitHub Container Registry (GHCR)** via verified GitHub Actions workflows.
*   **Dependency Pinning**: All Helm chart dependencies and container base images are pinned to specific version tags to prevent risks introduced by upstream updates.
