"""
competitor_tracker.py — บันทึกและเปรียบเทียบ snapshot ของคู่แข่ง

Storage layout:
  data/competitors/{competitor_name}/{YYYY-WXX}.json   ← weekly snapshot
  data/competitors/{competitor_name}/{YYYY-MM}.json    ← monthly snapshot (auto-aggregate)

Usage (CLI):
  python src/competitor_tracker.py save    <competitor> <json_file>
  python src/competitor_tracker.py compare <competitor> week
  python src/competitor_tracker.py compare <competitor> month
  python src/competitor_tracker.py compare <competitor> year
  python src/competitor_tracker.py report  [competitor]
  python src/competitor_tracker.py list
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

COMP_DIR = Path(__file__).parent.parent / "data" / "competitors"
REPORT_DIR = Path(__file__).parent.parent / "reports"

KNOWN_COMPETITORS = {
    "หมอจั่นเจา":  {"facebook": "JunjaoDentalClinic",  "tiktok": "@dr.piyawat5",   "website": "junjaodentalclinic.com"},
    "DioDental":   {"facebook": "DioDentalClinicEsan",  "tiktok": "@diodental",      "website": ""},
    "Toothmate":   {"facebook": "ToothmateDC",          "instagram": "@toothmate_dc", "website": ""},
    "DentalPark":  {"facebook": "Dentalpark2020",       "tiktok": "@dental.park.clinic", "website": ""},
}

# ──────────────────────────────────────────────
# Schema helpers
# ──────────────────────────────────────────────

def _week_label(d: date) -> str:
    """date → 'YYYY-WXX' (ISO week)"""
    return f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"

def _month_label(d: date) -> str:
    return d.strftime("%Y-%m")

def _prev_week_label(label: str) -> str:
    year, w = label.split("-W")
    d = date.fromisocalendar(int(year), int(w), 1) - timedelta(weeks=1)
    return _week_label(d)

def _prev_month_label(label: str) -> str:
    year, m = int(label[:4]), int(label[5:7])
    if m == 1:
        return f"{year-1}-12"
    return f"{year}-{m-1:02d}"

def _prev_year_label(label: str) -> str:
    return f"{int(label[:4])-1}{label[4:]}"

def _snapshot_path(competitor: str, period_label: str) -> Path:
    return COMP_DIR / competitor / f"{period_label}.json"

def empty_snapshot(competitor: str, period_label: str) -> dict:
    return {
        "competitor": competitor,
        "period": period_label,
        "snapshot_date": date.today().isoformat(),
        "platforms": {
            "facebook":  {"followers_est": None, "posts": [], "posts_count": 0},
            "tiktok":    {"followers_est": None, "videos": [], "videos_count": 0},
            "instagram": {"followers_est": None, "posts": [], "posts_count": 0},
            "website":   {"active_promotions": []},
        },
        "promotions":            [],
        "content_themes":        [],
        "top_content":           [],
        "activity_level":        "unknown",
        "primary_platform":      "",
        "posting_frequency":     "",
        "estimated_reach":       None,
        "notes":                 "",
    }

# ──────────────────────────────────────────────
# Save / Load
# ──────────────────────────────────────────────

def save_snapshot(competitor: str, snapshot: dict, period_label: str | None = None) -> Path:
    label = period_label or snapshot.get("period") or _week_label(date.today())
    path = _snapshot_path(competitor, label)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def load_snapshot(competitor: str, period_label: str) -> dict | None:
    path = _snapshot_path(competitor, period_label)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def list_snapshots(competitor: str) -> list[str]:
    """คืน list ของ period labels ที่มีข้อมูล เรียงจากเก่าไปใหม่"""
    comp_dir = COMP_DIR / competitor
    if not comp_dir.exists():
        return []
    return sorted(p.stem for p in comp_dir.glob("*.json"))

def list_all_competitors() -> list[str]:
    if not COMP_DIR.exists():
        return []
    return [p.name for p in COMP_DIR.iterdir() if p.is_dir()]

# ──────────────────────────────────────────────
# Compare engine
# ──────────────────────────────────────────────

def _safe_int(v) -> int | None:
    try:
        return int(v) if v is not None else None
    except (ValueError, TypeError):
        return None

def _pct(old, new) -> float | None:
    o, n = _safe_int(old), _safe_int(new)
    if o is None or n is None or o == 0:
        return None
    return (n - o) / o * 100

def _arrow(pct: float | None) -> str:
    if pct is None:
        return "—"
    sym = "↑" if pct >= 0 else "↓"
    sign = "+" if pct >= 0 else ""
    color = "green" if pct >= 0 else "red"
    return f'<span style="color:{color}">{sym} {sign}{pct:.1f}%</span>'

def _diff_list(old: list, new: list) -> dict:
    old_set, new_set = set(old), set(new)
    return {
        "added":   sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "kept":    sorted(old_set & new_set),
    }

def compare_snapshots(snap_old: dict, snap_new: dict) -> dict:
    """
    เปรียบเทียบ 2 snapshots และคืน diff dict
    """
    result = {
        "competitor":  snap_new.get("competitor", ""),
        "period_old":  snap_old.get("period", ""),
        "period_new":  snap_new.get("period", ""),
        "platforms":   {},
        "promotions":  _diff_list(snap_old.get("promotions", []), snap_new.get("promotions", [])),
        "content_themes": _diff_list(snap_old.get("content_themes", []), snap_new.get("content_themes", [])),
        "activity_level": {
            "old": snap_old.get("activity_level", ""),
            "new": snap_new.get("activity_level", ""),
        },
        "estimated_reach": {
            "old": snap_old.get("estimated_reach"),
            "new": snap_new.get("estimated_reach"),
            "change_pct": _pct(snap_old.get("estimated_reach"), snap_new.get("estimated_reach")),
        },
        "top_content_new": snap_new.get("top_content", []),
        "notes_new":       snap_new.get("notes", ""),
    }

    for platform in ("facebook", "tiktok", "instagram"):
        old_p = snap_old.get("platforms", {}).get(platform, {})
        new_p = snap_new.get("platforms", {}).get(platform, {})
        result["platforms"][platform] = {
            "followers_old": old_p.get("followers_est"),
            "followers_new": new_p.get("followers_est"),
            "followers_change_pct": _pct(old_p.get("followers_est"), new_p.get("followers_est")),
            "posts_old": old_p.get("posts_count", 0) or old_p.get("videos_count", 0),
            "posts_new": new_p.get("posts_count", 0) or new_p.get("videos_count", 0),
        }

    return result

# ──────────────────────────────────────────────
# Report builder
# ──────────────────────────────────────────────

def generate_comparison_report(diff: dict) -> str:
    comp    = diff["competitor"]
    p_old   = diff["period_old"]
    p_new   = diff["period_new"]
    today   = date.today().isoformat()

    lines = [
        f"# Competitor Tracking: {comp}",
        f"**เปรียบเทียบ:** {p_old} → {p_new}  ",
        f"**วันที่สร้างรายงาน:** {today}",
        "",
        "---",
        "",
        "## Platform Overview",
        "",
        "| Platform | Followers เดิม | Followers ใหม่ | เปลี่ยนแปลง | Posts/Videos |",
        "|----------|---------------|---------------|-------------|--------------|",
    ]

    for platform in ("facebook", "tiktok", "instagram"):
        p = diff["platforms"][platform]
        f_old = f"{p['followers_old']:,}" if p["followers_old"] else "-"
        f_new = f"{p['followers_new']:,}" if p["followers_new"] else "-"
        arrow = _arrow(p["followers_change_pct"])
        posts = f"{p['posts_old']} → {p['posts_new']}"
        lines.append(f"| {platform.capitalize()} | {f_old} | {f_new} | {arrow} | {posts} |")

    # Activity level
    act = diff["activity_level"]
    reach = diff["estimated_reach"]
    reach_old = f"{reach['old']:,}" if reach["old"] else "-"
    reach_new = f"{reach['new']:,}" if reach["new"] else "-"

    lines += [
        "",
        "## Activity & Reach",
        "",
        f"| | {p_old} | {p_new} |",
        "|---|---|---|",
        f"| Activity Level | {act['old'] or '-'} | {act['new'] or '-'} |",
        f"| Estimated Reach | {reach_old} | {reach_new} |",
        "",
    ]

    # Promotions
    promo = diff["promotions"]
    lines += ["## โปรโมชัน", ""]
    if promo["added"]:
        lines.append("**🆕 โปรใหม่ที่เพิ่มมา:**")
        for p in promo["added"]:
            lines.append(f"- {p}")
        lines.append("")
    if promo["removed"]:
        lines.append("**❌ โปรที่หมดแล้ว:**")
        for p in promo["removed"]:
            lines.append(f"- {p}")
        lines.append("")
    if promo["kept"]:
        lines.append("**✅ โปรที่ยังมีอยู่:**")
        for p in promo["kept"]:
            lines.append(f"- {p}")
        lines.append("")
    if not any([promo["added"], promo["removed"], promo["kept"]]):
        lines.append("*ไม่พบข้อมูลโปรโมชัน*\n")

    # Content themes
    ct = diff["content_themes"]
    lines += ["## Content Themes", ""]
    if ct["added"]:
        lines.append("**🆕 Theme ใหม่:**")
        for t in ct["added"]:
            lines.append(f"- {t}")
        lines.append("")
    if ct["removed"]:
        lines.append("**📤 Theme ที่หายไป:**")
        for t in ct["removed"]:
            lines.append(f"- {t}")
        lines.append("")
    if ct["kept"]:
        lines.append("**📌 Theme ต่อเนื่อง:**")
        for t in ct["kept"]:
            lines.append(f"- {t}")
        lines.append("")

    # Top content
    top = diff.get("top_content_new", [])
    if top:
        lines += ["## Top Content ช่วงนี้", ""]
        for i, c in enumerate(top[:5], 1):
            title   = c.get("title", "-")
            views   = f"{c.get('views', '-'):,}" if isinstance(c.get("views"), int) else c.get("views", "-")
            platform = c.get("platform", "")
            lines.append(f"{i}. **{title}** ({platform}) — {views} views")
        lines.append("")

    # Notes
    notes = diff.get("notes_new", "")
    if notes:
        lines += ["## หมายเหตุ / สรุปเพิ่มเติม", "", notes, ""]

    lines.append("*รายงานนี้สร้างโดย Claude Code | Social Analytics App — คลินิกทันตกรรม สกลนคร*")
    return "\n".join(lines)


def generate_summary_report(competitor: str, mode: str = "week") -> str:
    """
    สร้าง comparison report อัตโนมัติจากข้อมูลใน storage

    mode: 'week' | 'month' | 'year'
    """
    today = date.today()
    if mode == "week":
        current = _week_label(today)
        previous = _prev_week_label(current)
    elif mode == "month":
        current = _month_label(today)
        previous = _prev_month_label(current)
    else:
        current = _month_label(today)
        previous = _prev_year_label(current)

    snap_new = load_snapshot(competitor, current)
    snap_old = load_snapshot(competitor, previous)

    if not snap_new and not snap_old:
        return f"# {competitor}\n\n> ⚠️ ไม่พบข้อมูล snapshot สำหรับ {current} หรือ {previous}\n> ใช้ /comp-track --snapshot เพื่อบันทึกข้อมูลปัจจุบัน\n"

    snap_new = snap_new or empty_snapshot(competitor, current)
    snap_old = snap_old or empty_snapshot(competitor, previous)

    diff = compare_snapshots(snap_old, snap_new)
    return generate_comparison_report(diff)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python src/competitor_tracker.py list")
        print("  python src/competitor_tracker.py save <competitor> <json_file>")
        print("  python src/competitor_tracker.py compare <competitor> week|month|year")
        print("  python src/competitor_tracker.py report [competitor]")
        sys.exit(0)

    cmd = args[0]

    if cmd == "list":
        comps = list_all_competitors()
        if not comps:
            print("ยังไม่มีข้อมูลคู่แข่งใน data/competitors/")
        else:
            for c in comps:
                snaps = list_snapshots(c)
                print(f"  {c}: {len(snaps)} snapshot(s) — {snaps[-1] if snaps else 'none'}")

    elif cmd == "save" and len(args) >= 3:
        competitor = args[1]
        json_path  = Path(args[2])
        if not json_path.exists():
            print(f"ไม่พบไฟล์: {json_path}")
            sys.exit(1)
        snapshot = json.loads(json_path.read_text(encoding="utf-8"))
        saved_path = save_snapshot(competitor, snapshot)
        print(f"บันทึกแล้ว: {saved_path}")

    elif cmd == "compare" and len(args) >= 3:
        competitor = args[1]
        mode       = args[2]  # week | month | year
        report = generate_summary_report(competitor, mode)
        print(report)

    elif cmd == "report":
        targets = [args[1]] if len(args) >= 2 else list_all_competitors()
        if not targets:
            print("ไม่พบข้อมูลคู่แข่ง")
            sys.exit(0)
        today_str = date.today().strftime("%Y%m%d")
        out_path  = REPORT_DIR / f"comp-track-{today_str}.md"
        out_path.parent.mkdir(exist_ok=True)
        sections  = []
        for comp in targets:
            sections.append(generate_summary_report(comp, "week"))
            sections.append("\n---\n")
        out_path.write_text("\n".join(sections), encoding="utf-8")
        print(f"บันทึกแล้ว: {out_path}")

    else:
        print(f"คำสั่งไม่ถูกต้อง: {' '.join(args)}")
        sys.exit(1)
