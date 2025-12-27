# 📚 SafeChord Documentation Hub
[![Methodology: KDD](https://img.shields.io/badge/Methodology-KDD-blueviolet?style=for-the-badge)](docs/safechord.kdd.introduction.md)
[![Powered By: MkDocs](https://img.shields.io/badge/Powered_By-MkDocs-blue?style=for-the-badge)](https://www.mkdocs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Single Source of Truth (SSOT)** for the SafeChord Ecosystem.

This repository serves as the central knowledge base for the SafeChord project. It adopts the **Knowledge-Driven Development (KDD)** methodology, treating documentation not just as a reference, but as the **executable specification (Prompt Code)** that drives AI Agents (Gemini, Cline) to generate code and infrastructure configurations.

---

## 🔗 The Ecosystem

SafeChord uses a **Twin-Repo Strategy** plus a dedicated PaaS layer. This documentation hub connects them all:

| Repository | Role | Description |
| :--- | :--- | :--- |
| **[🟦 SafeZone](../SafeZone)** | **Application** | The microservices source code, business logic, and data pipelines (Kafka/FastAPI). |
| **[🟨 SafeZone-Deploy](../SafeZone-Deploy)** | **Delivery** | Helm Umbrella Charts and GitOps configurations for Preview/Staging environments. |
| **[🟥 Chorde](../Chorde)** | **Platform** | The underlying Kubernetes (K3s) clusters and platform services (DB, MQ). |
| **[⬜ Docs](.)** | **Knowledge** | **(You are here)** The master plan, security policies, and architectural specs. |

---

## 🧠 Knowledge Navigation

Before writing any code, we define it here.

*   **🗺️ [Knowledge Map (Start Here)](docs/safechord.knowledgetree.md)**: The global navigation guide to all documents.
*   **🛡️ [Security Architecture](docs/safechord.security.md)**: The "Constitution" of the project—SecretOps, RBAC, and Network Policies.
*   **🌍 [Environment Evolution](docs/safechord.environment.md)**: Understanding the "Trinity" (Local -> Preview -> Staging).
*   **🤖 [KDD Methodology](docs/safechord.kdd.introduction.md)**: How we collaborate with AI Agents.

---

## 🚀 Quick Start (Local Preview)

This site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). You can run it locally to browse the knowledge graph.

### 1. Install Dependencies
```bash
pip install mkdocs-material
```

### 2. Run Dev Server
```bash
mkdocs serve
```
Open `http://127.0.0.1:8000` in your browser.

---

## 🤝 Contribution & Workflow

We follow a strict **"Doc-First"** policy driven by KDD:

1.  **Update the Spec**: Before changing any code in `SafeZone` or `SafeZone-Deploy`, update the corresponding specification file in `docs/`.
2.  **Align with AI**: Use these documents as the context prompt for your AI coding assistant.
3.  **Verify**: Ensure `safechord.knowledgetree.md` accurately reflects the new structure.

For detailed collaboration rules, please read **[KDD Practice](docs/safechord.kdd.practice.md)**.

## 📄 License

This project is licensed under the MIT License.
