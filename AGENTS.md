# Cisco Multi-domain Inventory Tool & MCP Server

A unified tool and **Model Context Protocol (MCP) Server** that retrieves and manages inventory from four Cisco network domains: **ACI**, **Meraki**, **Catalyst Center**, and **SD-WAN**.

## Dev environment tips

- **Python version**: Use Python 3.9+.
- **Virtual env (recommended)**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install -U pip
  pip install -r requirements.txt
  ```

- **Configuration**: Copy `config.yaml.sample` to `config.yaml` and fill in your controller credentials. Never commit `config.yaml` (it contains secrets).
  ```bash
  cp config.yaml.sample config.yaml
  ```

### Quick run examples

- **CLI** (table output in terminal):
  ```bash
  python multidomain_inventory_cli.py
  ```
- **Web dashboard** (Flask, serves at `http://127.0.0.1:5001`):
  ```bash
  python multidomain_inventory_web.py
  ```
- **MCP server** (for AI assistant integration, e.g. Claude Desktop):
  ```bash
  python multidomain_inventory_mcp.py
  ```

## Testing instructions

- **MCP server**: This project includes `multidomain_inventory_mcp.py`, a FastMCP-based server. Configure it in Claude Desktop's `claude_desktop_config.json`:
  ```json
  {
    "mcpServers": {
      "cisco-multidomain-inventory": {
        "command": "/path/to/.venv/bin/python3",
        "args": ["/path/to/multidomain_inventory_mcp.py"]
      }
    }
  }
  ```

- **Test the code with the Cisco DevNet sandbox**

  Visit https://devnetsandbox.cisco.com/DevNet to book a related sandbox.

- **Latest Cisco API documentation**:

  - ACI: https://developer.cisco.com/docs/aci/
  - Meraki: https://developer.cisco.com/meraki/api-v1/
  - Catalyst Center: https://developer.cisco.com/docs/dna-center/
  - SD-WAN: https://developer.cisco.com/docs/sdwan/

## PR instructions

- **Security**: Do not commit real credentials or tokens. Controller credentials belong in `config.yaml`, which must stay in `.gitignore`. Use `config.yaml.sample` for placeholder examples.

## Contribution conventions

- **Backward compatibility**: Do not change existing sample behavior unless clearly improving or fixing a bug; document changes.
- **Copyright header**: Every `.py` file must begin with:
  ```
  # Copyright 2026 Cisco Systems, Inc. and its affiliates
  #
  # SPDX-License-Identifier: MIT
  ```
