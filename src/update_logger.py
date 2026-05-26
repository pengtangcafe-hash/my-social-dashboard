"""
update_logger.py — บันทึก/อ่าน ประวัติการอัปเดตข้อมูลแต่ละหมวด

Sections ที่ track:
  intel        → ข่าวกรองตลาด  (เรียกจาก /intel)
  pricing      → ราคาทำฟัน      (เรียกจาก /intel เพราะ pricing มาจาก intel data)
  deep         → วิเคราะห์เชิงลึก (เรียกจาก /intel-deep)
  comp_track   → Tracker คู่แข่ง  (เรียกจาก /comp-track --snapshot)

Usage:
  from src.update_logger import log_update, get_log, inject_into_dashboard

  log_update("intel")               # บันทึกว่าวันนี้อัปเดต intel
  log_update("intel", "pricing")    # บันทึกหลาย section พร้อมกัน
  get_log()                         # คืน dict ทั้งหมด
  inject_into_dashboard(html_path)  # แทรก UPDATE_LOG ใน dashboard HTML

CLI:
  python src/update_logger.py log intel pricing
  python src/update_logger.py log comp_track
  python src/update_logger.py show
  python src/update_logger.py inject dashboard/index.html
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "data" / "update-log.json"

SECTION_LABELS = {
    "intel":      "ข่าวกรองตลาด",
    "pricing":    "ราคาทำฟัน",
    "deep":       "วิเคราะห์เชิงลึก",
    "comp_track": "Tracker คู่แข่ง",
}

THAI_MONTHS = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
               "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

def _fmt_thai(iso_date: str) -> str:
    """'2026-05-27' → '27 พ.ค. 2569'"""
    try:
        y, m, d = iso_date.split("-")
        thai_year = int(y) + 543
        return f"{int(d)} {THAI_MONTHS[int(m)]} {thai_year}"
    except Exception:
        return iso_date

# ──────────────────────────────────────────────
# Read / Write log
# ──────────────────────────────────────────────

def _load() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {"sections": {}}

def _save(data: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_log() -> dict:
    return _load()

# ──────────────────────────────────────────────
# Log an update
# ──────────────────────────────────────────────

def log_update(*sections: str) -> dict:
    """
    บันทึกว่าวันนี้มีการอัปเดต sections ที่ระบุ
    คืน dict ของ sections ที่อัปเดตแล้ว
    """
    today = date.today().isoformat()
    data  = _load()

    updated = {}
    for section in sections:
        if section not in SECTION_LABELS:
            print(f"⚠️  ไม่รู้จัก section: {section} (รู้จัก: {list(SECTION_LABELS.keys())})")
            continue

        sec = data["sections"].setdefault(section, {
            "label":        SECTION_LABELS[section],
            "last_updated": "",
            "update_count": 0,
            "history":      [],
        })

        # เพิ่มวันที่ถ้ายังไม่มี (ไม่ซ้ำในวันเดียวกัน)
        if today not in sec["history"]:
            sec["history"].append(today)
            sec["update_count"] = len(sec["history"])

        sec["last_updated"] = today
        sec["label"]        = SECTION_LABELS[section]
        updated[section]    = sec

    _save(data)
    return updated

# ──────────────────────────────────────────────
# Build UPDATE_LOG JS constant
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    """สร้าง JS constant UPDATE_LOG ที่ inject เข้า dashboard"""
    data = _load()
    sections = data.get("sections", {})

    # Enrich with Thai-formatted dates
    enriched = {}
    for key, sec in sections.items():
        enriched[key] = {
            "label":         sec.get("label", key),
            "last_updated":  sec.get("last_updated", ""),
            "last_updated_th": _fmt_thai(sec.get("last_updated", "")),
            "update_count":  sec.get("update_count", 0),
            "history":       sec.get("history", []),
            "history_th":    [_fmt_thai(d) for d in sec.get("history", [])],
        }

    return f"const UPDATE_LOG = {json.dumps(enriched, ensure_ascii=False)};"

# ──────────────────────────────────────────────
# Inject into dashboard HTML
# ──────────────────────────────────────────────

def inject_into_dashboard(html_path: str | Path) -> bool:
    """
    แทรกหรืออัปเดต UPDATE_LOG constant ใน dashboard HTML
    วางก่อน // ── Chart instances cache ──
    คืน True ถ้าสำเร็จ
    """
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()

    # ถ้ามี UPDATE_LOG อยู่แล้ว ให้แทนที่
    pattern = r"const UPDATE_LOG\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต UPDATE_LOG ใน {html_path.name}")
    else:
        # แทรกก่อน // ── Chart instances cache ──
        marker = "// ── Chart instances cache ──"
        if marker in html:
            html = html.replace(marker, f"{js_const}\n\n{marker}")
            print(f"✅ เพิ่ม UPDATE_LOG ใน {html_path.name}")
        else:
            print(f"⚠️  ไม่พบ marker ใน {html_path.name} — เพิ่ม UPDATE_LOG ที่ท้าย <script>")
            html = html.replace("<script>", f"<script>\n{js_const}\n", 1)

    html_path.write_text(html, encoding="utf-8")
    return True

# ──────────────────────────────────────────────
# Show log (CLI)
# ──────────────────────────────────────────────

def show_log() -> None:
    data = _load()
    print("\n📋 Update Log — Social Analytics Dashboard")
    print("─" * 50)
    for key, sec in data.get("sections", {}).items():
        last = _fmt_thai(sec.get("last_updated", ""))
        count = sec.get("update_count", 0)
        history = sec.get("history", [])
        print(f"\n  [{sec.get('label', key)}]")
        print(f"    อัปเดตล่าสุด : {last}")
        print(f"    จำนวนครั้ง   : {count} ครั้ง")
        print(f"    ประวัติ      : {', '.join(_fmt_thai(d) for d in history)}")
    print()

# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args:
        show_log()
        sys.exit(0)

    cmd = args[0]

    if cmd == "show":
        show_log()

    elif cmd == "log" and len(args) >= 2:
        sections = args[1:]
        updated = log_update(*sections)
        for key, sec in updated.items():
            print(f"✅ บันทึก [{sec['label']}] — {_fmt_thai(sec['last_updated'])} (ครั้งที่ {sec['update_count']})")

    elif cmd == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1])

    else:
        print("Usage:")
        print("  python src/update_logger.py show")
        print("  python src/update_logger.py log intel pricing deep comp_track")
        print("  python src/update_logger.py inject dashboard/index.html")
