import os
import requests
import urllib3
from dotenv import load_dotenv

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
    if not CONFIG["ACI"]["HOST"]: return [{"domain": "ACI", "error": "Missing Config"}]
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
            "domain": "ACI",
            "name": i['fabricNode']['attributes'].get('name'),
            "model": i['fabricNode']['attributes'].get('model'),
            "serial": i['fabricNode']['attributes'].get('serial'),
            "version": i['fabricNode']['attributes'].get('version'),
            "ip": i['fabricNode']['attributes'].get('address'),
            "dashboard_url": f"https://{host}/"
        } for i in res.json().get('imdata', [])]
    except Exception as e: return [{"domain": "ACI", "error": str(e)}]

def get_meraki_inventory():
    if not CONFIG["MERAKI"]["KEY"]: return [{"domain": "Meraki", "error": "Missing Config"}]
    session = requests.Session()
    session.proxies.update(get_proxies("MERAKI") or {})
    try:
        url = f"https://api.meraki.com/api/v1/organizations/{CONFIG['MERAKI']['ORG_ID']}/devices"
        res = session.get(url, headers={"X-Cisco-Meraki-API-Key": CONFIG["MERAKI"]["KEY"]}, timeout=TIMEOUT)
        results = []
        for d in res.json():
            serial = d.get('serial')
            results.append({
                "domain": "Meraki",
                "name": d.get('name') or serial,
                "model": d.get('model'),
                "serial": serial,
                "version": d.get('firmware'),
                "ip": d.get('lanIp') or "Cloud",
                "dashboard_url": f"https://dashboard.meraki.com/o/{CONFIG['MERAKI']['ORG_ID']}/manage/organization/inventory?search={serial}"
            })
        return results
    except Exception as e: return [{"domain": "Meraki", "error": str(e)}]

def get_catalyst_inventory():
    if not CONFIG["CATALYST"]["HOST"]: return [{"domain": "Catalyst", "error": "Missing Config"}]
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies("CATALYST") or {})
    host = CONFIG["CATALYST"]["HOST"]
    try:
        res = session.post(f"https://{host}/dna/system/api/v1/auth/token", auth=(CONFIG["CATALYST"]["USER"], CONFIG["CATALYST"]["PASS"]), timeout=TIMEOUT)
        token = res.json()['Token']
        res = session.get(f"https://{host}/dna/intent/api/v1/network-device", headers={"X-Auth-Token": token}, timeout=TIMEOUT)
        return [{
            "domain": "Catalyst",
            "name": d.get('hostname'),
            "model": d.get('platformId'),
            "serial": d.get('serialNumber'),
            "version": d.get('softwareVersion'),
            "ip": d.get('managementIpAddress'),
            "dashboard_url": f"https://{CONFIG['CATALYST']['USER']}@{host}/dna/assurance/device/details?id={d.get('id')}"
        } for d in res.json()['response']]
    except Exception as e: return [{"domain": "Catalyst", "error": str(e)}]

def get_sdwan_inventory():
    if not CONFIG["SDWAN"]["URL"]: return [{"domain": "SDWAN", "error": "Missing Config"}]
    session = requests.Session()
    session.verify = False
    session.proxies.update(get_proxies("SDWAN") or {})
    url = CONFIG["SDWAN"]["URL"]
    try:
        session.post(f"{url}/j_security_check", data={'j_username': CONFIG["SDWAN"]["USER"], 'j_password': CONFIG["SDWAN"]["PASS"]}, timeout=TIMEOUT)
        res = session.get(f"{url}/dataservice/device", timeout=TIMEOUT)
        return [{
            "domain": "SDWAN",
            "name": d.get('host-name'),
            "model": d.get('device-model'),
            "serial": d.get('uuid'),
            "version": d.get('version'),
            "ip": d.get('system-ip'),
            "dashboard_url": f"{url}/#/app/monitor/network/system?deviceId={d.get('system-ip')}"
        } for d in res.json()['data']]
    except Exception as e: return [{"domain": "SDWAN", "error": str(e)}]

def get_all_inventory():
    data = []
    data.extend(get_aci_inventory())
    data.extend(get_meraki_inventory())
    data.extend(get_catalyst_inventory())
    data.extend(get_sdwan_inventory())
    return data