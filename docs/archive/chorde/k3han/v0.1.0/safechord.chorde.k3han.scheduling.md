---
version: v0.1.0
module: k3han
role: techdoc         
status: deprecated
summary: k3han 內節點工作分配及 K8S 節點屬性定義。
updated: 2024-05-09
submodule_versions: null
--- 
# 🧭 Scheduling - 調度策略與資源分層邏輯

> 本頁紀錄 K3han Cluster 中的節點屬性、模組調度原則與 affinity/taint 實作策略。
> 
> 
> K3han 雖小，但節點異質性強。為了讓每一個模組能在正確的地方、用適當的資源運行，我們定義了一套清晰的節點屬性與部署準則。
> 

---

## 🏷️ Label 標籤定義

| Label Key | 範例值 | 說明 |
| --- | --- | --- |
| `region` | `sin, tw` | 地理區域，影響網路延遲與部署優先順序 |
| `tier` | `low, medium, high` | 運算能力等級，用於 Pod 排程評估 |
| `avail` | `24/7, on-demand`  | 可用性，決定關鍵服務調度 |
| `provider` | `hetzner, gce, local` | 節點來源，對應部署來源（地端 / 雲端） |

> 上述 Label 搭配 nodeSelector、affinity、anti-affinity 等機制，構成彈性排程邏輯基礎。
> 

## **📌** 節點 Role 與 Label 配置

### **節點 Role 設定**

| Node Name | Role | 說明 |
| --- | --- | --- |
| **hz-serv-sin** | `control-plane` | K3s 控制平面節點，責任整個叢集的排程 |
| **acer-agent** | `infra` | 本地主要節點，提供 NFS、Redis 主服務
與大部分 infra 非關鍵元件 |

> 沒標示的節點 Role 為空。
> 

## ⚙️ Taint / Toleration 與節點隔離設計

| Node Name | taint | 說明 |
| --- | --- | --- |
| **hz-serv-sin** | `control-plane=true:NoSchedule
tier=low:NoSchedule` | 控制平面節點，低運算力，不參與一般排程 |
| **gce-agent-1** | `tier=low:NoSchedule` | 雲端低運算節點，僅在需要時接受排程 |
| **gce-agent-2** | `tier=low:NoSchedule` | 同上 |
| **acer-agent** | `reliability=low:PreferNoSchedule` | 本地主節點，具穩定性，但設定為低優先使用  |
| **laptop-agent** | `avail=on-demand:NoSchedule`
`reliability=low:PreferNoSchedule` | 按需節點，預設不排程，作為特殊用途 |
| **desktop-agent** | `avail=on-demand:NoSchedule`
`reliability=low:PreferNoSchedule` | 同上 |

---

### 節點 Label 設定

| Node Name | Labels | 說明 |
| --- | --- | --- |
| **hz-serv-sin** | `region=sin, tier=low, avail=24/7, provider=hetzner` | 來自 Hetzner 的新加坡雲端節點 |
| **gce-agent-1** | `region=tw, tier=low, avail=24/7, provider=gce` | 來自 Google Cloud 的臺灣雲端節點 |
| **gce-agent-2** | `region=tw, tier=low, avail=24/7, provider=gce` | 來自 Google Cloud 的臺灣雲端節點 |
| **acer-agent** | `region=tw, tier=medium, avail=24/7, provider=local` | 本地 24 小時開機的主要伺服器節點 |
| **laptop-agent** | `region=tw, tier=medium, avail=on-demand, provider=local` | 本地筆電節點，按需開機，
具備備措與測試用途 |
| **desktop-agent** | `region=tw, tier=high, avail=on-demand, provider=local` | 家用娛樂機，搭配 WSL 可作為高效能計算節點使用 |

## 📦 模組部署原則（靜態配置階段）

| 模組 | 部署節點 | 策略簡述 | 部署分類 |
| --- | --- | --- | --- |
| PostgreSQL Primary | hz-serv-sin | 高可用性優先，避免依賴本地端硬體 | cloud |
| PostgreSQL Replica | gce-agent-1 | 與查詢節點靠近，降低延遲 | cloud |
| SafeZone API | gce-agent-1 | 與 Dashboard 分散部署，平衡負載 | cloud |
| Redis Replica | gce-agent-2 | 接近主要資料使用者，提供快速存取 | cloud |
| Dashboard | gce-agent-2 | 與 API 分散部署，避免單點瓶頸 | cloud |
| CLI Relay | acer-agent | 接收來自開發端的需求，部署於本地優先響應 | local |
| Prometheus / ArgoCD / 
Redis Primary | acer-agent | 高 I/O 但低可用性要求的基礎設施模組，適合放於本地 | local |

---

## 🧩 Affinity 與 Topology Spread 應用示

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

> 上例為需要 24/7 且高負載排程策略。
> 

---