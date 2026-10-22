# zh Glossary

The terms a zh page under `docs/zh/` uses. `.ai-rules.md` §2.3 holds the voice and the other
language rules; this file holds the words. The translate skill's run reads it, and so does the
review of what the run writes, so a change here reaches the next translation.

**Avoid** lists wording common in Simplified-Chinese technical writing that a Taiwanese engineer
would not use for that meaning. The hard QA prints each one it finds in a zh page as a warning.
Some have a legitimate other meaning (住家地址 is a street address), so a warning is for the reviewer
to judge, not a failure. A word whose other meaning is common in Taiwan (支持, 項目, 數據) is left
out of Avoid.

The general and programming terms follow the Linux kernel's zh_TW glossary
(`Documentation/translations/zh_TW/glossary.rst`), as a reference: its spacing rule is not ours
(§2.3), and its interface terms are left out.

## Kept in English

Software and product names stay as they are written. So do these terms: Helm, ArgoCD, Kafka,
Schema, FastAPI, GitOps, KEDA, Tailscale, K3s, Ingress, ConfigMap, Secret, Sync Waves, SSOT, ADR,
TDD, KDD, Spike, Pod, playbook, drop-in, Agent, and terms of the same kind. In a requirement's
scenarios, GIVEN / WHEN / THEN / AND stay in English.

## Project terms

One fixed translation each.

| en | zh |
| :--- | :--- |
| Settler | 維護者 |
| Pioneer | 開拓者 |
| Red Walls | 紅線 |
| Documentation Reconciliation | 文件對齊 |
| Alignment (internal, incremental, full) | 校正（內部校正、增量校正、全量校正） |
| Spike | Spike |
| Discussion, Development, Delivery, Operations (modes) | 討論、開發、交付、維運 |
| Time Server (the SafeZone component) | 時間伺服器 |

## General terms

| en | zh | Avoid |
| :--- | :--- | :--- |
| kernel | 核心 | 內核 |
| firmware | 韌體 | 固件 |
| software / hardware | 軟體／硬體 | 軟件、硬件 |
| user / user space | 使用者／使用者空間 | 用戶 |
| default | 預設 | 默認、缺省 |
| information | 資訊 | 信息 |
| network | 網路 | 網絡 |
| server | 伺服器 | 服務器 |
| video | 影片 | 視頻 |
| documentation | 文件 | 文檔 |
| file | 檔案 | |
| repository | 儲存庫 | 倉庫 |
| project | 專案 | |
| create | 建立 | 創建 |
| access (data, a resource) | 存取 | 訪問 |
| integrate | 整合 | 集成 |
| dashboard | 儀表板 | |

## Programming terms

| en | zh | Avoid |
| :--- | :--- | :--- |
| source code | 原始碼 | 源代碼、源碼 |
| code | 程式碼 | 代碼 |
| process | 行程 | 進程 |
| thread | 執行緒 | 線程 |
| schedule / scheduler | 排程／排程器 | 調度 |
| queue | 佇列 | 隊列 |
| memory | 記憶體 | 內存 |
| cache | 快取 | 緩存 |
| interface | 介面 | 接口 |
| port | 埠 | 端口 |
| stack | 堆疊 | 堆棧 |
| function | 函式 | 函數 |
| callback | 回呼 | 回調 |
| return value | 回傳值 | 返回值 |
| variable | 變數 | 變量 |
| object | 物件 | 對象 |
| array | 陣列 | 數組 |
| character / string | 字元／字串 | 字符 |
| byte | 位元組 | 字節 |
| binary | 二進位 | 二進制 |
| type | 型別 | |
| module | 模組 | 模塊 |
| component | 元件 | 組件 |
| build | 建置 | 構建 |
| debug | 除錯 | 調試 |
| implement | 實作 | |
| global / local | 全域／區域 | 全局 |
| constant | 常數 | 常量 |
| comment (in code) | 註解 | 注釋 |
| load | 載入 | 加載 |
| export / import | 匯出／匯入 | 導出 |
| link | 連結 | 鏈接 |
| distributed | 分散式 | 分布式 |
| configuration file | 設定檔 | 配置文件 |
| settings, configuration | 設定 | |
| file system | 檔案系統 | 文件系統 |
| field | 欄位 | 字段 |
| disk | 磁碟 | 磁盤 |
| trace, tracking | 追蹤 | 跟蹤 |

## Cloud and operations terms

| en | zh | Avoid |
| :--- | :--- | :--- |
| address (network) | 位址 | 地址 |
| run, runtime | 執行、執行期 | 運行 |
| forward (packets, ports) | 轉送 | 轉發 |
| cluster | 叢集 | 集群 |
| node | 節點 | |
| deploy, deployment | 部署 | |
| policy | 政策 | |
| origin (server) | 來源伺服器, or origin | 源站 |
| allowlist | 允許清單 | |
| guest (virtual machine) | 客體 | |
| bare metal | 裸機 | |
| invariant | 不變量 | |
| root cause | 根本原因 | 根因 |

## Characters

Taiwan's standard forms.

| en | zh | Avoid |
| :--- | :--- | :--- |
| (for, as) | 為 | 爲 |
| (inside) | 裡 | 裏 |
| (particle) | 著 | 着 |
| (open, start) | 啟 | 啓 |
| publish, release | 發布 | 發佈 |
