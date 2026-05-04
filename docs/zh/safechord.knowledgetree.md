# SafeChord 知識地圖

## 🗺️ 導航指南

SafeChord 採用**解耦四層**架構。請根據您的角色與目標選擇閱讀路徑：

*   **⬜ 知識層（Docs）**：**單一事實來源（SSOT）**。定義方法論、標準與全域規格。
*   **🟦 應用層（SafeZone）**：核心業務邏輯。聚焦於 Python/Go 原始碼、非同步資料流與 TDD 邊界。
*   **🟨 部署層（SafeZone-Deploy）**：交付與打包。聚焦於 Helm Chart 與 GitOps 推進工作流程。
*   **🟥 基礎設施層（Chorde）**：平台層。管理混合雲 K3s 叢集、網路邊界與排程策略。

### 🏷️ 圖例

| 圖示 | 意義 | 描述 |
| :--- | :--- | :--- |
| ⭐ | **核心概念** | 理解關鍵架構的必讀內容。 |
| 📄 | **文件** | 標準技術規格或詳細設計節點。 |
| 🛡️ | **安全** | 與安全架構或密碼管理相關的文件。 |
| 🔄 | **時間線** | 版本演進、變更記錄或遷移背景。 |
| 🚧 | **進行中** | 開發中或草稿階段的文件。 |

---

## 🌳 專案結構樹

*   🧩 **SafeChord 生態系統** - 整體概觀
    *   [📄 index.md](index.md) ⭐（系統概述：MVA 哲學、技術棧與策略演進）
    *   [📄 knowledgetree.md](safechord.knowledgetree.md)（本文件：全域導航）
    *   [📄 safechord.security.md](safechord.security.md) 🛡️（安全架構與 SecretOps 治理）
    *   🌐 **環境地圖**
        *   [📄 safechord.environment.md](safechord.environment.md) ⭐（分層環境：從本地 Compose 到平台整合）

    *   ⬜ **知識層（Repo: Docs）**
        *   *焦點：KDD 方法論、標準、SSOT*
        *   [📄 safechord.kdd.introduction.md](safechord.kdd.introduction.md)（KDD 哲學介紹）
        *   [📄 safechord.kdd.practice.md](safechord.kdd.practice.md) ⭐（實務：三引擎模型與 Headless 協定）

    *   🟦 **應用層（Repo: SafeZone）**
        *   *焦點：原始碼、業務邏輯、AsyncIO 資料流*
        *   **核心架構**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐（應用地圖：非同步資料流與事件驅動設計）
            *   [📄 safechord.safezone.service.python_scaffold.md](safechord.safezone.service.python_scaffold.md) ⭐（藍圖：標準 Python 架構與分層）
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md)（🔄 應用版本歷史與技術遷移）
        *   **微服務**
            *   [📄 safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md)（模擬器：AsyncIO 資料來源）
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md)（資料攝取器：Kafka Producer 閘道器）
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md)（工作者：Golang / Franz-Go 消費者）
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md)（API：聚合器與 Scaffold 藍圖）
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md)（UI：時間感知視覺化）
        *   **工具包與工作流程**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md)（時間伺服器：虛擬時鐘控制器）
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md)（SZCLI：維運工具與 CLI 轉送）
            *   [📄 safechord.safezone.workflow.md](safechord.safezone.workflow.md) ⭐（腳本：CI 工作流程與冒煙測試規格）

    *   🟨 **部署層（Repo: SafeZone-Deploy）**
        *   *焦點：設定、Helm、GitOps CD*
        *   [📄 safechord.safezone.deployment.md](safechord.safezone.deployment.md) ⭐（部署架構與全域 ADR）
            *   [📄 safechord.safezone.deployment.workflow.md](safechord.safezone.deployment.workflow.md)（腳本：GitOps 工作流程與環境推進）

    *   🟥 **基礎設施層（Repo: Chorde）**
        *   *焦點：Kubernetes、平台運算子、排程*
        *   [📄 safechord.chorde.md](safechord.chorde.md)（Chorde 概述：平台框架與儲存庫結構）
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐（K3han：混合雲叢集導航）
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) ⭐（實體拓撲、延遲矩陣與 Tailscale SDN）
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md)（Ingress 邊界：雙通道隔離）
            *   [📄 safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md) ⭐（排程器：可靠度階層與 Taints 策略）
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md)（可觀測性：Loki 與 Prometheus Operator）
            *   [📄 safechord.chorde.k3han.changelog.md](safechord.chorde.k3han.changelog.md)（🔄 平台版本演進）