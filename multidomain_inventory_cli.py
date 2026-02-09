import sys
import time
from multidomain_inventory_core import get_all_inventory

# --- カラー設定 (GUIのバッジ風にするため背景色を使用) ---
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # 文字色
    WHITE_TXT = '\033[97m'
    BLACK_TXT = '\033[30m'
    RED_TXT = '\033[91m'

    # 背景色 (Badge Style)
    BG_BLUE = '\033[44m'    # ACI
    BG_GREEN = '\033[42m'   # Meraki
    BG_CYAN = '\033[46m'    # Catalyst
    BG_PURPLE = '\033[45m'  # SD-WAN

def get_badge_color(domain):
    """ドメインに応じたバッジ色(背景色+文字色)を返す"""
    d = domain.lower()
    if "aci" in d:      return Colors.BG_BLUE + Colors.WHITE_TXT
    if "meraki" in d:   return Colors.BG_GREEN + Colors.WHITE_TXT
    if "catalyst" in d: return Colors.BG_CYAN + Colors.BLACK_TXT # Cyanは見にくいので黒文字
    if "sdwan" in d:    return Colors.BG_PURPLE + Colors.WHITE_TXT
    return Colors.RESET

def main():
    print(f"\n{Colors.BOLD}🚀 Starting Multi-Domain Inventory Collector (CLI)...{Colors.RESET}\n")
    
    start_time = time.time()
    data = get_all_inventory()
    
    # テーブルフォーマット
    # Domainカラムの幅を少し調整
    fmt = "{:<14} {:<25} {:<20} {:<18} {:<15} {}"
    
    print("-" * 130)
    print(Colors.BOLD + fmt.format("DOMAIN", "NAME", "MODEL", "SERIAL", "VERSION", "URL") + Colors.RESET)
    print("-" * 130)
    
    for row in data:
        domain = row.get('domain', 'Unknown')
        
        # バッジ色の決定
        badge_color = get_badge_color(domain)
        
        # ドメイン部分のフォーマット (色開始 -> テキスト -> 色リセット)
        # 10文字分の幅でスペース埋めし、その背景を塗る
        domain_str = f"{badge_color} {domain:^10} {Colors.RESET}"

        if "error" in row:
            print(f"{domain_str} {Colors.RED_TXT}Error: {row['error']}{Colors.RESET}")
            continue
            
        print(f"{domain_str} "
              f"{str(row.get('name', ''))[:25]:<25} "
              f"{str(row.get('model', ''))[:20]:<20} "
              f"{str(row.get('serial', ''))[:18]:<18} "
              f"{str(row.get('version', ''))[:15]:<15} "
              f"{row.get('dashboard_url', '')}")
              
    print("-" * 130)
    print(f"{Colors.BOLD}📊 Total Devices: {len(data)}{Colors.RESET}")
    print(f"✨ Completed in {time.time() - start_time:.2f} seconds.\n")

if __name__ == "__main__":
    main()