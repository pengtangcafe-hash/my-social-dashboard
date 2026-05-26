"""
content_category_analyzer.py — วิเคราะห์ performance ตาม content format/category

Data Sources:
  1. Facebook รูปแบบเนื้อหายอดนิยม.csv — Reach/Engagement/Impressions ต่อ format (Reels, Image, Story...)
  2. data/content-log.json — manual post log พร้อม category tag (education, before_after, ...)

คำนวณแล้ว inject CONTENT_PERF เข้า dashboard HTML

Usage (CLI):
  python src/content_category_analyzer.py show
  python src/content_category_analyzer.py inject dashboard/index.html
  python src/content_category_analyzer.py log tiktok education "วิธีแปรงฟัน" --reach 5200 --engagement 312
"""

import json
import re
import sys
import csv
import io
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
CONTENT_LOG  = DATA_DIR / "content-log.json"
SAMPLE_DIR   = PROJECT_ROOT / "sample-data"
FB_FORMAT_CSV = SAMPLE_DIR / "Facebook" / "รูปแบบเนื้อหายอดนิยม.csv"

CATEGORIES = {
    "education":    {"label": "ความรู้ทันตกรรม", "emoji": "💡"},
    "before_after": {"label": "ก่อน-หลังรักษา",   "emoji": "✨"},
    "faq":          {"label": "ตอบคำถามที่พบบ่อย", "emoji": "❓"},
    "promotion":    {"label": "โปรโมชั่น",          "emoji": "🎁"},
    "behind_scenes":{"label": "เบื้องหลังคลินิก",   "emoji": "🏥"},
    "local":        {"label": "Content สกลนคร",     "emoji": "🌊"},
}

# ──────────────────────────────────────────────
# Parse Facebook content format CSV
# ──────────────────────────────────────────────

# Known format order from FB export (UTF-16, mojibake — we hardcode known column order)
_FB_FORMAT_NAMES = {
    "Reels":         "Reels",
    "�ٻ��":    "รูปภาพ",   # corrupt Thai
    "�ʵ���":  "สตอรี่",
    "����������": "อัลบั้ม",
    "������": "ลิงก์",
    "����": "วิดีโอ",
}


def _parse_fb_format_csv() -> dict | None:
    """
    อ่าน Facebook รูปแบบเนื้อหายอดนิยม.csv
    คืน dict: {
        "reach":       {format_name: value, ...},
        "engagement":  {format_name: value, ...},
        "impressions": {format_name: value, ...},
    }
    หรือ None ถ้าไม่พบไฟล์ / parse ไม่ได้
    """
    if not FB_FORMAT_CSV.exists():
        return None

    try:
        raw = FB_FORMAT_CSV.read_bytes()
        text = raw.decode("utf-16")
    except Exception:
        return None

    # แยกบรรทัด ข้ามบรรทัด sep= และบรรทัดเปล่า
    lines = [ln.strip() for ln in text.splitlines()]
    # กรองแค่บรรทัดที่มีข้อมูล (ไม่ใช่ sep=, ไม่เปล่า)
    data_lines = [ln for ln in lines if ln and not ln.startswith("sep=")]

    # โครงสร้าง: บรรทัดคู่ header+values สลับกัน 3 section
    # (ยอดรับ/reach, การมีส่วนร่วม/engagement, การแสดง/impressions)
    # แต่ชื่อ section อ่านไม่ออกจาก mojibake — ใช้ตำแหน่งแทน
    # data_lines ที่เหลือ: [section1_label, header1, values1, section2_label, header2, values2, ...]
    # section_label ถ้ามีแค่ 1 field (ไม่มีคอมมา) = label
    # header = หลาย field, values = หลาย field ตัวเลข

    sections_raw = []
    i = 0
    while i < len(data_lines):
        line = data_lines[i]
        # ตรวจว่าเป็น header row (มีคอมมา)
        reader = csv.reader(io.StringIO(line))
        fields = next(reader)
        if len(fields) > 1:
            # น่าจะเป็น header — บรรทัดถัดไปเป็น values
            headers = [f.strip().strip('"') for f in fields]
            if i + 1 < len(data_lines):
                v_reader = csv.reader(io.StringIO(data_lines[i + 1]))
                values_raw = next(v_reader)
                values = []
                for v in values_raw:
                    v = v.strip().strip('"')
                    try:
                        values.append(float(v.replace(",", "")))
                    except ValueError:
                        values.append(0.0)
                sections_raw.append((headers, values))
                i += 2
            else:
                i += 1
        else:
            # section label — ข้ามไป
            i += 1

    if len(sections_raw) < 3:
        return None

    def _build_dict(headers, values):
        d = {}
        for h, v in zip(headers, values):
            name = _clean_fb_format_name(h)
            d[name] = int(v)
        return d

    return {
        "reach":       _build_dict(*sections_raw[0]),
        "engagement":  _build_dict(*sections_raw[1]),
        "impressions": _build_dict(*sections_raw[2]),
    }


