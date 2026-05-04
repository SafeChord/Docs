# 排程與編排政策 (大腦)

> **策略目標**：透過強制實行「控制平面本地性」與「可靠性分層」來管理高度不對稱的混合雲，以減輕跨境延遲與資源稀缺問題。

---

## 1. 背景與挑戰
K3han 橫跨三個特性差異極大的區域：
*   **Contabo (日本)**：高穩定性、12GB RAM，但到台灣約 80ms 延遲。
*   **GCE (台灣)**：優質 peering，但僅 1GB RAM 且頻寬成本高。
*   **Home (台灣)**：高 IOPS/CPU、Sunk Cost，但受消費級 ISP 網路波動影響。

標準 K8s 排程無法應對，因為它忽略了「帳單風險」與「自建機房電力波動」。

## 2. 核心原則
1.  **控制平面本地性**：運算子（CNPG、Strimzi、KEDA）必須留在雲端節點（API 延遲 <1ms）。
2.  **資料本地性**：副本與高吞吐量 broker（Kafka/Redis）留在本地節點以節省出口成本。
3.  **邊緣隔離**：GCE 節點僅限於流量轉發。
4.  **可靠性分層**：使用 Taints 來 soft-reject 關鍵生產 Pod 落在自建機房硬體上，除非明確容忍。

---

## 3. 編排決策

### 3.1 隔離策略 (Taints)
| Taint Key | Effect | 目標節點 | 理由 |
| :--- | :--- | :--- | :--- |
| `node-role.kubernetes.io/control-plane` | `NoSchedule` | `ct-serv-jp` | **Master 保護**：防止業務負載影響 ArgoCD/Operators。 |
| `chorde.io/purpose=proxy-only` | `NoSchedule` | `gce-agent-tw` | **Ingress 保護**：保留 1GB RAM 僅供 Nginx-Ingress 使用。 |
| `chorde.io/provider=local` | `PreferNoSchedule`| `acer-agent` | **可用性過濾**：防止非容錯 Pod 落在自建機房硬體上。 |

### 3.2 標籤結構 (v0.3.x 快照)
> 💡 **參考**：在 `nodeSelector` 或 `affinity` 區塊中使用這些標籤。

| 標籤 Key | 值 | 用途 |
| :--- | :--- | :--- |
| `topology.kubernetes.io/region` | `jp` / `tw` | 地理成本與延遲計算。 |
| `chorde.io/provider` | `contabo` / `gce` / `local` | 硬體可靠性分組。 |
| `chorde.io/tier` | `low` / `medium` / `high` | 資源容量排名。 |
| `node.safechord.io/capability` | `high-iops` | 將 DB/Kafka 固定在本地 SSD 上。 |

---

## 4. 實作參考 (YAML)

### 模式：將運算子固定在雲端
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: node-role.kubernetes.io/control-plane
              operator: Exists
```

### 模式：將副本/應用固定在本地台灣
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: chorde.io/region
              operator: In
              values: ["tw"]
            - key: chorde.io/tier
              operator: In
              values: ["medium"]
```

---

## 5. 權衡與後果
*   **優點**：資料複製幾乎零跨境頻寬成本。
*   **優點**：GitOps 與 Operator 層極度穩定。
*   **缺點**：高度依賴 `acer-agent`。若自建機房斷電，副本將遺失。
*   **緩解措施**：定義了手動升級腳本，用於雲端備援節點。

## 6. 參考資料
*   **庫存清單**：`Chorde/cluster/k3han/ansible/inventory.ini`
*   **清單檔**：檢視 `Chorde/gitops/k3han/manifests/` 中的 Affinity 區塊。