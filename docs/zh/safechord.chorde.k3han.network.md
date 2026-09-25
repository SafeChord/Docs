# Pod 資料路徑與 CNI（Brain）

> **一句話版本**：flannel 負責發位址、接好 bridge，但跨節點的流量它一個 byte 都沒搬過，全是 Tailscale 在搬。
>
> **這種分工不是臨時湊出來的。** 它就是 [Kilo](https://kilo.squat.ai/) 以 flannel add-on 模式提供的架構：*「Kilo will take care of the network between locations, while Flannel will take care of the network within locations.」* 我們只是把「跨地點」這個角色換成 Tailscale（D1）。Kilo 在一個元件內完成的事，我們是用兩個原本就沒打算共處一台節點的專案拼出來的。所以這份文件大半篇幅都在講：兩者在哪裡交會、誰說了算。

---

## 1. 設計限制（紅線）

*   **只准一層 tunnel。** 跨節點的 pod 流量穿越 WAN 時，只能包一層：經由 Tailscale 的 WireGuard。
*   **Invariant 是路由結果，不是參數。** 每一台節點上，前往**其他**節點 pod CIDR 的路由都必須解析為 `dev tailscale0 table 52`（§2.3）。
*   **跨節點 pod 流量絕不做來源 NAT。** 不論從哪台節點連過來，server pod 看到的都是 client 真實的 pod IP（D2）。
*   **NetworkPolicy 在兩條路徑上都成立**，不論是經過 bridge 的還是經過路由的。同節點流量只會經過 Linux bridge，而 kernel 預設**完全不會**讓 iptables 看到 bridge 上的流量。`net.bridge.bridge-nf-call-iptables = 1` 這個開關就是讓 iptables 看得到。少了它，NetworkPolicy 永遠看不到同節點流量。這條列在[叢集策略 §3](safechord.chorde.k3han.cluster.md) 的 kernel invariant（見 §2.2）。
*   **絕不把 `cni0` 降到 tunnel 的 MTU**（D4）。PMTUD 已經在第一跳免費解決了這個落差。把 `cni0` 釘在 1280，正是 [tailscale#16820](https://github.com/tailscale/tailscale/issues/16820) 那個設定：iperf3 TCP 從直連的 700–800 掉到 2–3 Mbit/s。

---

## 2. 機制（Mechanism）

這一節只講事實，不講選擇：kernel、flannel 和 Tailscale 放在同一台節點上時實際做了什麼。這裡沒有替代方案可言，每一項主張都有 §4 的量測支撐。

### 2.1 誰負責什麼

| 職責 | 負責者 |
| :--- | :--- |
| Pod IPAM（每台節點依 `.spec.podCIDR` 分到一個 `/24`）、`cni0` bridge、veth 接線 | flannel（CNI plugin） |
| Pod 對外的 masquerade；`FLANNEL-FWD`：在 `-P FORWARD DROP` 的節點上放行沒有被 policy 管到的 pod 流量 | flannel（iptables） |
| **跨節點傳輸** | **Tailscale subnet routes** |
| VXLAN overlay（`flannel.1`） | flannel backend。**閒置：**開機至今收到 0 byte |
| NetworkPolicy | kube-router，內建於 k3s |

### 2.2 同節點 vs. 跨節點

分岔點在 **pod 自己的路由表**裡。flannel 替每個 pod 寫入：

```
<本節點的 /24>   dev eth0              ← 同節點：on-link，走 L2
10.42.0.0/16     via <cni0 位址>       ← 其他節點：交給 gateway
default          via <cni0 位址>
```

**同節點，在 L2 交換：**`pod A → veth → cni0 → veth → pod B`。bridge 像交換器一樣轉送 frame，主機的 IP 路由完全不參與，iptables 也就跟著不參與。這樣一來 NetworkPolicy 會看不到同節點流量。`bridge-nf-call-iptables` 這個開關（由 `br_netfilter` 模組提供）補上這個缺口：它讓 bridge 上的 frame 也走一遍 iptables。kube-router 專門為這個情況寫了另一種規則（`-m physdev --physdev-is-bridged`）。

**跨節點，在 L3 路由。**每個封包在送出端會經過 netfilter **兩次**：

```
第一輪：pod 封包，被轉送（forward）
  pod A → cni0（frame 的目的地是 bridge 自己）→ 主機 IP 堆疊
    PREROUTING   conntrack；kube-proxy DNAT（Service VIP → pod IP）
    routing      ip rule 5270 → table 52 → 10.42.x.0/24 dev tailscale0
    FORWARD      kube-router NetworkPolicy；kube-proxy；ts-forward；FLANNEL-FWD
    POSTROUTING  KUBE-POSTROUTING → ts-postrouting → FLANNEL-POSTRTG
  → tailscale0（TUN，沒有 L2）→ 交給 user space 的 tailscaled

第二輪：WireGuard 封包，本機產生
  tailscaled 加密 → 從自己的 socket 送出新的 UDP 封包（fwmark 0x80000）
    OUTPUT       本機送出
    routing      ip rule 5210：fwmark 0x80000 → main（跳過 table 52）
    POSTROUTING
  → eth0 → 對端節點的公開 endpoint
```

如果沒有那個 fwmark，第二輪的封包會跟其他封包一樣查到 table 52，加密後的封包就又被送回 tunnel 裡。

Hook 的順序（PREROUTING → routing → FORWARD → POSTROUTING）是 kernel 寫死的，在我們所有的發行版和 kernel 版本上都一樣。但同一條 chain **裡面**的規則順序不是固定的：誰最後插入，誰就排在前面。

### 2.3 為什麼路由是 Tailscale 贏

flannel 把 `via flannel.1` 寫進 **main** table；Tailscale 把 `dev tailscale0` 寫進 **table 52**。kernel 會照 preference 由小到大逐條檢查 `ip rule`，採用第一張查得到路由的 table。**最長前綴匹配只在同一張 table 內比較，從不跨 table。** Tailscale 的 `5270: lookup 52` 排在 main table 的 `32766` 前面，所以 table 52 贏。flannel 則完全沒有安裝任何 `ip rule`。

這個結果要四個條件同時成立：

| 前提 | 由誰維持 |
| :--- | :--- |
| Rule 5270 排在 main table 前面 | Tailscale（原始碼裡的常數） |
| 每台節點都開 `--accept-routes` | tailscaled prefs |
| 每台節點都宣告自己的 `.spec.podCIDR` | tailscaled prefs |
| 宣告的路由在 tailnet 上**已被核准** | Tailscale admin console（手動） |

> ⚠️ **無聲的 fallback。**任何一個前提失效都不會報錯。流量會滑到 `flannel.1` 上，而它的 VTEP 就是 Tailscale IP，所以 fallback 是「VXLAN 包在 WireGuard 裡面」：通得了、封裝兩層、從來沒量過。唯一的訊號是 `flannel.1` 的 **RX** 不再是 0（§2.6）。

### 2.4 MTU：瓶頸在第一跳

Pod 拿到的是 `cni0` 的 1450，`tailscale0` 是 1280。Linux 的 TCP 會設 DF，所以第一個滿載的 segment 會被**丟棄，而不是分片**。送出端的節點此時就是 pod 的第一跳路由器，它會回一個 ICMP *fragmentation needed*（RFC 1191）。pod 把這個目的地的 path MTU 記成 1280，TCP 就縮小 segment。代價是每條新路徑多一次來回，快取過期後再來一次。

這個 ICMP 是**在同一台主機內**產生、也在同一台主機內送達的，所以沒有任何中間設備能過濾掉它。kube-router 的 pod chain 會先放行來自本機節點的流量（`--src-type LOCAL`），再進入預設的 policy chain。

### 2.5 Netfilter 有多個寫入者，沒有仲裁者

kube-router、kube-proxy、flannel 和 Tailscale 都會寫每台節點的 `filter` 和 `nat` table，`ct-serv-jp` 上還有 ufw，`acer-agent` 上還有 Docker。iptables 在它們之間沒有優先順序可言：誰最後執行 `-I CHAIN 1`，誰就排第一。kube-router 在 resync 時會把自己的 jump 放回最前面，但不會去調整別人的順序。

Policy 之所以還能成立，靠的是兩個結構性的原因：

*   kube-router 對每一筆拒絕，都是**在自己的 chain 裡**用 `REJECT` 結束，被拒的封包根本不會回到 FORWARD 去碰到 Tailscale 那條無條件 `ACCEPT`。
*   Policy 所在的 `FORWARD` 排在 masquerade 所在的 `POSTROUTING` 之前。Policy 看到的永遠是原始來源。

### 2.6 驗證

| 檢查 | 位置 | 驗證內容 |
| :--- | :--- | :--- |
| 跨節點路由 gate | `privision.yaml` 最後幾個 task | prefs 吻合；每個其他節點的 CIDR 都解析為 `dev tailscale0 table 52`。不通過就讓 play 失敗 |
| `node-routing-test.sh` | `Chorde/scripts/test/pod-path/` | 在 live cluster 上跑同一個 gate，另外檢查 `bridge-nf-call-iptables` 和 `flannel.1` RX = 0。唯讀；跨節點流量看起來不對時第一個要跑的 |
| `netpol-matrix-test.sh` | `Chorde/scripts/test/pod-path/` | 在所有節點配對上跑 27 組探測：policy 的判決和真實來源 IP。會建立並刪除一個 namespace |

要看 `flannel.1` 的 **RX**，不要看 TX。TX 在每台節點上都不是 0：tailscaled 對其他節點 `10.42.x.0/.1` 位址送出的 disco probe 帶著繞道用的 fwmark，會落到 main table，然後從 `flannel.1` 送出去。

---

## 3. 決策（Decisions）

### D1. 傳輸：用 Tailscale subnet routes，不用 flannel 的 overlay

*   **決策。**每台節點都在 tailnet 上宣告自己的 pod CIDR，並接收其他節點的。flannel 保留作為 CNI，它的 VXLAN backend 維持設定但閒置。
*   **理由。**
    *   家裡那台節點在住宅網路的 NAT 後面，而 tailnet 已經解決了 NAT 穿透和加密。
    *   由一個元件從頭到尾負責整條路徑，MTU 落差就只有一個，而不是兩個。
*   **前例。**這就是 Kilo 的 flannel add-on 拓撲，只是 Kilo 的位置換成了 Tailscale：flannel 負責節點內的網路，WireGuard mesh 負責節點之間的網路。
    *   Kilo 要求每個地點至少一台節點有可公開路由的 IP。Tailscale 不需要，直連失敗時會改走 DERP relay。這一點對家裡那台節點很關鍵。
    *   相對於 Kilo，我們放棄的是整合度。Kilo 會自己從 Kubernetes 讀取 pod CIDR 並設定路由；在這裡，宣告和核准路由都是我們自己的工作（見代價）。
*   **被否決的替代方案。**
    *   *flannel VXLAN 直接跑在 WAN 上*（k3s 預設）：不加密，也不處理 NAT 穿透。
    *   *VXLAN 疊在 Tailscale 上*（`--flannel-iface=tailscale0`、`--vpn-auth`）：兩層 tunnel，`cni0` 會被壓到約 1230。`--vpn-auth` 還是實驗性功能。`--flannel-iface` 當時實際試過，在那時的 k3s 版本上沒成功。它現在只以無聲 fallback 的形式存在。
    *   *flannel `wireguard-native`*：是真正的單層，但家裡那台節點沒有 NAT 穿透。
    *   *換掉 CNI*（Cilium、`--flannel-backend=none`）：在跨國的 live cluster 上換 CNI，只為了移除一個零成本的 overlay。
*   **代價。**
    *   路由正確與否取決於 Tailscale 的 rule preference，而這是一個上游常數，目前還有公開討論（[tailscale#6231](https://github.com/tailscale/tailscale/issues/6231)）。
    *   路由核准放在 admin console，不在 git 裡。
    *   `flannel.1` 和它的路由看起來像是有一層 overlay，實際上什麼都沒在搬，會誤導任何看 `ip route` 的人。
*   **緩解。**
    *   §2.6 的 gate 和測試驗證的是 kernel 最後的決定，而不是那四個輸入。常駐的 `flannel.1` RX tripwire 已在規劃中。
    *   如果哪天 rule 不再勝出：`ip rule add not fwmark 0x80000/0xff0000 to 10.42.0.0/16 lookup 52 pref 5000`，並在 tailscaled 之後持久化。這只在 Tailscale 還使用 table 52 的前提下有效。
*   **背景。**把一個 cluster 拉到約 80 ms 的距離並不是主流做法，因為 etcd 需要個位數毫秒內的節點。為這種情境打造的專案（Kilo、Cilium 搭配 WireGuard）都收斂到同一條規則：由一個元件負責傳輸和它的 MTU。上面那些把 VXLAN 疊在 WireGuard 上的替代方案，都違反了這條規則。

### D2. 不做 subnet SNAT

*   **決策。**每台節點都設 `--snat-subnet-routes=false`。
*   **理由。**開著 SNAT 時，來源身分取決於 chain 的順序（§2.5）。在 `ts-forward` 比 kube-router 的 ACCEPT 先執行的節點上，從 `tailscale0` 進來的封包會被打上 mark，然後被 masquerade。在 `acer-agent` 上，每一個跨節點的 client 連到它的 pod 時，來源都變成了該節點的 `cni0` 位址。flannel 雖然會把 pod→pod 排除在 masquerade 之外，但 `ts-postrouting` 先執行。
*   **被否決的替代方案。**
    *   *重啟服務來修正 chain 順序*：只撐到下一次 tailscaled 重啟，而 auto-update 是開著的。
*   **代價。**不屬於 cluster 的 tailnet client 連到 pod 時，改為依賴回程路由，而不是 SNAT。目前沒有這樣的 client 在使用。
*   **緩解。**`netpol-matrix-test.sh` 會驗證每一台 server 看到的都是真實的 client IP。

### D3. netfilter 維持共管（暫時）

*   **決策。**Tailscale 的 netfilter mode 維持預設。除了 SNAT（D2）以外，接受沒有仲裁的順序。
*   **理由。**Policy 的判決不受順序影響（§2.5）。剩下的曝險範圍很窄：在 `ts-forward`／`ts-input` 排在 kube-proxy chain 前面的節點上（目前是 `acer-agent`），tailnet 來的流量會跳過 `KUBE-PROXY-FIREWALL`、`KUBE-FORWARD` 和 `KUBE-FIREWALL`。只有 tailnet 成員能送出這種流量，而且目前沒有任何 Service 使用 `loadBalancerSourceRanges`。
*   **延後的替代方案。**
    *   *`--netfilter-mode=nodivert`*（**優先的下一步**）：Tailscale 持續維護它的 chain，由我們把 jump 放在 chain 尾端，kube-* 從前面插入的規則推不動它。順序從此變成宣告出來的。
    *   *`--netfilter-mode=off`*：完全消除競爭。但 `ct-serv-jp` 的 ufw 沒有任何放行規則，它的 API server、kubelet 和 WireGuard port 全靠 `ts-input` 放行，得先把這些改寫成明確的規則。
*   **代價。**各節點的 chain 順序仍然不同，仍然取決於啟動順序。
*   **緩解。**chain 順序的 tripwire 已在規劃中。

### D4. 不調整 MTU

*   **決策。**`cni0` 維持 flannel 推導出的值。不做 MSS clamp。不設 `tcp_mtu_probing`。
*   **理由。**MTU 落差由第一跳的 PMTUD 解決，ICMP 從來不離開節點（§2.4）。典型的黑洞問題不適用。
*   **被否決的替代方案。**
    *   *把 `cni0` 降到 1280*：就是 [tailscale#16820](https://github.com/tailscale/tailscale/issues/16820) 裡讓 TCP throughput 崩掉的設定。
    *   *MSS clamp*：用一個手動維護的常數去做 PMTUD 本來就在做的事。
    *   *`tcp_mtu_probing = 1`*（RFC 4821）：為一個這個拓撲根本不會發生的故障模式投保。
*   **代價。**`cni0` 的值是 flannel 根據網卡推導出來的，當初是為了一個什麼都沒在搬的 overlay 計算的，只是剛好是對的。它在各節點之間已經不一致（`gce-agent-tw` 推導出的值較低），但無害。
*   **緩解。**§1 的紅線。

---

## 4. 參考快照

> 時間點紀錄，**不是 SSOT**。throughput 於 2026-09-21 驗證，其餘於 2026-09-25 驗證。

| 觀察 | 數值 | 支撐 |
| :--- | :--- | :--- |
| 跨節點 pod→pod TCP，預設／MSS 1100／節點→節點 | 中位數 209／234／232 Mbit/s | D1、D4：pod 流量跑在節點之間的 tailnet 速率上，CNI 的安排沒有帶來可量測的成本。這個速率的上限卡在哪裡（上行頻寬、跨國路徑、WireGuard CPU）沒有調查 |
| 同節點 pod→pod | 32.1 Gbit/s | §2.2：bridge 路徑完全不碰 tunnel |
| 10 秒跨節點測試期間 `tailscale0` 與 `flannel.1` 的 TX | +215,542,969 B 對 +1,460 B | §2.3 |
| 所有節點的 `flannel.1` RX | 開機至今 0 B | §2.3：fallback 從未被使用 |
| `ct-serv-jp` 開機至今的 `IpFragCreates`／`IpFragFails` | 0／5353 | §2.4：丟棄並回報，從未分片 |
| NetworkPolicy 矩陣，3 節點 × 3 client × 3 server | 27/27 | §2.5 |
| 全部改為 NoSNAT 後 server 看到的來源 IP | 所有配對都是真實的 client pod IP | D2 |

---

## 5. 參考資料

*   **Provisioning 與 gate**：`Chorde/cluster/k3han/ansible/privision.yaml`
*   **記錄下來的 k3s unit**：`Chorde/cluster/k3han/k3s/`
*   **測試**：`Chorde/scripts/test/pod-path/`
*   **Tickets**：Chorde#16（本設計）、Chorde#15（playbook 從未執行過）、Chorde#17（playbook 拆成 roles）
*   **相關策略**：[叢集策略](safechord.chorde.k3han.cluster.md)、[流量進入政策](safechord.chorde.k3han.ingress.md)
*   **外部資料**：[Tailscale netfilter modes](https://tailscale.com/docs/reference/netfilter-modes)、[Tailscale route injection](https://tailscale.com/docs/reference/route-injection)、RFC 1191、RFC 4821
