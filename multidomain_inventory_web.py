from flask import Flask, render_template_string, make_response, redirect, url_for
import io
import csv
import time
from multidomain_inventory_core import get_all_inventory

app = Flask(__name__)

# --- グローバルキャッシュ (Web表示の高速化用) ---
DATA_CACHE = None
LAST_UPDATE = 0
CACHE_DURATION = 300 # 5分間はキャッシュを使う

# --- UIテキスト (多言語対応) ---
UI_TEXT = {
    'en': {
        'title': 'Cisco Multi-Domain Asset Tracker',
        'subtitle': 'Unified visibility: ACI, Meraki, Catalyst Center, & SD-WAN',
        'btn_csv': 'Export to CSV',
        'btn_refresh': 'Refresh Data',
        'lbl_total': 'Total Devices',
        'lbl_controller_breakdown': 'Breakdown by Controller',
        'col_domain': 'Domain', 'col_controller': 'Controller / Site', 'col_name': 'Name (Click for Detail)', 
        'col_model': 'Model', 'col_serial': 'Serial / UUID', 'col_version': 'Version', 'col_ip': 'Mgmt / System IP'
    },
    'ja': {
        'title': 'Cisco マルチドメイン 資産管理ダッシュボード',
        'subtitle': 'ACI, Meraki, Catalyst Center, SD-WAN の統合可視化',
        'btn_csv': 'CSVでエクスポート',
        'btn_refresh': 'データを最新化',
        'lbl_total': '総デバイス数',
        'lbl_controller_breakdown': 'コントローラ別 内訳',
        'col_domain': 'ドメイン', 'col_controller': 'コントローラ / 拠点', 'col_name': 'ホスト名 (クリックで詳細)', 
        'col_model': 'モデル', 'col_serial': 'シリアル / UUID', 'col_version': 'バージョン', 'col_ip': '管理IP / System IP'
    },
    'ko': {
        'title': 'Cisco 멀티도메인 자산 관리 대시보드',
        'subtitle': 'ACI, Meraki, Catalyst Center, SD-WAN 통합 가시성',
        'btn_csv': 'CSV로 내보내기',
        'btn_refresh': '데이터 새로고침',
        'lbl_total': '총 장치 수',
        'lbl_controller_breakdown': '컨트롤러 별 내역',
        'col_domain': '도메인', 'col_controller': '컨트롤러 / 사이트', 'col_name': '호스트 이름 (클릭 시 상세)', 
        'col_model': '모델', 'col_serial': '시리얼 / UUID', 'col_version': '버전', 'col_ip': '관리 IP / System IP'
    },
    'zh': {
        'title': 'Cisco 多域资产管理仪表板',
        'subtitle': 'ACI, Meraki, Catalyst Center, SD-WAN 统一可视化',
        'btn_csv': '导出为 CSV',
        'btn_refresh': '刷新数据',
        'lbl_total': '设备总数',
        'lbl_controller_breakdown': '按控制器细分',
        'col_domain': '域', 'col_controller': '控制器 / 站点', 'col_name': '主机名 (点击查看详情)', 
        'col_model': '型号', 'col_serial': '序列号 / UUID', 'col_version': '版本', 'col_ip': '管理 IP / System IP'
    }
}

