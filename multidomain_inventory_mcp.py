import json
from mcp.server.fastmcp import FastMCP
from multidomain_inventory_core import (
    get_all_inventory, 
    get_aci_inventory, 
    get_meraki_inventory, 
    get_catalyst_inventory, 
    get_sdwan_inventory
)

# Initialize FastMCP server
# FastMCPサーバーの初期化
mcp = FastMCP("Cisco-MultiDomain-Inventory")

# --- Resources: Static or summary information for context ---
# --- リソース: コンテキスト把握のための静的情報またはサマリー ---

@mcp.resource("inventory://summary")
def get_inventory_summary() -> str:
    """
    Returns a high-level summary of the network inventory across all domains.
    Includes total device counts, breakdown by domain, and a count of unhealthy devices.
    
    全ドメインにわたるネットワークインベントリの概要サマリーを返します。
    デバイス総数、ドメインごとの内訳、および異常な状態のデバイス数を含みます。
    """
    # Get data from all domains
    # 全ドメインからデータを取得
    data = get_all_inventory()
    
    # Define statuses that are considered "unhealthy"
    # "異常 (unhealthy)" とみなされるステータスを定義
    unhealthy_statuses = ["offline", "unreachable", "error", "inactive", "alerting", "unknown"]
    
    summary = {
        "total_devices": len(data),
        "by_domain": {},
        "health_issues": 0
    }
    
    for device in data:
        # Count by domain
        # ドメインごとにカウント
        domain = device.get("domain", "Unknown")
        summary["by_domain"][domain] = summary["by_domain"].get(domain, 0) + 1
        
        # Check for health issues
        # 健康状態（異常有無）のチェック
        status = str(device.get("status", "")).lower()
        if "error" in device or status in unhealthy_statuses:
            summary["health_issues"] += 1
            
    return json.dumps(summary, indent=2, ensure_ascii=False)

# --- Tools: Actions the LLM can perform ---
# --- ツール: LLMが実行可能なアクション ---

@mcp.tool()
def get_full_inventory() -> str:
    """
    Retrieves the complete inventory list from all registered domains (ACI, Meraki, Catalyst, SD-WAN).
    Use this sparingly as the output can be large.
    
    登録されている全ドメイン (ACI, Meraki, Catalyst, SD-WAN) から完全なインベントリリストを取得します。
    出力が大きくなる可能性があるため、必要な場合のみ使用してください。
    """
    return json.dumps(get_all_inventory(), indent=2, ensure_ascii=False)

@mcp.tool()
def get_domain_inventory(domain: str) -> str:
    """
    Retrieves inventory for a specific network domain.
    
    特定のネットワークドメインのインベントリを取得します。
    
    Args:
        domain: The target domain (valid options: 'aci', 'meraki', 'catalyst', 'sdwan').
                対象ドメイン（有効な値: 'aci', 'meraki', 'catalyst', 'sdwan'）。
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
            
    # Return error message if domain is not found
    # ドメインが見つからない場合はエラーメッセージを返す
    return f"Error: '{domain}' is not a supported domain. Available options: {list(domain_map.keys())}"

@mcp.tool()
def search_devices(query: str) -> str:
    """
    Searches for devices across all domains by matching a keyword.
    
    キーワードを使用して全ドメインのデバイスを横断検索します。
    
    Args:
        query: The search term (matches against Name, Serial Number, IP Address, or ID).
               検索語句（名前、シリアル番号、IPアドレス、またはIDに一致）。
    """
    data = get_all_inventory()
    q = query.lower()
    
    # Filter devices matching the query
    # クエリに一致するデバイスをフィルタリング
    results = [
        d for d in data 
        if q in str(d.get("name", "")).lower() or 
           q in str(d.get("serial", "")).lower() or 
           q in str(d.get("ip", "")).lower() or
           q in str(d.get("id", "")).lower()
    ]
    
    if not results:
        return f"No devices found matching query: '{query}'"
        
    return json.dumps(results, indent=2, ensure_ascii=False)

@mcp.tool()
def get_unhealthy_devices() -> str:
    """
    Retrieves a list of devices that are currently in an abnormal state.
    Filters for statuses such as 'offline', 'unreachable', 'error', 'inactive', or 'alerting'.
    Useful for troubleshooting and health checks.
    
    現在異常な状態にあるデバイスのリストを取得します。
    'offline', 'unreachable', 'error', 'inactive', 'alerting' などのステータスでフィルタリングします。
    トラブルシューティングやヘルスチェックに役立ちます。
    """
    data = get_all_inventory()
    unhealthy_statuses = ["offline", "unreachable", "error", "inactive", "alerting"]
    
    issues = [
        d for d in data 
        if str(d.get("status", "")).lower() in unhealthy_statuses or "error" in d
    ]
    
    if not issues:
        return "No unhealthy devices found. All systems appear normal."
        
    return json.dumps(issues, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()