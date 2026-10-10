# -*- coding: utf-8 -*-
"""
Logic tính "Ngày lấy hàng vs Ngày giao hàng" cho khu vực Miền Tây.

File này được dùng ở 2 nơi:
  - index.html tải file này và chạy bằng Pyodide (Python trong trình duyệt),
    truyền vào các dòng đã qua bộ lọc Dự án/Năm/Tháng/Tuần của dashboard.
  - scripts/mientay_giaohang.py import để chạy/đối chiếu trên máy.
Chỉ dùng thư viện chuẩn để chạy được trên Pyodide mà không cần cài thêm gói.
"""
import json
import re
from collections import Counter
from datetime import date, datetime

KHU_VUC = 'Miền Tây'
COL_NGAY_LAY = 'Ngày'              # vd: "6 January 2026"
COL_NGAY_GIAO = 'Ngày giao hàng'   # vd: "06-01-26" (dd-mm-yy)

MONTHS = {m: i for i, m in enumerate(
    ['january', 'february', 'march', 'april', 'may', 'june', 'july',
     'august', 'september', 'october', 'november', 'december'], start=1)}


def parse_ngay_lay(s):
    """'6 January 2026' -> date. Không phụ thuộc locale của máy."""
    m = re.fullmatch(r'\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*', s or '')
    if not m or m.group(2).lower() not in MONTHS:
        return None
    return date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))


def parse_ngay_giao(s):
    """'06-01-26' (dd-mm-yy) -> date."""
    try:
        return datetime.strptime((s or '').strip(), '%d-%m-%y').date()
    except ValueError:
        return None


def tinh_mien_tay(rows):
    """rows: list dict (key = tên cột Sheet). Trả về dict kết quả."""
    mt = [r for r in rows if (r.get('Khu vực') or '').strip() == KHU_VUC]

    invalid = []
    diffs = []
    for r in mt:
        d_lay = parse_ngay_lay(r.get(COL_NGAY_LAY))
        d_giao = parse_ngay_giao(r.get(COL_NGAY_GIAO))
        if d_lay is None or d_giao is None:
            invalid.append({'stt': r.get('Stt'), 'ma_don': r.get('Mã đơn'),
                            'ngay_lay': r.get(COL_NGAY_LAY), 'ngay_giao': r.get(COL_NGAY_GIAO)})
            continue
        diffs.append((d_giao - d_lay).days)

    total = len(diffs)
    same = sum(1 for d in diffs if d == 0)
    diff = total - same
    by_delay = Counter(d for d in diffs if d != 0)

    return {
        'khu_vuc': KHU_VUC,
        'tong_don': total,
        'cung_ngay': same,
        'khac_ngay': diff,
        'ty_le_cung_ngay': round(same / total * 100, 2) if total else 0,
        'ty_le_khac_ngay': round(diff / total * 100, 2) if total else 0,
        # Chi tiết nhóm khác ngày: số ngày (giao - lấy) -> số đơn và % trên tổng đơn
        'chi_tiet_khac_ngay': [
            {'so_ngay': k, 'so_don': n,
             'ty_le': round(n / total * 100, 2),
             'ty_le_trong_khac_ngay': round(n / diff * 100, 2)}
            for k, n in sorted(by_delay.items())
        ],
        'so_dong_loi_ngay': len(invalid),
        'dong_loi_ngay': invalid,
    }


def tinh_mien_tay_json(rows_json):
    """Cầu nối cho Pyodide: nhận/trả chuỗi JSON."""
    return json.dumps(tinh_mien_tay(json.loads(rows_json)), ensure_ascii=False)
