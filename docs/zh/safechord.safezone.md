# 🗺️ SafeZone 應用程式地圖

> **類型**：地圖（架構總覽）
> **上下文**：事件驅動的分散式疫情模擬與分析引擎。

---

## 1. 系統上下文與資料流

SafeZone 設計為單向資料處理管線。資料由模擬器產生，經緩衝區處理以提升彈性，再持續寫入結構化視圖，以支援高效能查詢。

```mermaid
graph LR
    %% 樣式
    classDef source fill:#e1f5fe,stroke:#01579b;
    classDef process fill:#fff9c4,stroke:#fbc02d;
    classDef storage fill:#e0e0e0,stroke:#616161;
    classDef view fill:#e8f5e9,stroke:#2e7d32;

    %% 控制平面
    subgraph Trigger [控制平面]
        CLI(SZCLI / 協調器):::source
        Time(時間伺服器):::source
    end

    %% 寫入路徑
    subgraph WritePath [寫入管線]
        Sim(疫情模擬器<br/>AsyncIO Generator):::source
        Ingest(資料接收器<br/>Kafka Producer):::process
        Kafka(Kafka 主題<br/>covid.raw.data):::storage
        Worker(Golang Worker<br/>Franz-Go Consumer):::process
    end

    %% 持久儲存
    subgraph DataStore [持久層]
        DB[(PostgreSQL<br/>原始事實)]:::storage
        Redis[(Redis 快取)]:::storage
    end

    %% 讀取路徑
    subgraph ReadPath [讀取管線]
        API(分析 API<br/>聚合器):::process
        Dash(儀表板<br/>互動式 UI):::view
    end

    %% 互動關係
    CLI <-->|"控制與讀取"| Time
    CLI -->|"1. 觸發（虛擬日期）"| Sim
    Sim -->|"2. 事件（HTTP）"| Ingest
    Ingest -->|"3. 緩衝"| Kafka
    Kafka -->|"4. 消費（批次）"| Worker
    Worker -->|"5. 更新寫入"| DB
    
    API -->|"6. 查詢"| DB
    API -.->|"快取"| Redis
    Dash -->|"7. 視覺化"| API
    Time -.->|"時間同步"| Dash
```

---

## 2. 微服務索引

SafeZone 遵循**關注點分離**原則，將邏輯解耦至各專業微服務。

### 2.1 寫入管線
負責高併發資料接收與持久儲存。

| 服務 | 角色 | 關鍵技術 | 文件 |
| :--- | :--- | :--- | :--- |
| **疫情模擬器** | **資料來源** | AsyncIO, httpx, Pandas | [藍圖](safechord.safezone.service.pandemicsimulator.md) |
| **資料接收器** | **閘道** | FastAPI, aiokafka | [藍圖](safechord.safezone.service.dataingestor.md) |
| **Worker (Golang)** | **消費者** | Golang, Franz-Go | [藍圖](safechord.safezone.service.worker.md) |

### 2.2 讀取管線
負責資料聚合與使用者呈現。

| 服務 | 角色 | 關鍵技術 | 文件 |
| :--- | :--- | :--- | :--- |
| **分析 API** | **聚合器** | FastAPI, Redis, SQLAlchemy | [藍圖](safechord.safezone.service.analyticsapi.md) |
| **儀表板** | **視覺化工具** | Plotly Dash, httpx | [藍圖](safechord.safezone.service.dashboard.md) |

### 2.3 工具組與協調
支援性元件，負責維護模擬的狀態與運作。

| 元件 | 角色 | 關鍵技術 | 文件 |
| :--- | :--- | :--- | :--- |
| **SZCLI** | **控制器** | Python Typer | [參考](safechord.safezone.toolkit.cli.md) |
| **時間伺服器** | **全域時鐘** | FastAPI | [藍圖](safechord.safezone.toolkit.timeserver.md) |

---

## 3. 關鍵架構特性

1.  **事件驅動解耦**：
    *   寫入路徑透過 **Kafka** 完全解耦。接收器（閘道）與 Worker（處理器）可獨立擴展。
    *   **價值**：流量高峰時，接收器僅負責快速接收資料；Worker 則根據處理能力平穩地寫入資料庫（負載均攤）。

2.  **多語言實作**：
    *   **Python**：用於複雜領域邏輯（模擬器、API）以及快速迭代 UI（儀表板）。
    *   **Golang**：用於運算密集型、高吞吐量的任務（Worker），以最大化資源使用效率。

3.  **時間感知**：
    *   SafeZone 支援「虛擬時間線」。所有與時間相關的元件（模擬器、儀表板）皆參照**時間伺服器**，而非系統時鐘。
    *   **價值**：支援「時光旅行」模擬（快進或暫停疫情進程），以利除錯與預測。

---

## 4. 運維連結

*   **部署架構**：[部署與運維](safechord.safezone.deployment.md)
*   **CI/CD 管線**：[CI/CD 工作流程](safechord.safezone.workflow.md)
*   **API 規格**：請參閱各服務藍圖中的**介面**章節。