def _clean_fb_format_name(raw: str) -> str:
    """แปลง mojibake หรือ Reels → ชื่อที่อ่านได้"""
    raw = raw.strip()
    if raw == "Reels":
        return "Reels"
    # decode cp874 ถ้าเป็น mojibake
    try:
        decoded = raw.encode("latin-1").decode("cp874")
        return decoded
    except Exception:
        return raw


# ──────────────────────────────────────────────
# Content Log
# ──────────────────────────────────────────────

def load_content_log() -> list[dict]:
    if not CONTENT_LOG.exists():
        return []
    try:
        data = json.loads(CONTENT_LOG.read_text(encoding="utf-8"))
        return data.get("posts", [])
    except Exception:
        return []


def add_post_log(platform: str, category: str, title: str,
                 reach: float = 0, engagement: float = 0,
                 post_date: str | None = None, notes: str = "") -> None:
    """เพิ่ม post ลงใน content-log.json"""
    if CONTENT_LOG.exists():
        data = json.loads(CONTENT_LOG.read_text(encoding="utf-8"))
    else:
        data = {"posts": []}

    entry = {
        "date":       post_date or date.today().isoformat(),
        "platform":   platform.lower(),
        "category":   category.lower(),
        "title":      title,
        "reach":      float(reach),
        "engagement": float(engagement),
        "notes":      notes,
    }
    data["posts"].append(entry)
    data["last_updated"] = date.today().isoformat()
    CONTENT_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    cat_info = CATEGORIES.get(category, {})
    print(f"✅ บันทึกแล้ว: [{platform}] {cat_info.get('label', category)} — {title}")


# ──────────────────────────────────────────────
# Compute stats
# ──────────────────────────────────────────────

def _compute_category_stats(posts: list[dict]) -> dict:
    """รวม stats ต่อ category จาก post log"""
    stats = {cat: {"posts": 0, "total_reach": 0.0, "total_engagement": 0.0}
             for cat in CATEGORIES}

    for p in posts:
        cat = p.get("category", "")
        if cat not in stats:
            continue
        stats[cat]["posts"] += 1
        stats[cat]["total_reach"] += float(p.get("reach", 0) or 0)
        stats[cat]["total_engagement"] += float(p.get("engagement", 0) or 0)

    result = {}
    for cat, s in stats.items():
        n = s["posts"]
        avg_reach = round(s["total_reach"] / n, 0) if n > 0 else 0
        avg_reach_safe = s["total_reach"] if s["total_reach"] > 0 else 1
        avg_eng_rate = round(s["total_engagement"] / avg_reach_safe * 100, 2) if avg_reach > 0 else 0
        result[cat] = {
            "label":       CATEGORIES[cat]["label"],
            "emoji":       CATEGORIES[cat]["emoji"],
            "posts":       n,
            "avg_reach":   int(avg_reach),
            "avg_eng_rate": avg_eng_rate,
        }
    return result


def _make_recommendation(fb_fmt: dict | None, cat_stats: dict, total_posts: int) -> str:
    if total_posts == 0 and fb_fmt is None:
        return "เริ่มบันทึก post ของคุณเพื่อดู category ที่ perform ดีที่สุด"

    recs = []

    if fb_fmt:
        top_reach = fb_fmt.get("top_reach")
        top_eng   = fb_fmt.get("top_engagement")
        if top_reach:
            recs.append(f"'{top_reach}' สร้าง Reach สูงสุดบน Facebook — เพิ่มสัดส่วนในแผน content")
        if top_eng and top_eng != top_reach:
            recs.append(f"'{top_eng}' ได้ Engagement ต่อโพสต์สูงสุด")

    if total_posts >= 3:
        # หา top category by engagement rate
        top_cat = max(
            (c for c in cat_stats if cat_stats[c]["posts"] > 0),
            key=lambda c: cat_stats[c]["avg_eng_rate"],
            default=None
        )
        if top_cat:
            info = cat_stats[top_cat]
            recs.append(
                f"'{info['emoji']} {info['label']}' engagement rate เฉลี่ย {info['avg_eng_rate']:.1f}% — "
                f"แนะนำเพิ่ม content ประเภทนี้"
            )

    return " • ".join(recs) if recs else "นำเข้าข้อมูลเพิ่มเติมเพื่อรับคำแนะนำที่แม่นยำขึ้น"


