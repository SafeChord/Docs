# SafeZone 服務標準（藍圖）

> **類型**：藍圖（跨服務）
> **焦點**：每個 SafeZone 服務對系統其他部分的共同承諾。
> **限制**：只寫現況，而且只寫約束一個以上服務的承諾。不寫程式撰寫慣例（看 `SafeZone/.ai-rules.md`）。不寫欄位層級的形狀（看合約檔）。不寫理由（看[決策日誌](safechord.safezone.decisions.md)）。不寫沿革（看 [changelog](safechord.safezone.changelog.md)）。

## 1. 需求

除非需求本身指明較小的範圍，每條需求適用於所有服務。守住某條需求的測試會帶上它的 ID。

### STD-R1：請求可以從頭追蹤到尾
服務必須把收到的 trace ID 帶進自己的 log，以及它接著送出的每個請求或事件。沒有收到 trace ID 的服務必須自己建立一個。

#### 情境：HTTP 請求帶有 trace ID
- GIVEN 一個在 `X-Trace-ID` 標頭帶有 trace ID 的請求
- WHEN HTTP 服務處理它
- THEN 回應帶有相同的 trace ID
- AND 服務在處理過程中送出的每個請求或事件都帶有該 trace ID

#### 情境：沒有帶 trace ID
- GIVEN 一個沒有 trace ID 的請求
- WHEN HTTP 服務處理它
- THEN 回應帶有一個新建立的 trace ID

#### 情境：事件帶有 trace ID
- GIVEN 一筆帶有 trace ID 的事件
- WHEN 消費者處理它
- THEN 消費者為該事件寫出的每一行 log 都帶有該 trace ID

### STD-R2：HTTP 服務回報自己的健康狀態
每個 HTTP 服務在能夠服務請求時，都必須對 `GET /health` 回應成功狀態。

#### 情境：服務正常
- GIVEN 一個執行中的 HTTP 服務
- WHEN 請求 `/health`
- THEN 回應狀態為 200

### STD-R3：共用的合約只有一份定義
一個以上服務依賴的合約，必須恰好只有一份定義。兩端的服務以不同語言撰寫時，這份定義必須是 `SafeZone/utils/contract/` 底下的語言中立檔案。各服務自己的 model、struct 或資料表定義，都是它的實作。

#### 情境：同一語言的兩個服務
- GIVEN 一份只有 Python 服務使用的合約
- WHEN 任一服務需要它的形狀
- THEN 兩者都從 `SafeZone/utils/` import 同一份定義

#### 情境：不同語言的服務
- GIVEN 一份由不同語言的服務使用的合約
- WHEN 某個服務需要它的形狀
- THEN 它實作的是語言中立的檔案，而不是另一個服務的程式碼

### STD-R4：服務要證明自己遵守碰到的每份合約
對於服務生產或消費的每份合約，該服務必須有一個 unit test，在它的實作與合約定義不一致時失敗。生產端只送出合約允許的內容。消費端接受合約允許的一切，也可以接受更多。

#### 情境：生產端漂移
- GIVEN 一個對某合約生產的服務
- WHEN 它將送出合約禁止的內容
- THEN 該服務的某個 unit test 失敗

#### 情境：消費端漂移
- GIVEN 一個從某合約消費的服務
- WHEN 它無法接受合約允許的內容
- THEN 該服務的某個 unit test 失敗

## 2. 合約

SafeZone 服務之間共用的合約，以及各自的定義位置。服務藍圖的依賴表會指向這些檔案。

| 合約 | 定義 | 使用它的語言 | 現況 |
| :--- | :--- | :--- | :--- |
| 病例事件（Kafka topic） | `SafeZone/utils/contract/covid_event.json` | Python、Go | 語言中立。STD-R4 要求的測試追蹤於 SafeZone#70。 |
| 資料庫資料表 | `SafeZone/utils/db/schema.py` | Python、Go | 只有 Python 定義。`SafeZone/utils/contract/` 底下的 SQL 匯出追蹤於 SafeZone#70。 |
| 服務的請求與回應模型 | `SafeZone/utils/pydantic_model/` | Python、TypeScript | 只有 Python 定義。Dashboard 以手抄方式對應。尚無票。 |
| 行政區界與區域名稱 | `SafeZone/utils/geo_data/` | Python、TypeScript | 語言中立。以它檢查 dashboard 地圖資料的測試追蹤於 SafeZone#55。 |
| 快取版本鍵 | 無 | Python | 鍵名在 relay CLI 與 Analytics API 各寫一份。尚無票。 |
