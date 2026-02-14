import os
import requests
import urllib3
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# .env ファイルを読み込む
load_dotenv()

# SSL警告の抑止
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TIMEOUT = 15

# --- 共通設定 ---
CONFIG = {
    "ACI": {
        "HOST": os.getenv("ACI_HOST"),
        "USER": os.getenv("ACI_USER"),
        "PASS": os.getenv("ACI_PASS"),
        "PROXY": os.getenv("ACI_PROXY"),
    },
    "MERAKI": {
        "KEY": os.getenv("MERAKI_KEY"),
        "ORG_ID": os.getenv("MERAKI_ORG_ID"),
        "PROXY": os.getenv("MERAKI_PROXY"),
    },
    "CATALYST": {
        "HOST": os.getenv("CAT_HOST"),
        "USER": os.getenv("CAT_USER"),
        "PASS": os.getenv("CAT_PASS"),
        "PROXY": os.getenv("CAT_PROXY"),
    },
    "SDWAN": {
        "URL": os.getenv("SDWAN_URL"),
        "USER": os.getenv("SDWAN_USER"),
        "PASS": os.getenv("SDWAN_PASS"),
        "PROXY": os.getenv("SDWAN_PROXY"),
    }
}

def get_proxies(domain_key):
    p = CONFIG[domain_key].get("PROXY")
    return {"http": p, "https": p} if p else None

# --- 各ドメイン取得ロジック ---

def get_aci_inventory():
    """ACI (APIC) からインベントリを取得"""
    if not CONFIG["ACI"]["HOST"]: return []
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies("ACI") or {})
    host = CONFIG["ACI"]["HOST"]
    
    try:
        # Login
        url = f"https://{host}/api/aaaLogin.json"
        res = session.post(url, json={"aaaUser":{"attributes":{"name":CONFIG["ACI"]["USER"],"pwd":CONFIG["ACI"]["PASS"]}}}, timeout=TIMEOUT)
        res.raise_for_status()
        token = res.json()['imdata'][0]['aaaLogin']['attributes']['token']
        
        # Get Data
        res = session.get(f"https://{host}/api/node/class/fabricNode.json", cookies={'APIC-cookie': token}, timeout=TIMEOUT)
        
        return [{
            "id": i['fabricNode']['attributes'].get('dn'), # Distinguished Name をIDに使用
            "domain": "ACI",
            "name": i['fabricNode']['attributes'].get('name'),
            "status": i['fabricNode']['attributes'].get('fabricSt', 'unknown'), # active, inactive etc.
            "model": i['fabricNode']['attributes'].get('model'),
            "serial": i['fabricNode']['attributes'].get('serial'),
            "version": i['fabricNode']['attributes'].get('version'),
            "ip": i['fabricNode']['attributes'].get('address'),
            "dashboard_url": f"https://{host}/"
        } for i in res.json().get('imdata', [])]
    except Exception as e: return [{"domain": "ACI", "error": str(e)}]

def get_meraki_inventory():
    """Meraki Dashboard API からインベントリとステータスを取得"""
    if not CONFIG["MERAKI"]["KEY"]: return []
    session = requests.Session()
    session.proxies.update(get_proxies("MERAKI") or {})
    headers = {"X-Cisco-Meraki-API-Key": CONFIG["MERAKI"]["KEY"]}
    org_id = CONFIG["MERAKI"]["ORG_ID"]
    
    try:
        # デバイス一覧とステータス一覧を並列で取得（効率化）
        inventory_url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices"
        status_url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices/statuses"
        
        inv_res = session.get(inventory_url, headers=headers, timeout=TIMEOUT)
        stat_res = session.get(status_url, headers=headers, timeout=TIMEOUT)
        
        # ステータスをマッピング (Serial -> Status)
        status_map = {s['serial']: s.get('status') for s in stat_res.json()}
        
        results = []
        for d in inv_res.json():
            serial = d.get('serial')
            results.append({
                "id": serial,
                "domain": "Meraki",
                "name": d.get('name') or serial,
                "status": status_map.get(serial, "unknown"), # online, offline, alerting
                "model": d.get('model'),
                "serial": serial,
                "version": d.get('firmware'),
                "ip": d.get('lanIp') or "Cloud Managed",
                "dashboard_url": f"https://dashboard.meraki.com/o/{org_id}/manage/organization/inventory?search={serial}"
            })
        return results
    except Exception as e: return [{"domain": "Meraki", "error": str(e)}]

def get_catalyst_inventory():
    """Catalyst Center (DNA Center) からインベントリを取得"""
    if not CONFIG["CATALYST"]["HOST"]: return []
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies("CATALYST") or {})
    host = CONFIG["CATALYST"]["HOST"]
    try:
        # Auth
        res = session.post(f"https://{host}/dna/system/api/v1/auth/token", auth=(CONFIG["CATALYST"]["USER"], CONFIG["CATALYST"]["PASS"]), timeout=TIMEOUT)
        token = res.json()['Token']
        
        # Get Devices
        res = session.get(f"https://{host}/dna/intent/api/v1/network-device", headers={"X-Auth-Token": token}, timeout=TIMEOUT)
        return [{
            "id": d.get('id'),
            "domain": "Catalyst",
            "name": d.get('hostname'),
            "status": d.get('reachabilityStatus', 'unknown'), # Reachable, Unreachable
            "model": d.get('platformId'),
            "serial": d.get('serialNumber'),
            "version": d.get('softwareVersion'),
            "ip": d.get('managementIpAddress'),
            "dashboard_url": f"https://{host}/dna/assurance/device/details?id={d.get('id')}"
        } for d in res.json().get('response', [])]
    except Exception as e: return [{"domain": "Catalyst", "error": str(e)}]

def get_sdwan_inventory():
    """Cisco SD-WAN Manager (vManage) からインベントリを取得"""
    if not CONFIG["SDWAN"]["URL"]: return []
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies("SDWAN") or {})
    url = CONFIG["SDWAN"]["URL"]
    try:
        # Login
        session.post(f"{url}/j_security_check", data={'j_username': CONFIG["SDWAN"]["USER"], 'j_password': CONFIG["SDWAN"]["PASS"]}, timeout=TIMEOUT)
        
        # Get Devices
        res = session.get(f"{url}/dataservice/device", timeout=TIMEOUT)
        return [{
            "id": d.get('uuid'),
            "domain": "SDWAN",
            "name": d.get('host-name'),
            "status": d.get('status', 'unknown'), # normal, error etc.
            "model": d.get('device-model'),
            "serial": d.get('uuid'),
            "version": d.get('version'),
            "ip": d.get('system-ip'),
            "dashboard_url": f"{url}/#/app/monitor/network/system?deviceId={d.get('system-ip')}"
        } for d in res.json().get('data', [])]
    except Exception as e: return [{"domain": "SDWAN", "error": str(e)}]

def get_all_inventory():
    """すべてのドメインから並列でデータを取得する"""
    tasks = [
        get_aci_inventory,
        get_meraki_inventory,
        get_catalyst_inventory,
        get_sdwan_inventory
    ]
    
    combined_data = []
    # 最大4スレッドで並列実行
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = [executor.submit(t) for t in tasks]
        for future in futures:
            try:
                result = future.result()
                if isinstance(result, list):
                    combined_data.extend(result)
            except Exception as e:
                combined_data.append({"domain": "System", "error": f"Thread error: {str(e)}"})
                
    return combined_data