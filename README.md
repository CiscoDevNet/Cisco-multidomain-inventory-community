# Cisco Multi-domain Inventory Tool & MCP Server

[English](#english) | [日本語](#japanese)

---

<a name="english"></a>
## English

This is a unified tool and **Model Context Protocol (MCP) Server** designed to retrieve and manage inventory information from four major Cisco network domains: ACI, Meraki, Catalyst Center, and SD-WAN. 

By acting as an MCP server, it allows AI assistants like **Claude Desktop** to directly query, act on, and understand your network infrastructure using natural language.

### 🚀 Key Features
- **MCP Native**: Functions as a Model Context Protocol server for seamless AI integration.
- **Multi-domain Integration**: Supports ACI, Meraki, Catalyst Center, and SD-WAN.
- **Smart Prompts**: Pre-built AI workflows for instant health checks and device investigations.
- **Real-time Status**: Fetches live status (online/offline) and details from controllers.

### 🤖 AI Assistant Workflows (Tutorial)

Once connected to Claude Desktop, you can interact with the server using **Slash Commands** or **Natural Language**.

#### 1. Slash Commands (Pre-defined Workflows)
Type the following commands directly into the chat input.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **`/network_health_check`** | Type `/network`... | **Health Check**: Retrieves a summary of all devices and generates a structured report of any "unhealthy" devices (offline, errors). |
| **`/investigate_device`** | Type `/investigate`... | **Deep Dive**: Searches for a specific device (by IP, Name, or Serial) across all domains and displays detailed status/links. |

#### 2. Natural Language Examples
You don't need to remember commands. Just ask Claude naturally.

**🔍 Search & Discovery**
* "Find the device with IP address 192.168.10.5."
* "Where is the switch named 'JP-Tokyo-Core' located?"
* "Do we have any Catalyst 9300 switches in the inventory?"
* "Search for serial `FGLxxxx` and show me the Model and Firmware version."

**🏥 Health & Status**
* "List all offline devices in the Meraki domain."
* "Are there any critical errors in the SD-WAN fabric?"
* "List all devices that are currently unreachable."
* "Check the status of the device with IP 10.1.1.1."

**📊 Inventory Analysis**
* "Summarize the total number of devices per domain."
* "List the firmware versions of all Catalyst switches."
* "Visualize the breakdown of Catalyst models using a **text-based bar chart**."
* "Create a table listing all ACI Spines and Leafs."
* "Compare the device counts between Meraki and SD-WAN."
* "Generate a **Mermaid pie chart** showing the ratio of Healthy vs Unhealthy devices."

### 🛠 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kikuta/Cisco-multidomain-inventory.git
   cd Cisco-multidomain-inventory
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**: 
   Copy `config.yaml.sample` to `config.yaml` and fill in your controller credentials.
   ```bash
   cp config.yaml.sample config.yaml
   ```

### 💻 Interface Examples

#### AI Assistant (via MCP)
Interact with your network infrastructure using natural language in Claude Desktop.
<img width="800" alt="MCP Integration Concept" src="https://github.com/user-attachments/assets/4bfcf64e-a475-4de1-a7c5-816fbca72bed" />

<img width="800" alt="MCP Integration Concept" src="https://github.com/user-attachments/assets/e6a5effd-a6c1-402e-be97-f54f3602cda5" />

#### Web Interface
```bash
python multidomain_inventory_web.py
```

<img width="800" alt="Flask web app" src="https://github.com/user-attachments/assets/6e6f32d6-e29e-4b53-bf13-e3f40079fa55" />
*(Note: Using the Web UI screenshot as a reference for inventory visibility)*

#### CLI
```bash
python multidomain_inventory_cli.py
```

---

<a name="japanese"></a>
## 日本語

Ciscoの主要な4つのネットワークドメイン（ACI, Meraki, Catalyst Center, SD-WAN）のインベントリ情報を統合管理するためのツール、および **Model Context Protocol (MCP) サーバー** です。

MCPサーバーとして動作することで、**Claude Desktop** などのAIアシスタントが自然言語であなたのネットワーク構成を直接参照・理解し、トラブルシューティングを支援できるようになります。

### 🚀 主な機能
- **MCPネイティブ**: AI連携のための Model Context Protocol サーバー機能を搭載。
- **マルチドメイン統合**: ACI, Meraki, Catalyst Center, SD-WANを一括サポート。
- **スマートプロンプト**: ヘルスチェックやデバイス調査をワンクリックで実行できる定義済みコマンド。
- **リアルタイムステータス**: 各コントローラから最新のステータス（オンライン/オフライン）を取得。

### 🤖 AIアシスタント活用ガイド (チュートリアル)

Claude Desktopに接続後、**スラッシュコマンド** または **自然言語** で指示を出すことができます。

#### 1. スラッシュコマンド（定型ワークフロー）
チャット欄に `/` を入力し、コマンドをタイプしてください。

| コマンド | 入力例 | 機能説明 |
| :--- | :--- | :--- |
| **`/network_health_check`** | `/net` と入力 | **ヘルスチェック**: 全ドメインのサマリーを取得し、異常（オフライン等）があるデバイスを抽出して日本語レポートを作成します。 |
| **`/investigate_device`** | `/inv` と入力 | **デバイス詳細調査**: IPアドレス、ホスト名、シリアル番号から全ドメインを横断検索し、詳細情報を表示します。 |

#### 2. 自然言語プロンプト例
コマンドを覚えなくても、自然な言葉で質問するだけでAIが適切なツールを自動選択します。

**🔍 検索・探索**
* 「IPアドレス 192.168.10.5 のデバイスを探して」
* 「'JP-Tokyo-Core' という名前のスイッチはどこにある？」
* 「インベントリの中にCatalyst 9300はある？」
* 「シリアル `FGLxxxx` を検索して、モデルとファームウェアバージョンを表示して」

**🏥 ヘルスチェック・状態確認**
* 「Merakiドメインでオフラインになっているデバイスを一覧表示して」
* 「SD-WANファブリックに重大なエラーはある？」
* 「現在到達不能（Unreachable）なデバイスを全てリストアップして」
* 「IP 10.1.1.1 のデバイスの状態を確認して」

**📊 インベントリ分析**
* 「ドメインごとのデバイス総数をサマリーして」
* 「Catalystスイッチのファームウェアバージョンを一覧にして」
* 「Catalystのモデル別内訳を **テキスト形式の棒グラフ** で可視化して」
* 「ACIのSpineとLeafのリストを表形式で作って」
* 「MerakiとSD-WANのデバイス数を比較して」
* 「正常 vs 異常デバイスの比率を示す **Mermaid円グラフ** を生成して」

### 🛠 セットアップ

1. **リポジトリのクローン**:
   ```bash
   git clone https://github.com/kikuta/Cisco-multidomain-inventory.git
   cd Cisco-multidomain-inventory
   ```

2. **仮想環境の作成と有効化**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
   ```

3. **ライブラリのインストール**: 
   ```bash
   pip install -r requirements.txt
   ```

4. **環境設定**: 
   `config.yaml.sample` を `config.yaml` にコピーし、各コントローラの接続情報を入力してください。
   ```bash
   cp config.yaml.sample config.yaml
   ```

---

## 🤖 Claude Desktop (MCP) Configuration

To use this project as an **MCP Server**, add the following to your `claude_desktop_config.json`. 

> [!IMPORTANT]
> **Please replace `<username>` and the path to match your actual environment.**
> **ご自身の環境に合わせて `<username>` やパスを必ず書き換えてください。**

```json
{
  "mcpServers": {
    "cisco-multidomain-inventory": {
      "command": "/Users/<username>/Cisco-multidomain-inventory/.venv/bin/python3",
      "args": [
        "/Users/<username>/Cisco-multidomain-inventory/multidomain_inventory_mcp.py"
      ]
    }
  }
}
```

---

## ⚠️ Disclaimer / 免責事項
This tool is for educational and testing purposes. Please verify in a lab environment before using it in production.
本ツールは学習および技術検証を目的としています。本番環境での利用前には必ず検証環境で動作確認を行ってください。

---

## 👤 Author
* **Kazumasa Ikuta** (kikuta at cisco.com)