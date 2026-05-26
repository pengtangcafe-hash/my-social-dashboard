"""
goal_tracker.py — ติดตามความก้าวหน้า KPI รายเดือน เทียบกับเป้าหมาย

อ่านเป้าหมายจาก data/goals.json
อ่าน actual จาก data/history/ (latest snapshot ต่อ platform)
คำนวณ % progress แล้ว inject GOAL_DATA เข้า dashboard HTML

Usage (CLI):
  python src/goal_tracker.py show
  python src/goal_tracker.py inject dashboard/index.html
  python src/goal_tracker.py set tiktok total_reach 200000
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GOALS_PATH   = PROJECT_ROOT / "data" / "goals.json"
HISTORY_DIR  = PROJECT_ROOT / "data" / "history"

PLATFORMS    = ["tiktok", "facebook", "instagram"]

KPI_LABELS = {
    "total_reach":         "Reach รวม",
    "avg_engagement_rate": "Engagement Rate",
    "total_new_followers": "Followers ใหม่",
}

KPI_FORMAT = {
    "total_reach":         "number",
    "avg_engagement_rate": "percent",
    "total_new_followers": "number",
}

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

# ──────────────────────────────────────────────
# Load / Save goals
# ──────────────────────────────────────────────

def load_goals() -> dict:
    if GOALS_PATH.exists():
        return json.loads(GOALS_PATH.read_text(encoding="utf-8"))
    return {"monthly_targets": {p: {} for p in PLATFORMS}}


def save_goals(goals: dict) -> None:
    goals["updated_at"] = date.today().isoformat()
    GOALS_PATH.write_text(json.dumps(goals, ensure_ascii=False, indent=2), encoding="utf-8")


def set_goal(platform: str, kpi: str, value: float) -> None:
    goals = load_goals()
    targets = goals.setdefault("monthly_targets", {})
    targets.setdefault(platform, {})[kpi] = value
    save_goals(goals)
    print(f"✅ ตั้งเป้า [{PLATFORM_LABELS.get(platform, platform)}] {KPI_LABELS.get(kpi, kpi)}: {value:,}")


# ──────────────────────────────────────────────
# Load actual data from history
# ──────────────────────────────────────────────

def _latest_monthly_file(platform: str) -> Path | None:
    """หา history file รายเดือนล่าสุดของ platform"""
    files = sorted(HISTORY_DIR.glob(f"{platform}-????-??.json"))
    return files[-1] if files else None


def load_actuals() -> dict:
    """
    โหลด summary ล่าสุดของแต่ละ platform
    คืน dict: { platform: { kpi: value, ... }, ... }
    """
    actuals = {}
    for platform in PLATFORMS:
        f = _latest_monthly_file(platform)
        if not f:
            actuals[platform] = {}
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            snaps = data.get("snapshots", [])
            if not snaps:
                actuals[platform] = {}
                continue
            # ดึง summary จาก snapshot ล่าสุด
            summary = snaps[-1].get("summary", {})
            actuals[platform] = {k: v for k, v in summary.items() if v is not None}
        except Exception:
            actuals[platform] = {}
    return actuals


# ──────────────────────────────────────────────
# Compute progress
# ──────────────────────────────────────────────

def compute_progress() -> dict:
    """
    เปรียบเทียบ actual vs target ทุก KPI
    คืน dict ที่ inject เป็น GOAL_DATA JS constant ได้เลย
    """
    goals   = load_goals()
    actuals = load_actuals()
    targets = goals.get("monthly_targets", {})

    today     = date.today()
    month_key = today.strftime("%Y-%m")

    result = {
        "month":    month_key,
        "updated":  goals.get("updated_at", today.isoformat()),
        "platforms": {},
    }

    for platform in PLATFORMS:
        p_targets = targets.get(platform, {})
        p_actuals = actuals.get(platform, {})
        kpis      = {}

        for kpi in KPI_LABELS:
            target = p_targets.get(kpi)
            actual = p_actuals.get(kpi)

            if target is None:
                continue   # ไม่ได้ตั้งเป้าข้อนี้ ข้ามไป

            pct = None
            if target and target > 0 and actual is not None:
                pct = min(round(actual / target * 100, 1), 200)  # cap 200%

            kpis[kpi] = {
                "label":  KPI_LABELS[kpi],
                "format": KPI_FORMAT[kpi],
                "target": target,
                "actual": actual,
                "pct":    pct,
            }

        result["platforms"][platform] = {
            "label": PLATFORM_LABELS[platform],
            "color": PLATFORM_COLORS[platform],
            "kpis":  kpis,
        }

    return result


# ──────────────────────────────────────────────
# Build JS constant
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    data = compute_progress()
    return f"const GOAL_DATA = {json.dumps(data, ensure_ascii=False)};"


# ──────────────────────────────────────────────
# Inject into dashboard
# ──────────────────────────────────────────────

def inject_into_dashboard(html_path: str | Path) -> bool:
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html     = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()
    marker   = "// ── Goal Tracker Data ──"

    # ถ้ามี GOAL_DATA อยู่แล้ว ให้แทนที่
    pattern = r"const GOAL_DATA\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต GOAL_DATA ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{marker}\n{js_const}", 1)
        print(f"✅ เพิ่ม GOAL_DATA ใน {html_path.name}")
    else:
        # fallback: แทรกก่อน // ── Competitor Tracker Data ──
        fallback = "// ── Competitor Tracker Data ──"
        if fallback in html:
            html = html.replace(fallback, f"{marker}\n{js_const}\n\n{fallback}", 1)
        else:
            html = html.replace("<script>", f"<script>\n{marker}\n{js_const}\n", 1)
        print(f"✅ เพิ่ม GOAL_DATA (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# CLI report
# ──────────────────────────────────────────────

def show_progress() -> None:
    data = compute_progress()
    print(f"\n🎯 Goal Tracker — {data['month']}")
    print("─" * 55)
    for platform, info in data["platforms"].items():
        print(f"\n  [{info['label']}]")
        kpis = info.get("kpis", {})
        if not kpis:
            print("    ไม่มีเป้าหมาย")
            continue
        for kpi, v in kpis.items():
            actual = v["actual"]
            target = v["target"]
            pct    = v["pct"]
            fmt    = v["format"]
            label  = v["label"]

            if fmt == "percent":
                a_str = f"{actual:.2f}%" if actual is not None else "—"
                t_str = f"{target:.2f}%"
            else:
                a_str = f"{int(actual):,}" if actual is not None else "—"
                t_str = f"{int(target):,}"

            bar_width = 20
            filled    = round(min(pct or 0, 100) / 100 * bar_width)
            bar       = "█" * filled + "░" * (bar_width - filled)

            status = "✅" if (pct or 0) >= 100 else ("⚠️" if (pct or 0) >= 60 else "🔴")
            pct_str = f"{pct:.1f}%" if pct is not None else "—"
            print(f"    {status} {label:<18} {a_str:>10} / {t_str:>10}  [{bar}] {pct_str}")
    print()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_progress()

    elif args[0] == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1])

    elif args[0] == "set" and len(args) >= 4:
        platform = args[1].lower()
        kpi      = args[2]
        try:
            value = float(args[3])
        except ValueError:
            print("ค่าต้องเป็นตัวเลข")
            sys.exit(1)
        set_goal(platform, kpi, value)

    else:
        print("Usage:")
        print("  python src/goal_tracker.py show")
        print("  python src/goal_tracker.py inject dashboard/index.html")
        print("  python src/goal_tracker.py set tiktok total_reach 200000")
        print("  python src/goal_tracker.py set facebook avg_engagement_rate 1.5")