# --- HTML テンプレート (Bootstrap 5 + Icons) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ ui.title }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <style>
        body { background-color: #f4f7f6; padding: 20px; font-family: 'Segoe UI', 'Meiryo', sans-serif; }
        
        /* Header */
        .header-panel { background: linear-gradient(135deg, #005073 0%, #007cba 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        
        /* Dashboard Cards */
        .stat-card { border: none; border-radius: 10px; color: white; transition: transform 0.2s; overflow: hidden; position: relative; }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .stat-card .card-body { padding: 20px; z-index: 2; position: relative; }
        .stat-count { font-size: 2.5rem; font-weight: bold; line-height: 1; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }
        .stat-icon { position: absolute; right: 10px; bottom: 10px; font-size: 4rem; opacity: 0.2; z-index: 1; transform: rotate(-10deg); }

        .bg-total { background: linear-gradient(45deg, #343a40, #5a6268); }
        .bg-aci { background: linear-gradient(45deg, #017cad, #005073); }
        .bg-meraki { background: linear-gradient(45deg, #67b346, #4a8c2a); }
        .bg-catalyst { background: linear-gradient(45deg, #00bceb, #008cb3); }
        .bg-sdwan { background: linear-gradient(45deg, #702082, #501060); }
        
        /* Controller Cards (Color Coded) */
        .ctrl-card { background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: 0.2s; border-left: 5px solid #ccc; }
        .ctrl-card:hover { background-color: #f8f9fa; transform: translateY(-2px); }
        
        .ctrl-card-aci { border-left-color: #017cad; }
        .ctrl-card-meraki { border-left-color: #67b346; }
        .ctrl-card-catalyst { border-left-color: #00bceb; }
        .ctrl-card-sdwan { border-left-color: #702082; }

        /* Table Badges */
        .badge-aci { background-color: #017cad; }
        .badge-meraki { background-color: #67b346; }
        .badge-catalyst { background-color: #00bceb; }
        .badge-sdwan { background-color: #702082; }

        .controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .table { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .table thead { background-color: #343a40; color: white; }
        .device-link { color: #005073; text-decoration: none; font-weight: 600; }
        .device-link:hover { text-decoration: underline; color: #007cba; }
        
        .controller-name { font-weight: bold; color: #555; }
        
        .export-area { margin-top: 30px; text-align: center; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="controls">
            <a href="/refresh/{{ lang }}" class="btn btn-outline-primary btn-sm shadow-sm">
                <i class="bi bi-arrow-clockwise"></i> {{ ui.btn_refresh }}
            </a>
            
            <div class="btn-group shadow-sm">
                <a href="/en" class="btn btn-sm btn-outline-secondary {% if lang == 'en' %}active{% endif %}">English</a>
                <a href="/ja" class="btn btn-sm btn-outline-secondary {% if lang == 'ja' %}active{% endif %}">日本語</a>
                <a href="/ko" class="btn btn-sm btn-outline-secondary {% if lang == 'ko' %}active{% endif %}">한국어</a>
                <a href="/zh" class="btn btn-sm btn-outline-secondary {% if lang == 'zh' %}active{% endif %}">中文</a>
            </div>
        </div>
        
        <div class="header-panel text-center">
            <h1><i class="bi bi-hdd-network"></i> {{ ui.title }}</h1>
            <p class="mb-0">{{ ui.subtitle }}</p>
        </div>

        <div class="row mb-4 g-3">
            <div class="col-md">
                <div class="card stat-card bg-total h-100">
                    <div class="card-body">
                        <div class="stat-label">{{ ui.lbl_total }}</div>
                        <div class="stat-count">{{ stats.total }}</div>
                        <i class="bi bi-layers-half stat-icon"></i>
                    </div>
                </div>
            </div>
            <div class="col-md">
                <div class="card stat-card bg-aci h-100">
                    <div class="card-body">
                        <div class="stat-label">ACI</div>
                        <div class="stat-count">{{ stats.aci }}</div>
                        <i class="bi bi-building stat-icon"></i>
                    </div>
                </div>
            </div>
            <div class="col-md">
                <div class="card stat-card bg-meraki h-100">
                    <div class="card-body">
                        <div class="stat-label">Meraki</div>
                        <div class="stat-count">{{ stats.meraki }}</div>
                        <i class="bi bi-cloud-check stat-icon"></i>
                    </div>
                </div>
            </div>
            <div class="col-md">
                <div class="card stat-card bg-catalyst h-100">
                    <div class="card-body">
                        <div class="stat-label">Catalyst</div>
                        <div class="stat-count">{{ stats.catalyst }}</div>
                        <i class="bi bi-diagram-3 stat-icon"></i>
                    </div>
                </div>
            </div>
            <div class="col-md">
                <div class="card stat-card bg-sdwan h-100">
                    <div class="card-body">
                        <div class="stat-label">SD-WAN</div>
                        <div class="stat-count">{{ stats.sdwan }}</div>
                        <i class="bi bi-globe stat-icon"></i>
                    </div>
                </div>
            </div>
        </div>

        {% if stats.controllers %}
        <h6 class="text-secondary mb-2 ms-1"><i class="bi bi-diagram-2"></i> {{ ui.lbl_controller_breakdown }}</h6>
        <div class="row mb-4 g-3">
            {% for ctrl, info in stats.controllers.items() %}
            <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                <div class="card ctrl-card ctrl-card-{{ info.domain|lower }} h-100">
                    <div class="card-body py-2 px-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <small class="badge badge-{{ info.domain|lower }} opacity-75" style="font-size: 0.65rem;">{{ info.domain }}</small>
                        </div>
                        <div class="text-dark fw-bold text-truncate" title="{{ ctrl }}">{{ ctrl }}</div>
                        <div class="fs-4 fw-bold text-dark mt-1">{{ info.count }}</div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover mb-0 align-middle">
                        <thead class="table-dark">
                            <tr>
                                <th>{{ ui.col_domain }}</th>
                                <th>{{ ui.col_controller }}</th>
                                <th>{{ ui.col_name }}</th>
                                <th>{{ ui.col_model }}</th>
                                <th>{{ ui.col_serial }}</th>
                                <th>{{ ui.col_version }}</th>
                                <th>{{ ui.col_ip }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in data %}
                            {% if not row.error %}
                            <tr>
                                <td><span class="badge badge-{{ row.domain|lower }}">{{ row.domain }}</span></td>
                                <td class="controller-name">{{ row.controller }}</td>
                                <td><a href="{{ row.dashboard_url }}" target="_blank" class="device-link">{{ row.name }}</a></td>
                                <td>{{ row.model }}</td>
                                <td><code class="text-muted">{{ row.serial }}</code></td>
                                <td><small>{{ row.version }}</small></td>
                                <td>{{ row.ip }}</td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="export-area">
            <a href="/export" class="btn btn-success btn-lg shadow">
                <i class="bi bi-file-earmark-spreadsheet"></i> {{ ui.btn_csv }}
            </a>
        </div>
    </div>
</body>
</html>
"""

def get_data_with_cache(force=False):
    global DATA_CACHE, LAST_UPDATE
    now = time.time()
    if DATA_CACHE is not None and not force and (now - LAST_UPDATE < CACHE_DURATION):
        return DATA_CACHE
    
    print("📡 Fetching fresh data via Core Logic...")
    data = get_all_inventory()
    DATA_CACHE = data
    LAST_UPDATE = now
    return data

def calculate_stats(data):
    """データからドメインごとの台数と、コントローラごとの台数・ドメイン情報を集計する"""
    stats = {
        'total': 0, 
        'aci': 0, 'meraki': 0, 'catalyst': 0, 'sdwan': 0,
        'controllers': {} # { 'CtrlName': {'count': 5, 'domain': 'ACI'}, ... }
    }
    
    for row in data:
        if "error" in row: continue
        
        # Total Count
        stats['total'] += 1
        
        # Domain Count
        domain = row.get('domain', '').strip()
        d_lower = domain.lower()
        if 'aci' in d_lower: stats['aci'] += 1
        elif 'meraki' in d_lower: stats['meraki'] += 1
        elif 'catalyst' in d_lower: stats['catalyst'] += 1
        elif 'sdwan' in d_lower: stats['sdwan'] += 1
        
        # Controller Count & Metadata
        ctrl = row.get('controller', 'Unknown')
        
        if ctrl not in stats['controllers']:
            stats['controllers'][ctrl] = {'count': 0, 'domain': domain}
            
        stats['controllers'][ctrl]['count'] += 1
        
    return stats

# --- ルーティング ---

@app.route('/')
def index_root():
    return redirect(url_for('index_lang', lang='ja'))

@app.route('/<lang>')
def index_lang(lang):
    target_lang = lang if lang in UI_TEXT else 'en'
    data = get_data_with_cache(force=False)
    stats = calculate_stats(data)
    
    # テンプレートに渡すデータに stats を追加
    render_params = {
        'lang': target_lang,
        'ui': UI_TEXT[target_lang],
        'data': data,
        'stats': stats
    }
    
    return render_template_string(HTML_TEMPLATE, **render_params)

@app.route('/refresh/<lang>')
def refresh_data(lang):
    get_data_with_cache(force=True)
    return redirect(url_for('index_lang', lang=lang))

@app.route('/export')
def export():
    data = get_data_with_cache(force=False)
    si = io.StringIO()
    cw = csv.writer(si)
    # CSVヘッダー
    cw.writerow(['Domain', 'Controller/Site', 'Name', 'Model', 'Serial/UUID', 'Version', 'IP Address', 'Dashboard URL'])
    
    for row in data:
        if "error" in row: continue
        cw.writerow([
            row.get('domain'), 
            row.get('controller', '-'),
            row.get('name'), 
            row.get('model'), 
            row.get('serial'), 
            row.get('version'), 
            row.get('ip'), 
            row.get('dashboard_url')
        ])
    
    res = make_response(si.getvalue())
    res.headers["Content-Disposition"] = "attachment; filename=cisco_inventory.csv"
    res.headers["Content-type"] = "text/csv"
    return res

if __name__ == '__main__':
    print("🚀 Full-Stack Inventory Server starting at http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)