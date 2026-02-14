import json
from mcp.server.fastmcp import FastMCP
from multidomain_inventory_core import (
    get_all_inventory, 
    get_aci_inventory, 
    get_meraki_inventory, 
    get_catalyst_inventory, 
    get_sdwan_inventory
)

mcp = FastMCP("Cisco-MultiDomain-Inventory")

# --- Resources: LLMが参照できる静的な情報 ---

@mcp.resource("inventory://summary")
def get_inventory_summary() -> str:
    """インベントリの全体統計（ドメインごとのデバイス数と状態）を返します。"""
    data = get_all_inventory()
    summary = {
        "total_devices": len(data),
        "by_domain": {},
        "issues_found": len([d for d in data if "error" in d or d.get("status") in ["offline", "unreachable", "error"]])
    }
    
    for device in data:
        domain = device.get("domain", "Unknown")
        summary["by_domain"][domain] = summary["by_domain"].get(domain, 0) + 1
        
    return json.dumps(summary, indent=2, ensure_ascii=False)

# --- Tools: LLMが実行できるアクション ---

@mcp.tool()
def get_full_inventory() -> str:
    """すべてのドメイン(ACI, Meraki, Catalyst, SD-WAN)から全インベントリを取得します。"""
    return json.dumps(get_all_inventory(), indent=2, ensure_ascii=False)

@mcp.tool()
def get_domain_inventory(domain: str) -> str:
    """
    指定したドメインのインベントリのみを取得します。
    引数: aci, meraki, catalyst, sdwan
    """
    domain_map = {
        "aci": get_aci_inventory,
        "meraki": get_meraki_inventory,
        "catalyst": get_catalyst_inventory,
        "sdwan": get_sdwan_inventory
    }
    
    d = domain.lower()
    for key, func in domain_map.items():
        if key in d:
            return json.dumps(func(), indent=2, ensure_ascii=False)
            
    return f"Error: '{domain}' は不明なドメインです。aci, meraki, catalyst, sdwan のいずれかを指定してください。"

@mcp.tool()
def search_devices(query: str) -> str:
    """
    名前、シリアル番号、IPアドレス、またはIDでデバイスを横断検索します。
    """
    data = get_all_inventory()
    query = query.lower()
    results = [
        d for d in data 
        if query in str(d.get("name", "")).lower() or 
           query in str(d.get("serial", "")).lower() or 
           query in str(d.get("ip", "")).lower() or
           query in str(d.get("id", "")).lower()
    ]
    return json.dumps(results, indent=2, ensure_ascii=False)

@mcp.tool()
def get_unhealthy_devices() -> str:
    """
    ステータスが異常（offline, unreachable, error等）なデバイスのみを抽出して返します。
    """
    data = get_all_inventory()
    unhealthy_statuses = ["offline", "unreachable", "error", "inactive", "alerting"]
    
    issues = [
        d for d in data 
        if d.get("status", "").lower() in unhealthy_statuses or "error" in d
    ]
    return json.dumps(issues, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()