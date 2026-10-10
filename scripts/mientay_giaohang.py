# -*- coding: utf-8 -*-
"""
Chạy trên máy để xem/đối chiếu số liệu Miền Tây (ngày lấy vs ngày giao) trên toàn bộ dữ liệu.
Dashboard KHÔNG cần file này — index.html tự chạy scripts/mientay_calc.py bằng Pyodide.

    python scripts/mientay_giaohang.py
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mientay_calc import tinh_mien_tay  # noqa: E402

CONFIG_JS = Path(__file__).resolve().parent.parent / 'config.js'


def read_config():
    text = CONFIG_JS.read_text(encoding='utf-8')
    cfg = {}
    for key in ('SHEET_ID', 'API_KEY', 'SHEET_NAME'):
        m = re.search(key + r"\s*:\s*['\"]([^'\"]+)['\"]", text)
        if m:
            cfg[key] = m.group(1)
    cfg.setdefault('SHEET_NAME', 'data')
    return cfg


def fetch_rows(cfg):
    url = ('https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key={}'
           .format(cfg['SHEET_ID'], urllib.parse.quote(cfg['SHEET_NAME']), cfg['API_KEY']))
    with urllib.request.urlopen(url) as res:
        data = json.load(res)
    header, *body = data['values']
    header = [h.strip() for h in header]
    return [{h: (r[i] if i < len(r) else '') for i, h in enumerate(header)} for r in body if r]


def parse_num(v):
    s = re.sub(r'[^0-9.-]', '', str(v or ''))
    try:
        return float(s)
    except ValueError:
        return 0.0


def main():
    rows = fetch_rows(read_config())
    # Cùng điều kiện lọc với dashboard: bỏ dòng doanh thu = 0 và chi phí = 0
    rows = [r for r in rows if parse_num(r.get('Doanh thu')) > 0 or parse_num(r.get('Chi phí')) > 0]
    result = tinh_mien_tay(rows)
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
