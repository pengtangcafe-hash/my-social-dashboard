"""
posting_time_analyzer.py — วิเคราะห์วันที่ดีที่สุดในการโพสต์

วิเคราะห์จาก history data รายวัน แล้วบอกว่าวันไหนของสัปดาห์
ที่ engagement และ reach สูงสุดในแต่ละ platform

Usage (CLI):
  python src/posting_time_analyzer.py
  python src/posting_time_analyzer.py inject dashboard/index.html
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from history_store import load_history, list_available_history

PROJECT_ROOT = Path(__file__).parent.parent

DAYS_TH = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_EMOJIS = ["💼", "📱", "🦷", "✨", "🎉", "🌟", "☀️"]

# metric weights per platform (reach = reach or views, engage = engagement metric)
PLATFORM_METRICS = {
    "tiktok":    {"reach": "reach",      "engage": "likes"},
    "facebook":  {"reach": "reach",      "engage": "engagement"},
    "instagram": {"reach": "reach",      "engage": "engagement"},
}


def analyze_best_days(platform: str) -> dict:
    """
    วิเคราะห์ best day of week สำหรับ platform ที่ระบุ
    คืน dict พร้อม day-by-day averages และ best day
    """
    snapshots = load_history(platform, months=6)
    if not snapshots:
        return {"platform": platform, "available": False, "reason": "ไม่มีข้อมูล history"}

    # รวม rows จาก snapshot ทั้งหมด
    day_reach    = defaultdict(list)
    day_engage   = defaultdict(list)
    total_rows   = 0

    for snap in snapshots:
        table = snap.get("daily_data") or snap.get("table", [])
        for row in table:
            raw_date = row.get("date", "")
            if not raw_date:
                continue
            try:
                # รองรับ format หลายแบบ
                for fmt in ("%Y-%m-%d", "%d %b %Y", "%Y/%m/%d"):
                    try:
                        d = datetime.strptime(str(raw_date), fmt)
                        break
                    except ValueError:
                        continue
                else:
                    continue

                weekday = d.weekday()  # 0=Mon … 6=Sun
                reach   = row.get("reach", 0) or 0
                engage  = (row.get("likes", 0) or row.get("engagement", 0) or 0)

                if reach > 0:
                    day_reach[weekday].append(float(reach))
                if engage > 0:
                    day_engage[weekday].append(float(engage))
                total_rows += 1

            except Exception:
                continue

    if total_rows == 0:
        return {"platform": platform, "available": False, "reason": "ไม่มีข้อมูลรายวัน"}

    # คำนวณ average และ score ต่อวัน
    days_data = []
    for wd in range(7):
        reaches  = day_reach.get(wd, [])
        engages  = day_engage.get(wd, [])
        avg_r    = sum(reaches)  / len(reaches)  if reaches  else 0
        avg_e    = sum(engages)  / len(engages)  if engages  else 0
        days_data.append({
            "weekday":     wd,
            "day_th":      DAYS_TH[wd],
            "day_en":      DAYS_EN[wd],
            "emoji":       DAY_EMOJIS[wd],
            "avg_reach":   round(avg_r, 1),
            "avg_engage":  round(avg_e, 1),
            "samples":     len(reaches),
        })

    # Normalize เพื่อคำนวณ score 0-100
    max_r = max((d["avg_reach"]  for d in days_data), default=1) or 1
    max_e = max((d["avg_engage"] for d in days_data), default=1) or 1

    for d in days_data:
        score = (d["avg_reach"] / max_r * 60) + (d["avg_engage"] / max_e * 40)
        d["score"] = round(score, 1)

    # Best day = score สูงสุด (ที่มีข้อมูล)
    valid = [d for d in days_data if d["samples"] > 0]
    if not valid:
        return {"platform": platform, "available": False, "reason": "ข้อมูลไม่พอ"}

    best = max(valid, key=lambda d: d["score"])
    worst = min(valid, key=lambda d: d["score"])

    # top 3
    sorted_days = sorted(valid, key=lambda d: d["score"], reverse=True)

    return {
        "platform":    platform,
        "available":   True,
        "total_rows":  total_rows,
        "days":        days_data,
        "best_day":    best,
        "worst_day":   worst,
        "top3_days":   sorted_days[:3],
        "bottom2_days": sorted_days[-2:],
    }


def analyze_all_platforms() -> dict:
    """วิเคราะห์ทุก platform ที่มีข้อมูล"""
    available = list_available_history()
    results = {}
    for platform in available:
        results[platform] = analyze_best_days(platform)
    return results


def build_js_constant(results: dict) -> str:
    """สร้าง JS constant BEST_DAYS สำหรับ inject เข้า dashboard"""
    return f"const BEST_DAYS = {json.dumps(results, ensure_ascii=False)};"


def inject_into_dashboard(html_path: str | Path, results: dict | None = None) -> bool:
    """แทรก BEST_DAYS constant เข้า dashboard HTML"""
    import re
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    if results is None:
        results = analyze_all_platforms()

    html      = html_path.read_text(encoding="utf-8")
    js_const  = build_js_constant(results)
    pattern   = r"const BEST_DAYS\s*=\s*\{[^;]*\};"
    marker    = "// ── Chart instances cache ──"

    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต BEST_DAYS ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{js_const}\n\n{marker}")
        print(f"✅ เพิ่ม BEST_DAYS ใน {html_path.name}")
    else:
        html = html.replace("<script>", f"<script>\n{js_const}\n", 1)
        print(f"✅ เพิ่ม BEST_DAYS (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


def print_report(results: dict) -> None:
    """แสดง report ใน terminal"""
    print("\n📅 Best Day to Post — Social Analytics")
    print("─" * 50)
    for platform, data in results.items():
        print(f"\n  [{platform.upper()}]")
        if not data.get("available"):
            print(f"    ⚠️  {data.get('reason', 'ไม่มีข้อมูล')}")
            continue
        best  = data["best_day"]
        top3  = data["top3_days"]
        print(f"    🏆 วันที่ดีที่สุด : {best['emoji']} {best['day_th']}")
        print(f"       avg reach    : {best['avg_reach']:,.0f}")
        print(f"       avg engage   : {best['avg_engage']:,.0f}")
        print(f"    📊 Top 3 วัน   : {' · '.join(d['day_th'] for d in top3)}")
        print(f"    📁 ข้อมูล       : {data['total_rows']} rows")
    print()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    results = analyze_all_platforms()

    if args and args[0] == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1], results)
    else:
        print_report(results)
        if args and args[0] == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
