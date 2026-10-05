# 持久化儲存策略（Brain）

> **一句話版本**：volume 跟使用它的 pod 放在同一台節點上，而家用節點上不准有無法重建的資料。

---

## 1. 設計限制（紅線）

*   **本機磁碟前面不擋網路檔案系統。** 工作負載被釘在某一台節點時，它的 volume 就是那台節點上的 local volume。
*   **fsync 不跨 WAN。** 會做 fsync 的工作負載（PostgreSQL、Kafka、開了 AOF 的 Valkey），volume 絕不放在 pod 以外的節點。
*   **replica 絕不跟 primary 共用同一顆磁碟。**
*   **家用硬體上不放無法重建的資料。** `acer-agent` 只有一顆磁碟，OS 跟上面所有 volume 共用；磁碟掛了，節點就沒了。放在那裡的資料必須能從雲端節點或 git 重建。事實來源留在 `ct-serv-jp`。
*   **每個靜態 PV 都預留給自己的 claim。** PV 在 `claimRef` 裡指名它的 claim。否則同一台節點上大小、class 都相同的兩個 PV，對 binder 來說可以互換。
*   **操作者會偷換的資料，留在操作者指定的主機路徑。** simulator 的輸入檔是刻意在主機上被替換的；不管底層用什麼儲存，那個路徑都要能直接指到。

## 2. 策略／政策定義

### volume 是拿來做什麼的

這裡的 volume 只回答一個問題：*pod 重啟之後，什麼東西必須還在？* 它不回答*什麼東西必須撐過節點消失*。後者取決於資料能從哪裡重建。

| 工作負載 | 節點 | volume 保護的東西 | 節點消失後從哪裡重建 |
| :--- | :--- | :--- | :--- |
| PostgreSQL primary | `ct-serv-jp` | 系統的事實來源 | 無法重建。其他資料都是從它衍生的。 |
| PostgreSQL replica | `acer-agent` | 一份 streaming 副本 | primary，透過 `pg_basebackup` |
| Kafka broker | `acer-agent` | 已經 ack 給 producer、但還沒被消費的訊息；叢集身分與 consumer offset | topic 以 `KafkaTopic` 宣告；在途訊息會遺失，由 simulator 重送 |
| Valkey | `acer-agent` | 系統狀態（status 與模擬時間） | 遺失。應用程式能不能乾淨地重新初始化，尚未驗證。 |
| Simulator 輸入 | `acer-agent` | 一份唯讀 CSV | SafeZone repository |

Kafka 是單一 broker、replication factor 為 1，所以這個 volume 是唯一讓 ack 有意義的東西。這就是它採用持久化而不是 ephemeral 的原因：用 `emptyDir` 的話，每次 pod 重建都會無聲地丟掉 ingestor 以為已經送達的訊息。

### 靜態的節點本機 volume

*   **做法**：每個 volume 都是預先建好的 `local` PV，用 `nodeAffinity` 指名節點，主機路徑放在 `/mnt/k3han-pv/` 底下。class 是 `local-path`。因為 PV 透過 `claimRef` 預留，claim 會直接綁上去，`local-path` provisioner 不會自己另外生一個 volume。
*   **理由**：排程策略本來就把這些工作負載釘在單一節點（[排程邏輯 §2](safechord.chorde.k3han.scheduling.md)）。local volume 把這個相依性直接寫在 PV 上，而不是藏在一個只有那台節點掛得起來的 mount 後面。

### 否決的方案：在控制平面上架 NFS server

2026-10 以前，`acer-agent` 上的 volume 是 NFS export，由節點自己掛自己。這台節點的磁碟被懷疑有問題時，第一個方案是把 export 搬到 `ct-serv-jp`、pod 留在原地。這個方案被否決：

