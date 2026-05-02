---
title: 'Policy: Ingress & Network Perimeter'
doc_id: safechord.chorde.k3han.ingress
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-05-02'
summary: Defines the stratified ingress strategy for the K3han cluster. Covers isolation between public and private channels, GCP firewall hardening, and the enforcement of Full (Strict) TLS encryption.
keywords:
  - Ingress Policy
  - Zero Trust
  - Cloudflare Full (Strict)
  - GCP Firewall
  - Dual-Channel
logical_path: SafeChord.Chorde.K3han.Networking.Ingress
related_docs:
  - safechord.chorde.k3han.md
  - safechord.chorde.k3han.cluster.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests/ingress-nginx
  - Chorde/cluster/k3han/ansible/roles/firewall
tech_stack:
  - Kubernetes Ingress-Nginx
  - Cloudflare Tunnel
  - Cloudflare Origin CA
doc_version: 0.3.5
app_version: 0.3.0
---

# Ingress & Network Policy (Brain)

> **Strategic Focus**: Defense in Depth, Origin Hardening, and end-to-end encryption.

---

## 1. Strategy Overview

SafeChord employs a **Stratified Ingress Strategy** combining GCP infrastructure, Cloudflare CDN, and Nginx controllers to build a layered defense system.

*   **Public Channel**: Services users via Cloudflare WAF + GCP Firewall IP locking.
*   **Private Channel**: Reserved for ops/admin, exposed ONLY via the Tailscale virtual mesh.

### Detailed Traffic Flow
```mermaid
graph LR
    %% Styles
    classDef public fill:#e3f2fd,stroke:#1565c0;
    classDef private fill:#e8f5e9,stroke:#2e7d32;
    classDef k8s fill:#fff,stroke:#333;

    User(User):::public
    Admin(Admin):::private
    
    subgraph K3han [K3han Cluster]
        direction TB
        
        subgraph Agent ["GCE Edge (TW)"]
            direction TB
            GCP_FW["GCP Firewall<br/>(CF IP Allowlist)"]:::public
            PubIng["nginx-public<br/>HostPort: 80/443"]:::public
        end

        subgraph Master ["Contabo Core (JP)"]
            PrivIng["nginx-private<br/>Tailscale Interface Only"]:::private
        end
        
        App(SafeZone App):::k8s
        Ops(ArgoCD/Prometheus):::k8s
    end

    User -->|"Cloudflare Proxy"| GCP_FW
    GCP_FW -->|"Authorized Source"| PubIng
    PubIng -->|"Route"| App
    
    Admin -->|"Tailscale VPN"| PrivIng
    PrivIng -->|"Internal Route"| Ops
```

---

## 2. Channel Specifications

### 2.1 Public Channel (`nginx-public`)
*   **Ingress Class**: `nginx-public` (Isolated controller).
*   **Origin Hardening**: Nodes are tagged as `ingress-public`. GCP VPC rules allow ONLY Cloudflare CIDR blocks to access 80/443, **blocking 100% of direct IP attacks**.
*   **SSL Policy**: **Full (Strict)**. End-to-end encryption with Cloudflare-issued Origin CA certificates deployed within the cluster.
*   **Security Layering**: Combines global token verification with specific **Basic Authentication** for internal mock services (e.g., `echo-server`).

### 2.2 Private Channel (`nginx-private`)
*   **Ingress Class**: `nginx-private` (Hidden by default).
*   **Listen Mode**: `HostNetwork + Tailscale`. Binds exclusively to the Tailscale virtual NIC (100.x.x.x), making it **inaccessible from the public internet**.

---

## 3. Security & Connectivity Verification Log

> 💡 **Behavioral Snapshot**: The following table consolidates the routing and authentication behaviors verified against the GitOps manifests (as of v0.3.0).

| Subject | Access Path | Access Method | Expected Behavior | Actual Result |
| :--- | :--- | :--- | :--- | :--- |
| **Origin IP** | `http://<GCE_IP>:80` | Direct Public IP | ❌ Blocked by GCP Firewall | Timeout |
| **echo-server** | `/echo` | CF Domain Name | ❌ Identity Challenge | 401 Unauthorized |
| **echo-server** | `/echo` | With Basic Auth | ✅ Successful Access | 200 OK |
| **echo-server** | `/echo?token=5566`| With Token | ✅ Higher Priority Auth | 401 (Basic Auth Required) |
| **Private UI** | `/nginx` | Tailscale IP | ✅ Authorized Access | 200 OK |

---

## 4. Operational Maintenance

*   **Protecting New Services**: Apply the `kubernetes.io/ingress.class: "nginx-public"` annotation and reference the appropriate `SealedSecret` for Basic Auth.
*   **Firewall Updates**: Ansible playbooks in `Chorde/cluster/` automate the synchronization of the GCP Firewall with Cloudflare's rotating IP ranges.

---

## 5. References
*   **Networking Submodule**: `Chorde/gitops/k3han/manifests/argocd/`
*   **GCP Config**: `Chorde/cluster/k3han/ansible/roles/firewall/`
