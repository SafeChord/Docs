---
version: v0.1.0
module: k3han
role: spec            
status: deprecated
summary: K3han 內節點能力描述。
updated: 2024-05-09
submodule_versions: null
--- 
# 📦 SafeChord Node Specification (v0.3)

> 本文件紀錄 SafeChord / K3han 環境中各節點 (Node) 的硬體、作業系統與角色屬性。  
> 資料來源於 2025/04 整理作業。

---

## 🧱 Node 規格總表

| Node Name    | CPU 型號（參考）         | vCPU / RAM     | 磁碟容量               | 作業系統                      | Provider                      | 備註 |
|:-------------|:--------------------------|:---------------|:------------------------|:------------------------------|:---------|:-----|
| laptop-agent | Intel i7-4720HQ           | 4C8T / 16GB    | 256GB SATA SSD + 1TB HDD | Ubuntu Server 24.04 LTS       | Local        | 本地筆電 |
| acer-agent   | Intel i5-8500             | 6C6T / 16GB    | 256GB SATA SSD           | Ubuntu Server 24.04 LTS       | Local                   | 本地 Mini-Server |
| desktop-agent| Intel i5-13600K           | 14C20T / 28GB  | 1TB NVMe SSD             | Ubuntu 24.04 (WSL2)           | Local              | 高效能桌機 |
| gce-agent-1  | Xeon (Shared, vCPU 2.20GHz) | 2C2T / 4GB   | 10GB Persistent Disk     | Debian GNU/Linux 12 (Bookworm) | GCE              | VPS, shared CPU, 規格流動 |
| gce-agent-2  | Xeon (Shared, vCPU 2.20GHz) | 2C2T / 4GB   | 10GB Persistent Disk     | Debian GNU/Linux 12 (Bookworm) | GCE                           | VPS, shared CPU, 規格流動 |
| hz-serv-sin  | AMD EPYC (vServer,虛擬化)  | 3C3T / 4GB    | 81GB QEMU HARDDISK       | Ubuntu 24.04.2 LTS (Noble)    | Hetzner     | VPS, 穩定性中等 |

---

## 📋 註詢
- Local Device（laptop-agent / acer-agent / desktop-agent）皆為實體機，性能、CPU 型號、記憶體容量可信。
- Cloud VPS（gce-agent-1 / gce-agent-2 / hz-serv-sin）僅 vCPU 數量與記憶體容量可信，底層 CPU 型號與頻率皆屬虛擬化抽調，僅供參考。
- WSL2 環境（desktop-agent）內核由 Windows Hyper-V 管理，記憶體與 CPU 限制可於 Windows 設定中調整。

---

## 🔥 延伸建議（可選）
- 針對各 Node 進一步標記 `nodeSelectorLabels`（如 region、tier、ha-level、provider）。
- 設計基於 node label 的 affinity policy，加強 Pod 排程靈活性。
- 定期重新驗證 cloud VPS 資源，避免因 cloud provider policy 變更而出現資源突變問題。
