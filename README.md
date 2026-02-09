# Cisco Multi-domain Inventory Tool & MCP Server

[English](#english) | [日本語](#japanese)

---

<a name="english"></a>
## English

This is a unified tool and **Model Context Protocol (MCP) Server** designed to retrieve and manage inventory information from four major Cisco network domains: ACI, Meraki, Catalyst Center, and SD-WAN. 

By acting as an MCP server, it allows AI assistants like **Claude Desktop** to directly query and understand your network infrastructure using natural language.

### 🚀 Key Features
- **MCP Native**: Functions as a Model Context Protocol server for seamless AI integration.
- **Multi-domain Integration**: Supports ACI, Meraki, Catalyst Center, and SD-WAN.
- **Multiple Interfaces**: Web UI, CLI, and MCP.
- **AI Ready**: Empower your AI assistant with real-time network visibility.

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

MCPサーバーとして動作することで、**Claude Desktop** などのAIアシスタントが自然言語であなたのネットワーク構成を直接参照・理解できるようになります。

### 🚀 主な機能
- **MCPネイティブ**: AI連携のための Model Context Protocol サーバー機能を搭載。
- **マルチドメイン統合**: ACI, Meraki, Catalyst Center, SD-WANを一括サポート。
- **多様なインターフェース**: Web UI、CLI、および MCP に対応。
- **AI Ready**: リアルタイムのネットワーク情報をAIに学習・参照させることが可能。

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