*   它保護的是本來就能重建的資料，卻保護不了服務：節點掛了，pod 一樣跟著沒。
*   每一次 fsync 都要跨越台灣到日本的連線，而且 mount 是 `hard`，Tailscale 一斷，工作負載會卡死而不是失敗。
*   replica 會跟 primary 落在同一顆磁碟上。

### 變更運作中工作負載的儲存

這三種 operator 都不會把 storage class 的變更套用到運作中的工作負載：StatefulSet 的 `volumeClaimTemplates` 不可變更，Strimzi 會拒絕既有 node pool 的 class 變更，CloudNativePG 不會動既有的 claim。又因為 ArgoCD 追蹤 `main` 並開著 self-heal 與 prune，新的 manifest 必須先合併，再手動逐一重建工作負載：

*   先刪 claim，再刪擁有它的資源，重建出來的工作負載才不會沿用舊 claim。
*   資料要原地搬移時，不要事先建立目標目錄。local PV 的路徑不存在時，新 pod 會停在 `ContainerCreating`，直到資料搬到位。
*   Kafka node pool：刪掉 pool，保留 `Kafka` 資源。pod set 屬於 pool，cluster ID 屬於 `Kafka`。
*   replica：刪掉 `Cluster`，讓它重新 bootstrap。

## 3. 參考快照

> 驗證於 2026-10-05，Chorde #27 / #28 記錄的切換過程中。

| 觀察項目 | 數值 | 驗證的限制 |
| :--- | :--- | :--- |
| `acer-agent` → `ct-serv-jp` 經 Tailscale 的 RTT（直連） | 35 ms | fsync 不跨 WAN |
| `acer-agent` 的磁碟數 | 1（OS 與 volume 共用） | 家用硬體上不放無法重建的資料 |
| replica 以 `pg_basebackup` 重建 | 重建後 26 秒 healthy，streaming 追上 primary 的 LSN | replica 可重建 |
| Kafka 搬移 log 目錄之後 | cluster ID、end offset、consumer group 的 committed offset 都相同；lag 0 | volume 保住叢集身分 |
| Valkey 搬移資料目錄之後 | keyspace 相同，AOF 載入成功 | volume 撐過 pod 重建 |
| `acer-agent` 上剩下的 NFS mount | 只有 simulator 輸入 | 本機磁碟前面不擋網路檔案系統（仍有一個例外） |

> *目前的值以 `code_paths` 底下的 manifest 為準。*

## 4. 權衡與後果

| 優點 | 缺點 | 緩解方式 |
| :--- | :--- | :--- |
| fsync 走本機延遲；磁碟 I/O 不再依賴 Tailscale | volume 沒辦法跟著 pod 換節點 | 這些工作負載本來就被釘住；要搬就是在目標節點上重建資料 |
| PV 直接寫明資料在哪一台節點 | `acer-agent` 消失時，replica、Kafka 的在途訊息和 Valkey 的狀態會一起消失 | replica 與 Kafka 可重建，primary 在雲端節點；Valkey 的復原尚未驗證（§2） |
| 這些工作負載不再需要維運 NFS server | 主機目錄要手動建立與移除 | 路徑統一為 `/mnt/k3han-pv/<workload>` |

**仍開著的例外。** simulator 的輸入 PV 還是 `acer-agent` 上的 NFS export，因為它的 chart 把 claim 的 storage class 寫死了。NFS server 與 `local-nfs` class 會留到 SafeZone-Deploy #18 完成為止。

**尚未查明。** `acer-agent` 的磁碟為什麼開機時偶爾偵測不到。2026-10-05 的 SMART 沒有回報任何 reallocated、pending 或 uncorrectable sector。

## 5. 參考資料

*   **Manifests**：`code_paths` 底下，每個工作負載旁邊的 `PersistentVolume`
*   **相關策略**：[排程邏輯](safechord.chorde.k3han.scheduling.md)、[叢集策略](safechord.chorde.k3han.cluster.md)
*   **票**：Chorde #27、Chorde #28、SafeZone-Deploy #18