def compute_stats() -> dict:
    fb_raw  = _parse_fb_format_csv()
    posts   = load_content_log()
    cat_stats = _compute_category_stats(posts)

    # แปลง fb_raw เป็น format ที่ dashboard ใช้
    fb_fmt = None
    if fb_raw:
        all_fmts = sorted(
            set(list(fb_raw.get("reach", {}).keys()) +
                list(fb_raw.get("engagement", {}).keys()) +
                list(fb_raw.get("impressions", {}).keys()))
        )
        # เรียงตาม reach DESC
        reach_dict = fb_raw.get("reach", {})
        all_fmts_sorted = sorted(all_fmts,
                                 key=lambda f: reach_dict.get(f, 0), reverse=True)
        fb_fmt = {
            "labels":      all_fmts_sorted,
            "reach":       [reach_dict.get(f, 0) for f in all_fmts_sorted],
            "engagement":  [fb_raw.get("engagement", {}).get(f, 0) for f in all_fmts_sorted],
            "impressions": [fb_raw.get("impressions", {}).get(f, 0) for f in all_fmts_sorted],
            "top_reach":     max(reach_dict, key=reach_dict.get) if reach_dict else None,
            "top_engagement": (lambda d: max(d, key=d.get) if d else None)(fb_raw.get("engagement", {})),
        }

    top_cat = None
    if any(cat_stats[c]["posts"] > 0 for c in cat_stats):
        top_cat = max(
            (c for c in cat_stats if cat_stats[c]["posts"] > 0),
            key=lambda c: cat_stats[c]["avg_eng_rate"],
            default=None
        )

    return {
        "generated_at":      date.today().isoformat(),
        "has_format_data":   fb_fmt is not None,
        "has_category_data": any(cat_stats[c]["posts"] > 0 for c in cat_stats),
        "total_logged_posts": len(posts),
        "fb_formats":        fb_fmt,
        "categories":        cat_stats,
        "top_category":      top_cat,
        "recommendation":    _make_recommendation(fb_fmt, cat_stats, len(posts)),
    }


# ──────────────────────────────────────────────
# Build JS + inject
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    data = compute_stats()
    return f"const CONTENT_PERF = {json.dumps(data, ensure_ascii=False)};"


def inject_into_dashboard(html_path: str | Path) -> bool:
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html     = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()
    marker   = "// ── Content Category Data ──"

    pattern = r"const CONTENT_PERF\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต CONTENT_PERF ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{marker}\n{js_const}", 1)
        print(f"✅ เพิ่ม CONTENT_PERF ใน {html_path.name}")
    else:
        fallback = "// ── Monthly Trend Data ──"
        if fallback in html:
            html = html.replace(fallback, f"{marker}\n{js_const}\n\n{fallback}", 1)
        else:
            html = html.replace("<script>", f"<script>\n{marker}\n{js_const}\n", 1)
        print(f"✅ เพิ่ม CONTENT_PERF (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# CLI display
# ──────────────────────────────────────────────

def show_stats() -> None:
    data = compute_stats()
    print("\n📊 Content Category Analyzer")
    print("─" * 55)

    fb = data.get("fb_formats")
    if fb:
        print("\n  [Facebook Content Format]")
        labels = fb["labels"]
        reach  = fb["reach"]
        eng    = fb["engagement"]
        for i, lbl in enumerate(labels):
            r = reach[i] if i < len(reach) else 0
            e = eng[i]   if i < len(eng) else 0
            bar = "█" * min(int(r / max(reach) * 20), 20) if max(reach) > 0 else ""
            print(f"    {lbl:<14} Reach:{r:>5}  Eng:{e:>4}  {bar}")
        print(f"\n  Top reach: {fb['top_reach']}  |  Top engagement: {fb['top_engagement']}")

    posts = data["total_logged_posts"]
    print(f"\n  [Category Log] — {posts} post(s) บันทึกแล้ว")
    cat_stats = data.get("categories", {})
    for cat, s in cat_stats.items():
        if s["posts"] > 0:
            print(f"    {s['emoji']} {s['label']:<18} {s['posts']} posts  "
                  f"avg reach {s['avg_reach']:,}  eng {s['avg_eng_rate']:.1f}%")

    if posts == 0:
        print("    (ยังไม่มีข้อมูล — ใช้ 'log' command เพื่อบันทึก post)")

    print(f"\n  💡 {data['recommendation']}\n")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_stats()

    elif args[0] == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1])

    elif args[0] == "log" and len(args) >= 4:
        platform = args[1].lower()
        category = args[2].lower()
        title    = args[3]

        # parse optional flags
        reach = 0.0
        engagement = 0.0
        notes = ""
        post_date = None

        i = 4
        while i < len(args):
            if args[i] == "--reach" and i + 1 < len(args):
                reach = float(args[i + 1]); i += 2
            elif args[i] == "--engagement" and i + 1 < len(args):
                engagement = float(args[i + 1]); i += 2
            elif args[i] == "--date" and i + 1 < len(args):
                post_date = args[i + 1]; i += 2
            elif args[i] == "--notes" and i + 1 < len(args):
                notes = args[i + 1]; i += 2
            else:
                i += 1

        if category not in CATEGORIES:
            print(f"ประเภทที่ใช้ได้: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)

        add_post_log(platform, category, title, reach, engagement, post_date, notes)

    else:
        print("Usage:")
        print("  python src/content_category_analyzer.py show")
        print("  python src/content_category_analyzer.py inject dashboard/index.html")
        print("  python src/content_category_analyzer.py log tiktok education 'วิธีแปรงฟัน' --reach 5200 --engagement 312")
        print()
        print(f"Categories: {', '.join(CATEGORIES.keys())}")
