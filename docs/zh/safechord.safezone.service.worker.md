# Worker（服務藍圖）

> **類型**：藍圖（服務）
> **焦點**：這個服務對系統其他部分的承諾，以及它依賴什麼。
> **限制**：只寫現況。不寫檔案結構、函式庫或實作（看程式碼庫）。不寫欄位層級的形狀（看合約檔）。不寫理由（看[決策日誌](safechord.safezone.decisions.md)）。不寫沿革（看 [changelog](safechord.safezone.changelog.md)）。

## 1. 職責

*   **角色**：消費者 / 持久化者
*   **核心目標**：把 Kafka 上的病例事件串流，轉成 PostgreSQL 裡每個日期、城市、區域一筆的病例數。過程中不遺失事件，也不讓 consumer group 回報的進度偏離實際已儲存的內容。

## 2. 需求

每條需求都是系統其他部分會依賴的承諾。守住某條需求的測試會帶上它的 ID。所有服務共用的需求放在[服務標準](safechord.safezone.service.standards.md)，這裡不重複。

### WK-R1：有效事件會被儲存
Worker 必須把讀到的每一筆有效事件，儲存為該事件的日期、城市、區域的病例數。事件符合事件合約，且城市與區域存在於行政區資料表時，才算有效。

#### 情境：有效事件
- GIVEN topic 上有一筆有效事件
- WHEN worker 消費它
- THEN 病例表存有該日期、城市、區域的這個數字

### WK-R2：同一個鍵以最新事件為準
日期、城市、區域相同的事件，儲存的病例數必須是 topic 順序中最新那筆的值，不論事件如何分批或重送。

#### 情境：同一個鍵的兩筆事件一起到達
- GIVEN 兩筆鍵相同、病例數不同的事件
- WHEN worker 在同一次寫入中儲存它們
- THEN 病例表存的是後面那筆的數字

#### 情境：重送
- GIVEN 已經儲存過的事件
- WHEN 它們再次被送達
- THEN 儲存的數字不變

### WK-R3：儲存之後才記錄進度
Worker 必須在事件已被儲存或被刻意跳過（WK-R5）之後，才提交該事件的 offset。

#### 情境：儲存前就停止
- GIVEN 已讀取但尚未儲存的事件
- WHEN worker 在儲存前停止
- THEN 重啟後這些事件會再次被送達

### WK-R4：已提交的進度不會倒退
Consumer group 對任一 partition 已提交的 offset 必須永不減少，並在所有事件處理完後到達 log 末端。

#### 情境：消費途中成員變動
- GIVEN 數個 worker 在負載下消費
- WHEN 有 worker 加入或離開 group
- THEN 沒有任何 partition 的已提交 offset 減少
- AND 最後一筆事件處理完後 group lag 歸零

### WK-R5：無效事件不會卡住串流
Worker 必須記錄並跳過不有效的事件（WK-R1），包含無法解析的事件，並繼續消費之後的事件。

#### 情境：無效事件夾在有效事件之間
- GIVEN 一筆無效事件夾在兩筆有效事件之間
- WHEN worker 消費這三筆
- THEN 兩筆有效事件都被儲存
- AND 無效事件不會再次被送達

### WK-R6：關閉時不遺失資料
收到 SIGTERM 時，worker 必須先儲存手上的事件並離開 consumer group，然後才結束。

#### 情境：手上還有事件時被終止
- GIVEN 已讀取但尚未儲存的事件
- WHEN worker 收到 SIGTERM
- THEN process 結束時這些事件已在病例表中
- AND group 不必等 session timeout 就重新分配它的 partition

### WK-R7：閒置時事件不會被扣住
即使沒有後續事件到達，worker 也必須在設定的 flush 間隔內儲存事件。

#### 情境：流量在批次中途停止
- GIVEN 少於一個完整批次的事件
- WHEN 一個 flush 間隔內沒有新事件到達
- THEN 這些事件已在病例表中

### WK-R8：每筆處理過的事件都可追蹤
Worker 處理一筆事件時寫出的每一行 log，都必須帶有該事件的 trace ID，不論事件被儲存或被跳過。這是 STD-R1 在消費者上的應用。

#### 情境：事件被跳過
- GIVEN 一筆帶有 trace ID 的無效事件
- WHEN worker 跳過它
- THEN 記錄這次跳過的 log 帶有該 trace ID

### WK-R9：健康狀態反映消費迴圈
只有在消費迴圈於設定的 liveness 時間窗內轉過時，worker 才能回報健康（STD-R2）。Topic 閒置時，以及 Kafka 或資料庫連不上時，它都必須維持健康。

#### 情境：topic 閒置
- GIVEN 一個沒有事件可消費的 worker
- WHEN 請求 `/health`
- THEN 回應狀態為 200

#### 情境：迴圈卡住
- GIVEN 一個消費迴圈超過 liveness 時間窗沒有轉動的 worker
- WHEN 請求 `/health`
- THEN 回應不是成功狀態

#### 情境：資料庫連不上
- GIVEN 一個連不上資料庫、但迴圈仍在轉動的 worker
- WHEN 請求 `/health`
- THEN 回應狀態為 200

## 3. 依賴

| Channel | 方向 | 合約 | 另外假設 |
| :--- | :--- | :--- | :--- |
| 病例事件 topic | 消費 | `SafeZone/utils/contract/covid_event.json` | 同一城市與區域的事件落在同一個 partition，順序即生產順序。WK-R2 依賴這點。 |
| 病例表 | 寫入 | 尚無語言中立的合約。以 `SafeZone/utils/db/schema.py` 為準；SQL 匯出追蹤於 SafeZone#70。 | 無。 |
| 行政區資料表（cities、regions） | 讀取 | 同病例表。 | Worker 啟動時資料已齊。之後新增的資料要重啟才看得到。 |
