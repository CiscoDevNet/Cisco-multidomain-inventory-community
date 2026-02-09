import json
from mcp.server.fastmcp import FastMCP
from multidomain_inventory_core import get_all_inventory, get_aci_inventory, get_meraki_inventory, get_catalyst_inventory, get_sdwan_inventory

mcp = FastMCP("Cisco-MultiDomain-Inventory")

@mcp.tool()
def get_full_inventory() -> str:
    """Retrieve inventory from all domains (ACI, Meraki, Catalyst, SD-WAN)."""
    return json.dumps(get_all_inventory(), indent=2, ensure_ascii=False)

@mcp.tool()
def get_domain_inventory(domain: str) -> str:
    """Retrieve inventory for a specific domain (aci, meraki, catalyst, sdwan)."""
    d = domain.lower()
    if "aci" in d: return json.dumps(get_aci_inventory(), indent=2)
    if "meraki" in d: return json.dumps(get_meraki_inventory(), indent=2)
    if "catalyst" in d: return json.dumps(get_catalyst_inventory(), indent=2)
    if "sdwan" in d: return json.dumps(get_sdwan_inventory(), indent=2)
    return "Unknown domain"

if __name__ == "__main__":
    mcp.run()