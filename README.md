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

Once connected to Claude Desktop, you can use the following pre-defined **Prompts** to automate complex tasks.

#### 1. Network Health Check
Instantly analyze the status of all devices across all domains.
* **Command**: Type `/` in Claude and select **`network_health_check`**
* **What it does**:
    1.  Retrieves a summary of all devices.
    2.  Identifies any "unhealthy" devices (offline, errors, alerts).
    3.  **Output**: Generates a structured report with tables, highlighting critical issues in bold.

#### 2. Device Investigation
Search for a specific device across all domains using its Name, IP, or Serial Number.
* **Command**: Type `/` and select **`investigate_device`** (then enter the IP or Hostname)
* **What it does**:
    1.  Searches across ACI, Meraki, Catalyst, and SD-WAN simultaneously.
    2.  **Output**: Displays a detailed table with the device's status, model, firmware version, and a direct link to its dashboard.

#### 3. Natural Language Queries
You can also ask free-form questions. The AI will automatically select the right tools (`search_devices`, `get_unhealthy_devices`, etc.).
* *"Show me all offline devices in the Meraki domain."*
* *"What is the firmware version of the switch with IP 192.168.1.5?"*
* *"Summarize the total number of devices per domain."*

### 🛠 Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/kikuta/Cisco-multidomain-inventory.git](https://github.com/kikuta/Cisco-multidomain-inventory.git)
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

4. **Environment Variables**: 
   Copy `.env.sample` to `.env` and fill in your controller credentials.
   ```bash
   cp .env.sample .env
   ```

### 💻 Interface Examples

#### AI Assistant (via MCP)
Interact with your network infrastructure using natural language in Claude Desktop.
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

Claude Desktopに接続後、以下の定義済み **プロンプト（Prompts）** を使用することで、複雑な調査を自動化できます。

#### 1. ネットワーク・ヘルスチェック
全ドメインのデバイス状態を即座に診断します。
* **使い方**: Claudeの入力欄で `/` を入力し、メニューから **`network_health_check`** を選択（または入力）します。
* **動作**:
    1.  全デバイスのサマリーを取得します。
    2.  「異常あり（Unhealthy）」なデバイス（オフライン、エラー等）を自動抽出します。
    3.  **結果**: 日本語のテーブル形式でレポートを作成し、問題箇所を太字で強調表示します。

#### 2. デバイス詳細調査
IPアドレス、ホスト名、シリアル番号を使って、全ドメインを横断検索します。
* **使い方**: Claudeの入力欄で `/` を入力し、 **`investigate_device`** を選択します（引数として対象のIPや名前を入力）。
* **動作**:
    1.  ACI, Meraki, Catalyst, SD-WAN の全域から対象を検索します。
    2.  **結果**: ステータス、モデル、ファームウェアバージョン、管理画面への直リンクなどをテーブル形式で表示します。

#### 3. 自然言語による対話
プロンプトを使わずに、自然な会話で質問することも可能です。AIが適切なツール（`search_devices` や `get_unhealthy_devices`）を自動で選択します。
* *「Merakiドメインで落ちているデバイスを全部教えて」*
* *「IPアドレス 192.168.1.5 のスイッチのバージョンは？」*
* *「現在のネットワーク全体の台数サマリーを作って」*

### 🛠 セットアップ

1. **リポジトリのクローン**:
   ```bash
   git clone [https://github.com/kikuta/Cisco-multidomain-inventory.git](https://github.com/kikuta/Cisco-multidomain-inventory.git)
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
   `.env.sample` を `.env` にコピーし、各コントローラの接続情報を入力してください。
   ```bash
   cp .env.sample .env
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
* **Kazumasa Ikuta** (kikuta@cisco.com)