"""
monthly_trend.py — สร้างข้อมูลแนวโน้ม Reach + Engagement รายสัปดาห์/รายเดือน

Logic:
  - ถ้ามีข้อมูลแค่ 1 เดือน  → mode "weekly"  (แสดง 4 สัปดาห์ใน 28 วัน)
  - ถ้ามีข้อมูล 2+ เดือน    → mode "monthly" (แสดง month-over-month)

อ่านข้อมูลจาก data/history/{platform}-{YYYY-MM}.json
inject MONTHLY_TREND เข้า dashboard HTML

Usage (CLI):
  python src/monthly_trend.py show
  python src/monthly_trend.py inject dashboard/index.html
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
HISTORY_DIR  = PROJECT_ROOT / "data" / "history"
PLATFORMS    = ["tiktok", "facebook", "instagram"]

PLATFORM_COLORS = {
    "tiktok":    "#010101",
    "facebook":  "#1877f2",
    "instagram": "#e1306c",
}
PLATFORM_LABELS = {
    "tiktok":    "TikTok",
    "facebook":  "Facebook",
    "instagram": "Instagram",
}

THAI_MONTHS = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
               "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


# ──────────────────────────────────────────────
# Load history data
# ──────────────────────────────────────────────

def _parse_date(raw: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(raw).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _load_monthly_files() -> dict:
    """
    โหลดไฟล์ {platform}-{YYYY-MM}.json ทั้งหมด
    คืน: { (platform, "YYYY-MM"): [ {date, reach, engagement, ...}, ... ] }
    """
    result = {}
    for platform in PLATFORMS:
        files = sorted(HISTORY_DIR.glob(f"{platform}-????-??.json"))
        for f in files:
            try:
                data   = json.loads(f.read_text(encoding="utf-8"))
                snaps  = data.get("snapshots", [])
                if not snaps:
                    continue
                # ใช้ snapshot ล่าสุด
                snap      = snaps[-1]
                daily_raw = snap.get("daily_data", [])
                rows      = []
                for row in daily_raw:
                    d = _parse_date(row.get("date", ""))
                    if not d:
                        continue
                    reach   = float(row.get("reach", 0) or 0)
                    engage  = float(
                        row.get("likes", 0) or row.get("engagement", 0) or 0
                    )
                    followers = float(row.get("new_followers", 0) or 0)
                    rows.append({
                        "date":        d,
                        "reach":       reach,
                        "engagement":  engage,
                        "followers":   followers,
                    })
                if rows:
                    # period key จากชื่อไฟล์ เช่น "2026-05"
                    stem   = f.stem          # "tiktok-2026-05"
                    period = stem[len(platform) + 1:]  # "2026-05"
                    result[(platform, period)] = rows
            except Exception:
                continue
    return result


# ──────────────────────────────────────────────
# Build weekly breakdown (1 month)
# ──────────────────────────────────────────────

def _week_label(d: date, week_num: int) -> str:
    """สร้าง label เช่น 'สัป.1 (19-25 เม.ย.)'"""
    return f"สัป.{week_num}"


def _week_long_label(days: list[date]) -> str:
    if not days:
        return ""
    first, last = days[0], days[-1]
    m1 = THAI_MONTHS[first.month]
    m2 = THAI_MONTHS[last.month]
    if first.month == last.month:
        return f"{first.day}-{last.day} {m1}"
    return f"{first.day} {m1} – {last.day} {m2}"


def _build_weekly(all_rows: dict, period: str) -> dict:
    """
    แบ่ง 28 วันเป็น 4 สัปดาห์ (Monday-based)
    คืน dict สำหรับ MONTHLY_TREND
    """
    # ดึง date range จากทุก platform รวมกัน
    all_dates = []
    for platform in PLATFORMS:
        rows = all_rows.get((platform, period), [])
        all_dates.extend(r["date"] for r in rows)

    if not all_dates:
        return {}

    min_date = min(all_dates)
    max_date = max(all_dates)

    # แบ่งเป็น chunks 7 วัน
    chunks: list[tuple[date, date]] = []
    cur = min_date
    while cur <= max_date:
        end = min(cur + timedelta(days=6), max_date)
        chunks.append((cur, end))
        cur = end + timedelta(days=1)

    # ไม่เกิน 6 chunks (เผื่อ 6 สัปดาห์)
    chunks = chunks[:6]

    labels_short = []
    labels_long  = []
    for i, (s, e) in enumerate(chunks, 1):
        days = [s + timedelta(days=k) for k in range((e - s).days + 1)]
        labels_short.append(_week_label(s, i))
        labels_long.append(_week_long_label(days))

    series = {}
    for platform in PLATFORMS:
        rows = all_rows.get((platform, period), [])
        reach_vals  = []
        engage_vals = []
        for s, e in chunks:
            chunk_rows = [r for r in rows if s <= r["date"] <= e]
            r_sum = sum(r["reach"] for r in chunk_rows)
            # engagement rate: sum(engage)/sum(reach)*100 ถ้ามี reach
            r_reach = sum(r["reach"] for r in chunk_rows)
            r_eng   = sum(r["engagement"] for r in chunk_rows)
            eng_rate = round(r_eng / r_reach * 100, 2) if r_reach > 0 else 0
            reach_vals.append(round(r_sum, 0))
            engage_vals.append(eng_rate)

        series[platform] = {
            "label":           PLATFORM_LABELS[platform],
            "color":           PLATFORM_COLORS[platform],
            "reach":           reach_vals,
            "engagement_rate": engage_vals,
        }

    # สรุป month label
    y, m = period.split("-")
    month_label = f"{THAI_MONTHS[int(m)]} {int(y) + 543}"

    return {
        "mode":         "weekly",
        "period":       period,
        "month_label":  month_label,
        "labels_short": labels_short,
        "labels_long":  labels_long,
        "series":       series,
        "generated_at": date.today().isoformat(),
    }


# ──────────────────────────────────────────────
# Build monthly summary (2+ months)
# ──────────────────────────────────────────────

def _build_monthly(all_rows: dict, periods: list[str]) -> dict:
    """
    รวม reach ต่อเดือน แล้วเรียงตามเวลา
    """
    labels_short = []
    labels_long  = []
    for p in periods:
        y, m = p.split("-")
        labels_short.append(f"{THAI_MONTHS[int(m)]}")
        labels_long.append(f"{THAI_MONTHS[int(m)]} {int(y) + 543}")

    series = {}
    for platform in PLATFORMS:
        reach_vals  = []
        engage_vals = []
        for period in periods:
            rows = all_rows.get((platform, period), [])
            r_sum   = sum(r["reach"] for r in rows)
            r_reach = sum(r["reach"] for r in rows)
            r_eng   = sum(r["engagement"] for r in rows)
            eng_rate = round(r_eng / r_reach * 100, 2) if r_reach > 0 else 0
            reach_vals.append(round(r_sum, 0))
            engage_vals.append(eng_rate)

        series[platform] = {
            "label":           PLATFORM_LABELS[platform],
            "color":           PLATFORM_COLORS[platform],
            "reach":           reach_vals,
            "engagement_rate": engage_vals,
        }

    return {
        "mode":         "monthly",
        "periods":      periods,
        "labels_short": labels_short,
        "labels_long":  labels_long,
        "series":       series,
        "generated_at": date.today().isoformat(),
    }


# ──────────────────────────────────────────────
# Main compute
# ──────────────────────────────────────────────

def compute_trend() -> dict:
    all_rows = _load_monthly_files()

    # เก็บ periods ที่มีข้อมูลของอย่างน้อย 1 platform
    periods_set = set()
    for (platform, period) in all_rows:
        periods_set.add(period)
    periods = sorted(periods_set)

    if not periods:
        return {
            "mode": "empty",
            "message": "ยังไม่มีข้อมูล history — ใช้ /analyze เพื่อนำเข้าข้อมูล",
        }

    if len(periods) == 1:
        return _build_weekly(all_rows, periods[0])
    else:
        return _build_monthly(all_rows, periods)


# ──────────────────────────────────────────────
# Build JS + inject
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    data = compute_trend()
    return f"const MONTHLY_TREND = {json.dumps(data, ensure_ascii=False)};"


def inject_into_dashboard(html_path: str | Path) -> bool:
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html     = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()
    marker   = "// ── Monthly Trend Data ──"

    pattern = r"const MONTHLY_TREND\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต MONTHLY_TREND ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{marker}\n{js_const}", 1)
        print(f"✅ เพิ่ม MONTHLY_TREND ใน {html_path.name}")
    else:
        fallback = "// ── Goal Tracker Data ──"
        if fallback in html:
            html = html.replace(fallback, f"{marker}\n{js_const}\n\n{fallback}", 1)
        else:
            html = html.replace("<script>", f"<script>\n{marker}\n{js_const}\n", 1)
        print(f"✅ เพิ่ม MONTHLY_TREND (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def show_trend() -> None:
    data = compute_trend()
    mode = data.get("mode", "empty")

    if mode == "empty":
        print(f"\n⚠️  {data.get('message')}\n")
        return

    print(f"\n📈 Monthly Trend — mode: {mode}")
    print("─" * 55)

    if mode == "weekly":
        print(f"เดือน: {data.get('month_label')}  |  {len(data['labels_short'])} สัปดาห์")
    else:
        print(f"เดือน: {', '.join(data['labels_long'])}")

    for platform, s in data["series"].items():
        reach_str = "  ".join(f"{int(v):>8,}" for v in s["reach"])
        print(f"\n  [{s['label']}] Reach: {reach_str}")
        eng_str   = "  ".join(f"{v:>7.2f}%" for v in s["engagement_rate"])
        print(f"   Eng.Rate:            {eng_str}")

    print(f"\n  labels: {data['labels_short']}")
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_trend()
    elif args[0] == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1])
    else:
        print("Usage:")
        print("  python src/monthly_trend.py show")
        print("  python src/monthly_trend.py inject dashboard/index.html")
