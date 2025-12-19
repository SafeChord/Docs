---
title: "K3Han: Custom Scheduling Considerations for K3s"
doc_id: safechord.chorde.k3han.scheduling
version: "0.2.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔探討在使用 K3Han 管理的 K3s 集群中進行自定義調度的考量因素和策略，包括節點親和性、污點與容忍、以及其他影響 Pod 分配的高級調度技術。"
keywords:
  - K3Han
  - K3s
  - Kubernetes
  - custom scheduling
  - pod scheduling
  - node affinity
  - taints and tolerations
  - resource allocation
  - SafeChord
logical_path: "SafeChord.Chorde.K3Han.Scheduling"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.chorde.k3han.md"
  - "safechord.chorde.k3han.cluster.md"
  - "safechord.chorde.k3han.changelog.md"
parent_doc: "safechord.chorde.k3han"
tech_stack:
  - K3s
  - Kubernetes
---
**# 🧭 Scheduling - 調度策略與資源分層邏輯**

> 本頁記錄 K3han Cluster v0.2.0 的節點屬性、模組調度原則與 affinity/taint 策略。
>
> 本版相較 v0.1.0 精簡節點來源，移除多個 cloud 測試節點，改為以高效能 control-plane + 單一 ingress + 本地展示組成核心三角結構，調度邏輯也因此大幅更新。

---

**## 🏷️ Label 標籤定義**

| Label Key  | 範例值                   | 說明                   |
| ---------- | --------------------- | -------------------- |
| `region`   | `jp, tw`              | 地理區域，影響網路延遲與部署優先順序   |
| `tier`     | `low, medium, high`   | 運算能力等級，用於 Pod 排程評估   |
| `avail`    | `24/7, on-demand`     | 可用性，決定關鍵服務調度         |
| `provider` | `contabo, gce, local` | 節點來源，對應部署來源（地端 / 雲端） |

---

**## 📌 節點 Role 與 Label 配置**

### **節點 Role 設定**

| Node Name         | Role                | 說明                            |
| ----------------- | ------------------- | ----------------------------- |
| **ct-serv-jp**    | `control-plane`     | K3s 控制層節點，承載大部分核心服務           |
| **gce-agent-tw**  |                     | 公網進入點，僅作為 HTTP proxy 使用       |
| **acer-agent**    |                     | 開發主機、展示節點，承載 SafeZone 與部分監控模組 |
| **laptop-agent**  |                     | 測試用節點，保留中低頻開發實驗用途             |
| **desktop-agent** |                     | 高運算資源但不常開機，預留未來 batch 處理用途    |

---

**## ⚙️ Taint / Toleration 與節點隔離設計**

| Node Name         | taint                                | 說明                          |
| ----------------- | ----------------------------------   | ------------------            |
| **ct-serv-jp**    | `role=control-plane:NoSchedule`      | 控制層，不接受非關鍵模組排程     |
| **gce-agent-tw**  | `purpose=proxy:NoSchedule`           | 僅供 ingress，不進行模組排程    |
| **acer-agent**    | `reliability=local:PreferNoSchedule` | 本地機器，具穩定性但避開核心服務 |
| **laptop-agent**  | `avail=on-demand:NoSchedule`         | 測試用途，預設不排程            |
| **desktop-agent** | `avail=on-demand:NoSchedule`         | 同上                           |

---

**### 節點 Label 設定**

| Node Name         | Labels                                                    | 說明                 |
| ----------------- | --------------------------------------------------------- | ------------------ |
| **ct-serv-jp**    | `region=jp, tier=medium, avail=24/7, provider=contabo`      | 高性能雲端節點，為主控節點      |
| **gce-agent-tw** | `region=tw, tier=low, avail=24/7, provider=gce`           | 較弱 GCP 免費型節點，負責進入點 |
| **acer-agent**    | `region=tw, tier=medium, avail=24/7, provider=local`      | 穩定的地端節點，擔任開發與主展示環境 |
| **laptop-agent**  | `region=tw, tier=medium, avail=on-demand, provider=local` | 筆電節點，測試與備援用途       |
| **desktop-agent** | `region=tw, tier=high, avail=on-demand, provider=local`   | 家用高規節點，運算實驗用途      |

---

**## 📦 模組部署原則（靜態配置階段）**

| 模組                         | 部署節點       | 策略簡述                         | 部署分類  |
| -------------------------- | ---------- | ---------------------------- | ----- |
| PostgreSQL Primary         | ct-serv-jp | 高效能節點，供全系統統一查詢與資料寫入          | cloud |
| PostgreSQL Replica         | acer-agent | 本地同步查詢副本，降低主節點壓力             | local |
| SafeZone API               | acer-agent | 與 PostgreSQL Replica 同區，降低延遲 | local |
| Redis Cache                | acer-agent | 本地使用者最靠近，速度最佳                | local |
| Dashboard                  | acer-agent | UI 展示端點，預設由 ingress proxy 進入 | local |
| CLI Relay                  | acer-agent | 本地 CLI 控制與資料注入入口             | local |
| Prometheus / Loki / ArgoCD | ct-serv-jp | 控制層工具與監控模組統一部署               | cloud |

---

**## 🧩 Affinity 與 Topology Spread 應用示例（v0.2.0）**

```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: tier
        operator: NotIn
        values:
          - low
      - key: avail
        operator: In
        values:
          - 24/7
```

> 本策略針對持續運作型模組設計，排除 ingress 與 on-demand 節點。

---
