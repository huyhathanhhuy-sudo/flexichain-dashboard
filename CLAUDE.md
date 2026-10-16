# Flexichain Dashboard

Trang tĩnh (`index.html` + Chart.js) đọc Google Sheet đơn hàng (SHEET_ID/API_KEY trong `config.js`) và tính KPI bằng
JavaScript. Tab: Executive, Khách hàng, Khu vực, LTL vs FTL, Hiệu suất, Nhà xe, Miền Trung, Miền Tây (Python qua
Pyodide: `scripts/mientay_calc.py`). Chạy local: `python -m http.server 8765`.

## Dùng cho phân tích / báo cáo bằng AI

Không cần mở trình duyệt: **Flexichain Agent** (`../Flexichain Agent`) đã tích hợp Dashboard.

```bash
cd "../Flexichain Agent"
.venv/Scripts/python.exe main.py dashboard report --du-an Rebisco --thang 8,9
```

→ `data/reports/...` gồm `summary.md`, `metrics.json` (số liệu 8 tab) và `charts/*.png` (ảnh chụp biểu đồ của trang này).
Quy trình phân tích: `../Flexichain Agent/.claude/skills/bao-cao-hieu-qua/SKILL.md`.

## Khi sửa trang này

- Đổi công thức KPI trong `index.html` → sửa tương ứng `../Flexichain Agent/agent/analytics/metrics.py`.
- Đổi id tab (`showPage('...')`), class `.chart-card` / `.chart-title`, hàm `applyFilters`/`selectProject`/`selections`
  → kiểm tra `../Flexichain Agent/agent/analytics/charts.py` (chụp ảnh dựa vào các tên này).
- `scripts/mientay_calc.py` được agent import trực tiếp – giữ hàm `tinh_mien_tay(rows)`.
