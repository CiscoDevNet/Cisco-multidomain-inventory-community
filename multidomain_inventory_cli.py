# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: MIT

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
    GRAY_TXT = '\033[90m'

    # 背景色 (Badge Style)
    BG_BLUE = '\033[44m'    # ACI
    BG_GREEN = '\033[42m'   # Meraki
    BG_CYAN = '\033[46m'    # Catalyst
    BG_PURPLE = '\033[45m'  # SD-WAN
    BG_DEFAULT = '\033[40m' # Unknown

def get_badge_color(domain):
    """ドメインに応じたバッジ色(背景色+文字色)を返す"""
    d = str(domain).lower()
    if "aci" in d:      return Colors.BG_BLUE + Colors.WHITE_TXT
    if "meraki" in d:   return Colors.BG_GREEN + Colors.WHITE_TXT
    if "catalyst" in d: return Colors.BG_CYAN + Colors.BLACK_TXT
    if "sdwan" in d:    return Colors.BG_PURPLE + Colors.WHITE_TXT
    return Colors.BG_DEFAULT + Colors.WHITE_TXT

def main():
    print(f"\n{Colors.BOLD}🚀 Starting Multi-Domain Inventory Collector (CLI)...{Colors.RESET}\n")
    
    start_time = time.time()
    
    # データの取得（並列処理）
    print(f"{Colors.GRAY_TXT}Fetching data from all configured controllers...{Colors.RESET}")
    data = get_all_inventory()
    
    # --- ヘッダーの表示 ---
    # レイアウト: [DOMAINバッジ] [CONTROLLER名] [DEVICE NAME] ...
    # ANSIエスケープシーケンスがあるため、formatメソッドでの完全な位置合わせは難しい。
    # 視覚的なスペース数を計算してヘッダーを作成します。
    
    # Domain(12) + Controller(18) + Name(25) + Model(20) + Serial(18) + Version(15) + URL
    header_str = f"{'DOMAIN':<12} {'CONTROLLER':<18} {'NAME':<25} {'MODEL':<20} {'SERIAL':<18} {'VERSION':<15} {'URL'}"
    
    print("-" * 150)
    print(Colors.BOLD + header_str + Colors.RESET)
    print("-" * 150)
    
    for row in data:
        domain = row.get('domain', 'Unknown')
        controller = row.get('controller', '-') # core側で追加したcontrollerフィールドを取得
        
        # バッジ色の決定
        badge_color = get_badge_color(domain)
        
        # ドメインバッジの作成 (10文字幅でセンタリング)
        # 注意: 色コード自体は文字数に含まれないが、表示上のズレを防ぐためバッジ部分は独立してprintする
        domain_str = f"{badge_color} {domain:^10} {Colors.RESET}"

        # エラー行の処理
        if "error" in row:
            # エラー時もコントローラ名は表示して、どこが落ちているか分かるようにする
            print(f"{domain_str} "
                  f"{str(controller)[:17]:<18} "
                  f"{Colors.RED_TXT}Error: {row['error']}{Colors.RESET}")
            continue
            
        # 通常行の表示
        print(f"{domain_str} "
              f"{str(controller)[:17]:<18} " # コントローラ名（長すぎたらカット）
              f"{str(row.get('name', ''))[:24]:<25} "
              f"{str(row.get('model', ''))[:19]:<20} "
              f"{str(row.get('serial', ''))[:17]:<18} "
              f"{str(row.get('version', ''))[:14]:<15} "
              f"{row.get('dashboard_url', '')}")
              
    print("-" * 150)
    print(f"{Colors.BOLD}📊 Total Devices: {len(data)}{Colors.RESET}")
    print(f"✨ Completed in {time.time() - start_time:.2f} seconds.\n")

if __name__ == "__main__":
    main()