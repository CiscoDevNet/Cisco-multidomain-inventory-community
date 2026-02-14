import os
import yaml
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

# SSL警告の抑止
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TIMEOUT = 15

# ==============================================================================
# CONFIGURATION LOADING (Absolute Path Fix)
# 設定読み込み（絶対パス対応版）
# ==============================================================================

# スクリプト自身のディレクトリを取得（これでどこから実行されても大丈夫になります）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

def load_config():
    """config.yaml から設定を読み込む"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # ログにパスを出力してデバッグしやすくする
        print(f"[Error] Config file not found at: {CONFIG_PATH}")
        print("Running with empty configuration.")
        return {"ACI": [], "MERAKI": [], "CATALYST": [], "SDWAN": []}
    except yaml.YAMLError as e:
        print(f"[Error] Failed to parse config.yaml: {e}")
        return {"ACI": [], "MERAKI": [], "CATALYST": [], "SDWAN": []}

# グローバル設定として読み込み
CONFIG = load_config()

def get_proxies(proxy_url):
    """プロキシURLが設定されている場合、requests用の辞書を返す"""
    if proxy_url and isinstance(proxy_url, str) and proxy_url.strip():
        return {"http": proxy_url, "https": proxy_url}
    return None

# ==============================================================================
# Domain Specific Fetch Logic (Single Site)
# 各ドメインの単一サイト用取得ロジック
# ==============================================================================

def fetch_single_aci(site_config):
    """単一のACIサイトからインベントリを取得"""
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies(site_config.get("proxy")) or {})
    host = site_config.get("host")
    user = site_config.get("user")
    password = site_config.get("pass")
    site_name = site_config.get("name", host)

    if not host or not user or not password:
        return []

    try:
        # Login
        url = f"https://{host}/api/aaaLogin.json"
        payload = {"aaaUser": {"attributes": {"name": user, "pwd": password}}}
        res = session.post(url, json=payload, timeout=TIMEOUT)
        res.raise_for_status()
        token = res.json()['imdata'][0]['aaaLogin']['attributes']['token']
        
        # Get Data (Fabric Nodes)
        res = session.get(f"https://{host}/api/node/class/fabricNode.json", cookies={'APIC-cookie': token}, timeout=TIMEOUT)
        
        results = []
        for i in res.json().get('imdata', []):
            attr = i['fabricNode']['attributes']
            results.append({
                "id": attr.get('dn'),
                "domain": "ACI",
                "controller": site_name,
                "name": attr.get('name'),
                "status": attr.get('fabricSt', 'unknown'),
                "model": attr.get('model'),
                "serial": attr.get('serial'),
                "version": attr.get('version'),
                "ip": attr.get('address'),
                "dashboard_url": f"https://{host}/"
            })
        return results
    except Exception as e:
        return [{"domain": "ACI", "controller": site_name, "error": f"Connection failed: {str(e)}"}]

def fetch_single_meraki(org_config):
    """単一のMeraki Orgからインベントリを取得"""
    session = requests.Session()
    session.proxies.update(get_proxies(org_config.get("proxy")) or {})
    api_key = org_config.get("key")
    org_id = str(org_config.get("org_id"))
    org_name = org_config.get("name", org_id)

    if not api_key or not org_id:
        return []

    headers = {"X-Cisco-Meraki-API-Key": api_key}
    
    try:
        # デバイス一覧とステータス一覧を並列で取得（効率化）
        inventory_url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices"
        status_url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices/statuses"
        
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_inv = ex.submit(session.get, inventory_url, headers=headers, timeout=TIMEOUT)
            f_stat = ex.submit(session.get, status_url, headers=headers, timeout=TIMEOUT)
            
            inv_res = f_inv.result()
            stat_res = f_stat.result()
            
        inv_res.raise_for_status()
        stat_res.raise_for_status()
        
        # ステータスをマッピング (Serial -> Status)
        status_map = {s['serial']: s.get('status') for s in stat_res.json()}
        
        results = []
        for d in inv_res.json():
            serial = d.get('serial')
            results.append({
                "id": serial,
                "domain": "Meraki",
                "controller": org_name,
                "name": d.get('name') or serial,
                "status": status_map.get(serial, "unknown"),
                "model": d.get('model'),
                "serial": serial,
                "version": d.get('firmware'),
                "ip": d.get('lanIp') or "Cloud Managed",
                "dashboard_url": f"https://dashboard.meraki.com/o/{org_id}/manage/organization/inventory?search={serial}"
            })
        return results
    except Exception as e:
        return [{"domain": "Meraki", "controller": org_name, "error": f"Connection failed: {str(e)}"}]

def fetch_single_catalyst(site_config):
    """単一のCatalyst Centerからインベントリを取得"""
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies(site_config.get("proxy")) or {})
    host = site_config.get("host")
    user = site_config.get("user")
    password = site_config.get("pass")
    site_name = site_config.get("name", host)

    if not host or not user or not password:
        return []

    try:
        # Auth Token
        auth_url = f"https://{host}/dna/system/api/v1/auth/token"
        res = session.post(auth_url, auth=(user, password), timeout=TIMEOUT)
        res.raise_for_status()
        token = res.json()['Token']
        
        # Get Devices
        dev_url = f"https://{host}/dna/intent/api/v1/network-device"
        res = session.get(dev_url, headers={"X-Auth-Token": token}, timeout=TIMEOUT)
        res.raise_for_status()
        
        results = []
        for d in res.json().get('response', []):
            results.append({
                "id": d.get('id'),
                "domain": "Catalyst",
                "controller": site_name,
                "name": d.get('hostname'),
                "status": d.get('reachabilityStatus', 'unknown'),
                "model": d.get('platformId'),
                "serial": d.get('serialNumber'),
                "version": d.get('softwareVersion'),
                "ip": d.get('managementIpAddress'),
                "dashboard_url": f"https://{host}/dna/assurance/device/details?id={d.get('id')}"
            })
        return results
    except Exception as e:
        return [{"domain": "Catalyst", "controller": site_name, "error": f"Connection failed: {str(e)}"}]

def fetch_single_sdwan(site_config):
    """単一のSD-WAN vManageからインベントリを取得"""
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies(site_config.get("proxy")) or {})
    url = site_config.get("url")
    user = site_config.get("user")
    password = site_config.get("pass")
    site_name = site_config.get("name", url)

    if not url or not user or not password:
        return []

    try:
        # Login (j_security_check)
        login_url = f"{url}/j_security_check"
        session.post(login_url, data={'j_username': user, 'j_password': password}, timeout=TIMEOUT)
        
        # Get Devices
        dev_url = f"{url}/dataservice/device"
        res = session.get(dev_url, timeout=TIMEOUT)
        res.raise_for_status()
        
        results = []
        for d in res.json().get('data', []):
            results.append({
                "id": d.get('uuid'),
                "domain": "SDWAN",
                "controller": site_name,
                "name": d.get('host-name'),
                "status": d.get('status', 'unknown'),
                "model": d.get('device-model'),
                "serial": d.get('uuid'),
                "version": d.get('version'),
                "ip": d.get('system-ip'),
                "dashboard_url": f"{url}/#/app/monitor/network/system?deviceId={d.get('system-ip')}"
            })
        return results
    except Exception as e:
        return [{"domain": "SDWAN", "controller": site_name, "error": f"Connection failed: {str(e)}"}]

# ==============================================================================
# Aggregation Functions
# 集約関数
# ==============================================================================

def get_aci_inventory():
    """設定された全てのACIサイトから取得"""
    sites = CONFIG.get("ACI", [])
    if not sites: return []
    results = []
    with ThreadPoolExecutor(max_workers=len(sites) or 1) as executor:
        for res in executor.map(fetch_single_aci, sites):
            results.extend(res)
    return results

def get_meraki_inventory():
    """設定された全てのMeraki Orgから取得"""
    orgs = CONFIG.get("MERAKI", [])
    if not orgs: return []
    results = []
    with ThreadPoolExecutor(max_workers=len(orgs) or 1) as executor:
        for res in executor.map(fetch_single_meraki, orgs):
            results.extend(res)
    return results

def get_catalyst_inventory():
    """設定された全てのCatalyst Centerから取得"""
    sites = CONFIG.get("CATALYST", [])
    if not sites: return []
    results = []
    with ThreadPoolExecutor(max_workers=len(sites) or 1) as executor:
        for res in executor.map(fetch_single_catalyst, sites):
            results.extend(res)
    return results

def get_sdwan_inventory():
    """設定された全てのSD-WAN vManageから取得"""
    sites = CONFIG.get("SDWAN", [])
    if not sites: return []
    results = []
    with ThreadPoolExecutor(max_workers=len(sites) or 1) as executor:
        for res in executor.map(fetch_single_sdwan, sites):
            results.extend(res)
    return results

def get_all_inventory():
    """登録されている全ドメイン・全サイトから一括並列取得"""
    tasks = [get_aci_inventory, get_meraki_inventory, get_catalyst_inventory, get_sdwan_inventory]
    combined_data = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        for future in [executor.submit(t) for t in tasks]:
            try:
                res = future.result()
                if isinstance(res, list): combined_data.extend(res)
            except Exception as e:
                combined_data.append({"error": f"Domain fetch error: {str(e)}"})
    return combined_data