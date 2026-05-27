"""
content_radar.py — ระบบ Content Radar: วิเคราะห์คู่แข่งแล้วสร้างไอเดีย content ที่ตอบโต้

อ่านข้อมูล competitor snapshots ล่าสุด → วิเคราะห์ว่าเขากำลังโพสต์อะไร
→ สร้างไอเดีย content ของเรา ที่ parallel แต่ไม่ก็อป (mirror / counter / expand)
→ พร้อม hook, caption, hashtag, reel script outline

Usage:
  python src/content_radar.py show              — แสดง radar ปัจจุบัน
  python src/content_radar.py generate          — วิเคราะห์ใหม่จาก snapshot ล่าสุด
  python src/content_radar.py inject dashboard/index.html
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT   = Path(__file__).parent.parent
DATA_DIR       = PROJECT_ROOT / "data"
COMPETITORS_DIR = DATA_DIR / "competitors"
REPORTS_DIR    = PROJECT_ROOT / "reports"
RADAR_FILE     = DATA_DIR / "content-radar.json"

PLATFORM_COLORS = {
    "facebook":  "#1877f2",
    "tiktok":    "#010101",
    "instagram": "#e1306c",
}

# ── Strategy types ──
STRATEGY_LABELS = {
    "mirror":  {"label": "Mirror", "desc": "เรื่องเดียวกัน มุมต่างกัน", "color": "#8b5cf6", "icon": "🪞"},
    "counter": {"label": "Counter", "desc": "ตอบโต้โดยตรง ด้านที่เราดีกว่า", "color": "#ef4444", "icon": "⚔️"},
    "expand":  {"label": "Expand", "desc": "ขยายหัวข้อที่เขาไม่ได้ทำ", "color": "#0ea5e9", "icon": "🚀"},
    "own":     {"label": "Own It", "desc": "Claim พื้นที่ที่เขาไม่มี", "color": "#10b981", "icon": "👑"},
}


# ──────────────────────────────────────────────
# Load competitor snapshots (latest per competitor)
# ──────────────────────────────────────────────

def _load_latest_snapshots() -> list[dict]:
    """Load newest JSON file per competitor folder."""
    snapshots = []
    if not COMPETITORS_DIR.exists():
        return snapshots
    for comp_dir in COMPETITORS_DIR.iterdir():
        if not comp_dir.is_dir():
            continue
        files = sorted(comp_dir.glob("*.json"), reverse=True)
        if not files:
            continue
        try:
            data = json.loads(files[0].read_text(encoding="utf-8"))
            snapshots.append(data)
        except Exception:
            pass
    return snapshots


# ──────────────────────────────────────────────
# Content opportunity mapping
# ──────────────────────────────────────────────

# Each entry: topic_keywords → { strategy, our_angle, hook_th, caption_th, hashtags, platform }
CONTENT_PLAYBOOK = [
    # ── Adult Orthodontics (DentalPark is heavy on this) ──
    {
        "keywords": ["รุ่นใหญ่", "adult", "ผู้ใหญ่", "วัยทำงาน", "40", "35"],
        "strategy": "mirror",
        "service": "จัดฟันใส",
        "our_angle": "รุ่นใหญ่ก็สดใสได้ — จัดฟันใส ไม่เห็นเหล็ก ไปทำงานได้",
        "hook": "อายุ 30+ อยากจัดฟัน แต่กลัวเหมือนเด็กม.ต้น? มาดูวิธีที่เขาไม่บอก →",
        "caption": "รุ่นใหญ่ก็สดใสได้ ✨\n\nจัดฟันใส (Clear Aligner) ใส่แล้วไม่มีใครรู้\nทำงานได้ ประชุมได้ กินข้าวได้\nถอดล้างง่าย ไม่ต้องงดอาหารที่ชอบ\n\nปรึกษาฟรี ไม่มีค่าใช้จ่าย 📲\n\n#จัดฟันใส #ClearAligner #จัดฟันสกลนคร #ผู้ใหญ่ก็จัดฟันได้",
        "hashtags": ["#จัดฟันใส", "#จัดฟันสกลนคร", "#รุ่นใหญ่ก็ยิ้มได้", "#ClearAligner", "#ทันตกรรมสกลนคร"],
        "reel_outline": "0-3s: Show ผู้หญิงอายุ 35+ กำลังรอยยิ้มสวย | 4-8s: 'ฉันจัดฟันตอนอายุ 37' | 9-12s: ก่อน-หลัง clear aligner | 13-15s: 'ปรึกษาฟรีวันนี้'",
        "platform": "tiktok",
    },
    # ── Clear Aligner Promotion ──
    {
        "keywords": ["จัดฟันใส", "clear aligner", "นวัตกรรม", "ใส", "invisible"],
        "strategy": "counter",
        "service": "จัดฟันใส",
        "our_angle": "จัดฟันใส — เราใช้แบรนด์อะไร? เปรียบให้เห็น 3 ตัวเลือก",
        "hook": "จัดฟันใส ราคาต่างกันเพราะอะไร? หมอตอบตรงๆ ไม่มีกั๊ก →",
        "caption": "จัดฟันใส มีหลายแบบ ราคาต่างกันมาก เพราะ?\n\n💡 Invisible vs แบรนด์ name brand\n💡 ความแม่นยำของ 3D scan\n💡 ระยะเวลาที่ใส่\n\nไม่ต้องงง มาปรึกษาก่อน ฟรี ไม่มีค่าใช้จ่าย\nบอกความต้องการ หมอออกแบบให้เลย 🦷\n\n#จัดฟันใส #ClearAligner #จัดฟันสกลนคร",
        "hashtags": ["#จัดฟันใส", "#ClearAligner", "#จัดฟันราคา", "#จัดฟันสกลนคร"],
        "reel_outline": "0-3s: 'จัดฟันใสราคาต่างกันมาก' | 4-10s: อธิบาย 3 ปัจจัย (graphic simple) | 11-14s: 'ปรึกษาเราก่อนได้เลย' | 15s: CTA",
        "platform": "tiktok",
    },
    # ── Metal Base Denture (หมอจั่นเจา push heavily) ──
    {
        "keywords": ["ฟันปลอมฐานโลหะ", "ฟันปลอม", "denture", "โลหะ", "ไทเทเนียม"],
        "strategy": "expand",
        "service": "ฟันปลอม",
        "our_angle": "ฟันปลอม 3 แบบ เลือกแบบไหนเหมาะกับคุณ? หมอตอบ 60 วิ",
        "hook": "ฟันปลอมถอดได้ vs ฟันปลอมติดแน่น — ต่างกันยังไง ใครควรทำแบบไหน?",
        "caption": "ฟันปลอม มี 3 แบบ เลือกผิดเสียดาย 😬\n\n1️⃣ ฟันปลอมฐานอะคริลิก — ราคาประหยัด\n2️⃣ ฟันปลอมฐานโลหะ — แข็งแรง บางกว่า\n3️⃣ รากฟันเทียม — ใส่สบายที่สุด ถาวร\n\nเลือกตามงบ ตามสุขภาพกระดูก ตามไลฟ์สไตล์\nปรึกษาฟรี หมอแนะนำตรงๆ 📲\n\n#ฟันปลอมสกลนคร #รากฟันเทียม #ทันตกรรมสกลนคร",
        "hashtags": ["#ฟันปลอมสกลนคร", "#ฟันปลอม", "#รากฟันเทียม", "#ทันตกรรมสกลนคร"],
        "reel_outline": "0-3s: 'ฟันปลอมมี 3 แบบ คุณรู้ไหม?' | 4-12s: อธิบายแต่ละแบบ 3 วิ | 13-15s: 'บอกหมอได้เลยว่าต้องการอะไร'",
        "platform": "tiktok",
    },
    # ── Before/After (ทุกคู่แข่งทำ แต่เราทำได้ดีกว่า) ──
    {
        "keywords": ["before_after", "before after", "ก่อน", "หลัง", "รีวิว", "เคส"],
        "strategy": "own",
        "service": "จัดฟัน",
        "our_angle": "Before/After series จริง — ไม่ตกแต่ง ไม่กรอง",
        "hook": "6 เดือนที่ผ่านมา ฟันเปลี่ยนไปขนาดนี้ (ดูจริงๆ ไม่ใช้ filter) →",
        "caption": "นี่คือผลลัพธ์จริง — ไม่ filter ไม่แต่ง ✅\n\nคนไข้ของเราเริ่มต้นด้วยฟันซ้อน 6 เดือนต่อมาเห็นความเปลี่ยนแปลงชัดเจน\n\nทุกเคสไม่เหมือนกัน แต่ทุกเคสเราดูแลด้วยหัวใจ 🦷❤️\n\nอยากรู้ว่าเคสคุณใช้เวลาเท่าไหร่? มาปรึกษาฟรี\n\n#จัดฟันสกลนคร #BeforeAfter #จัดฟันได้ผลจริง",
        "hashtags": ["#จัดฟันสกลนคร", "#BeforeAfter", "#จัดฟันผลจริง", "#ทันตกรรมสกลนคร"],
        "reel_outline": "0-2s: ภาพก่อน (ไม่มีแสง fancy) | 3-8s: กระบวนการ (รวบรัด) | 9-14s: ผลหลัง reveal | 15s: 'นัดปรึกษาฟรี'",
        "platform": "tiktok",
    },
    # ── Clinic Tour (Dio ทำ แต่เราทำด้วย personal touch) ──
    {
        "keywords": ["clinic_tour", "ทัวร์คลินิก", "บรรยากาศ", "สาขา", "tour"],
        "strategy": "mirror",
        "service": "คลินิก",
        "our_angle": "ทัวร์คลินิก — 'ทำไมลูกค้าถึงกลับมาซ้ำ?' หมอพาดู",
        "hook": "ครั้งแรกที่เข้าคลินิกทันตกรรม กลัวไหม? เข้าก่อนดูก่อนได้เลย →",
        "caption": "กลัวหมอฟัน? ปกติมากเลย 😊\n\nมาดูก่อนว่าคลินิกเราเป็นยังไง ก่อนตัดสินใจนัด\nบรรยากาศอบอุ่น เครื่องมือทันสมัย หมอใจดี\n\nเปิดบริการ จ-ศ 09:00-19:00 เสาร์-อาทิตย์ 09:00-17:00\nโทรนัดหรือ inbox มาเลย ไม่ต้องรอ 📲\n\n#ทันตกรรมสกลนคร #คลินิกฟันสกลนคร #กลัวหมอฟัน",
        "hashtags": ["#ทันตกรรมสกลนคร", "#คลินิกฟัน", "#กลัวหมอฟัน", "#สกลนคร"],
        "reel_outline": "0-3s: หน้าคลินิก shot | 4-10s: walk-through ห้องรอ ห้องรักษา | 11-14s: หมอยิ้มพูดทัก | 15s: ที่อยู่ + เบอร์",
        "platform": "facebook",
    },
    # ── Veneer (Toothmate ทำ composite veneer) ──
    {
        "keywords": ["veneer", "วีเนียร์", "composite", "ครอบฟัน"],
        "strategy": "expand",
        "service": "วีเนียร์",
        "our_angle": "Composite Veneer vs Porcelain — ต่างกันยังไง? เลือกแบบไหนคุ้มกว่า",
        "hook": "วีเนียร์มี 2 แบบ ราคาต่างกัน 5 เท่า แต่ผลต่างกันเท่าไหร่?",
        "caption": "วีเนียร์ฟัน มีกี่แบบ รู้ไหม? 🦷\n\n✅ Composite Veneer — ทำวันเดียวเสร็จ ราคาเป็นมิตร แก้ไขได้\n✅ Porcelain Veneer — ทนทานกว่า สีสวยกว่า อายุ 10-15 ปี\n\nเลือกแบบไหนดีกว่า? ขึ้นอยู่กับฟันและงบของคุณ\nปรึกษาหมอก่อน ฟรี ไม่มีข้อผูกมัด 📲\n\n#วีเนียร์ #ฟันสวย #ทันตกรรมสกลนคร #Veneer",
        "hashtags": ["#วีเนียร์", "#ฟันสวย", "#CompositeVeneer", "#ทันตกรรมสกลนคร"],
        "reel_outline": "0-3s: Hook graphic 'วีเนียร์ 2 แบบ ต่างกันไหม?' | 4-10s: อธิบาย side-by-side | 11-14s: ก่อน-หลัง veneer จริง | 15s: CTA",
        "platform": "instagram",
    },
    # ── FAQ Dental (FAQ ทำได้ดีที่สุดใน content log ของเรา) ──
    {
        "keywords": ["faq", "คำถาม", "ทำไม", "เหตุผล", "อธิบาย", "คือ", "ควร"],
        "strategy": "own",
        "service": "ทั่วไป",
        "our_angle": "'หมอตอบตรงๆ' — FAQ series ที่คู่แข่งไม่กล้าตอบ",
        "hook": "คำถามที่คนกลัวถามหมอฟัน — หมอตอบตรงๆ ทุกข้อ",
        "caption": "หมอตอบตรง ไม่กั๊ก 🎤\n\nQ: จัดฟันเจ็บไหม?\nA: เจ็บแน่ แต่แค่ 2-3 วันแรก หลังจากนั้นชิน\n\nQ: ต้องถอนฟันก่อนจัดไหม?\nA: ขึ้นกับเคส ไม่ใช่ทุกคน\n\nQ: จัดฟันแล้วต้องใส่รีเทนเนอร์นานไหม?\nA: ใส่ตลอดชีวิตคืน ถ้าไม่อยากฟันกลับ\n\nอยากรู้อะไรอีก? comment ไว้ตอบเลย ⬇️\n\n#จัดฟันสกลนคร #FAQ #หมอตอบตรง #ทันตกรรม",
        "hashtags": ["#FAQ", "#หมอตอบตรง", "#จัดฟัน", "#ทันตกรรมสกลนคร", "#จัดฟันสกลนคร"],
        "reel_outline": "0-3s: 'คำถามที่คนกลัวถาม' | 4-12s: Q&A 3 ข้อ ตอบเร็ว | 13-15s: 'มีคำถามอื่น? Comment!' | ใช้ text overlay + face cam",
        "platform": "tiktok",
    },
    # ── Teeth Whitening (ไม่ค่อยมีคู่แข่งทำ) ──
    {
        "keywords": ["ฟอกสีฟัน", "whitening", "ฟันขาว", "สีฟัน"],
        "strategy": "own",
        "service": "ฟอกสีฟัน",
        "our_angle": "ฟอกสีฟัน 1 ชั่วโมง ขาวขึ้น 5 เฉดสี — ทดสอบจริง",
        "hook": "ฟันเหลืองทั้งที่แปรงทุกวัน? นี่คือสาเหตุจริงๆ และวิธีแก้ →",
        "caption": "ฟันไม่ขาวทั้งที่แปรงทุกวัน? 😰\n\nเหตุผลจริง:\n☕ กาแฟ ชา — ฝังสีในเนื้อฟัน\n🍷 อาหารสีเข้ม — สะสมทุกวัน\n⏰ อายุ — ฟันเหลืองตามธรรมชาติ\n\nแก้ได้ด้วยฟอกสีฟัน 1 ชั่วโมง\nขาวขึ้นทันที ไม่เจ็บ ไม่ตัดฟัน\n\nราคาเริ่มต้น 1,490 บาท 💬 DM สอบถามได้\n\n#ฟอกสีฟัน #ฟอกสีฟันสกลนคร #ฟันขาว #Whitening",
        "hashtags": ["#ฟอกสีฟัน", "#ฟอกสีฟันสกลนคร", "#ฟันขาว", "#Whitening", "#ทันตกรรมสกลนคร"],
        "reel_outline": "0-3s: Close-up ฟันก่อน | 4-8s: อธิบาย 3 สาเหตุ fast cut | 9-13s: กระบวนการฟอก montage | 14-15s: ฟันหลัง + ราคา",
        "platform": "tiktok",
    },
    # ── Price Transparency (Toothmate ทำ Dio ทำ) ──
    {
        "keywords": ["ราคา", "price", "บาท", "โปร", "ผ่อน", "ค่า"],
        "strategy": "counter",
        "service": "ทั่วไป",
        "our_angle": "เปิดราคาตรง ไม่มีซ่อน — ดูก่อนตัดสินใจ",
        "hook": "ราคาทำฟันที่สกลนคร — เราเปิดให้ดูตรงๆ เลย",
        "caption": "อยากรู้ราคาก่อนนัด? บอกได้เลย 🦷\n\n💰 ขูดหินปูน — เริ่ม 500 บาท\n💰 อุดฟัน — เริ่ม 300 บาท\n💰 ฟอกสีฟัน — เริ่ม 1,490 บาท\n💰 จัดฟัน — เริ่ม 25,000 บาท\n💰 รากฟันเทียม — เริ่ม 30,000 บาท\n\nทุกราคาบวกก็บอก ไม่มีค่าแอบซ่อน\nปรึกษาฟรีก่อนตัดสินใจ 📲\n\n#ราคาทำฟัน #ทันตกรรมสกลนคร #ราคาโปร่งใส",
        "hashtags": ["#ราคาทำฟัน", "#ทันตกรรมสกลนคร", "#ราคาทำฟันสกลนคร", "#จัดฟันราคา"],
        "reel_outline": "0-3s: 'อยากรู้ราคา ดูได้เลย' | 4-12s: scroll ผ่านรายการราคา graphic | 13-15s: 'ปรึกษาก่อน ฟรี' CTA",
        "platform": "facebook",
    },
    # ── Engagement / Humor (Dio ทำ) ──
    {
        "keywords": ["engagement", "humor", "ตลก", "เลื่อนนัด", "ฮา", "relatable"],
        "strategy": "mirror",
        "service": "ทั่วไป",
        "our_angle": "Relatable humor สไตล์อีสาน — ชีวิตคนที่กลัวหมอฟันแต่อยากฟันสวย",
        "hook": "คนที่กลัวหมอฟัน 🆚 คนที่อยากฟันสวย — อยู่คนเดียวกัน",
        "caption": "สิ่งที่คนที่กลัวหมอฟันเป็นทุกคน 😂\n\n'เดี๋ยวไปนะ... เดือนหน้า'\n'ยังไม่เจ็บมาก รอได้'\n'ไปแล้วแต่นัดไม่ได้ซักที'\n\nฉันรู้จักคนแบบนี้ (ก็ตัวเอง 555)\n\nแต่ถ้าพร้อมแล้ว เราพร้อมรอนะ 🦷❤️\nnot judgment, just dental love\n\n#กลัวหมอฟัน #ทันตกรรมสกลนคร #relatable",
        "hashtags": ["#กลัวหมอฟัน", "#ทันตกรรมสกลนคร", "#relatable", "#ฟันดี"],
        "reel_outline": "0-5s: แสดง 'inner monologue' คนที่เลื่อนนัดซ้ำ (text overlay) | 6-12s: สลับกับความจริงที่รู้อยู่ | 13-15s: 'พร้อมแล้วมาได้เลย'",
        "platform": "tiktok",
    },
]


def _match_opportunities(snapshots: list[dict]) -> list[dict]:
    """Map competitor content to our response opportunities."""
    radar_items = []
    seen_strategies = set()

    for snap in snapshots:
        comp_name = snap.get("competitor", "Unknown")
        platforms  = snap.get("platforms", {})
        themes     = snap.get("content_themes", [])
        promotions = snap.get("promotions", [])

        # Collect all content signals
        signals = []
        for platform, pdata in platforms.items():
            for key in ("videos", "posts"):
                for item in pdata.get(key, []):
                    topic = (item.get("topic") or item.get("title") or "").lower()
                    title = (item.get("title") or "").lower()
                    signals.append(topic + " " + title)
        for t in themes:
            signals.append(t.lower())
        for p in promotions:
            signals.append(p.lower())

        combined = " ".join(signals)

        # Match against playbook
        for play in CONTENT_PLAYBOOK:
            matched = any(kw.lower() in combined for kw in play["keywords"])
            if not matched:
                continue

            key = play["strategy"] + "|" + play["service"]
            if key in seen_strategies:
                continue  # dedupe

            seen_strategies.add(key)
            strat = STRATEGY_LABELS[play["strategy"]]

            radar_items.append({
                "competitor":     comp_name,
                "comp_theme":     _extract_theme_title(snap, play["keywords"]),
                "strategy":       play["strategy"],
                "strategy_label": strat["label"],
                "strategy_icon":  strat["icon"],
                "strategy_color": strat["color"],
                "service":        play["service"],
                "our_angle":      play["our_angle"],
                "hook":           play["hook"],
                "caption":        play["caption"],
                "hashtags":       play["hashtags"],
                "reel_outline":   play["reel_outline"],
                "platform":       play["platform"],
            })

    # Also add any unmatched "own it" opportunities
    for play in CONTENT_PLAYBOOK:
        if play["strategy"] == "own":
            key = play["strategy"] + "|" + play["service"]
            if key not in seen_strategies:
                seen_strategies.add(key)
                strat = STRATEGY_LABELS["own"]
                radar_items.append({
                    "competitor":     "—",
                    "comp_theme":     "(ไม่มีคู่แข่งทำ)",
                    "strategy":       "own",
                    "strategy_label": strat["label"],
                    "strategy_icon":  strat["icon"],
                    "strategy_color": strat["color"],
                    "service":        play["service"],
                    "our_angle":      play["our_angle"],
                    "hook":           play["hook"],
                    "caption":        play["caption"],
                    "hashtags":       play["hashtags"],
                    "reel_outline":   play["reel_outline"],
                    "platform":       play["platform"],
                })

    return radar_items


def _extract_theme_title(snap: dict, keywords: list[str]) -> str:
    """Find the most relevant content title from snapshot matching keywords."""
    for platform, pdata in snap.get("platforms", {}).items():
        for key in ("videos", "posts"):
            for item in pdata.get(key, []):
                t = (item.get("title") or item.get("topic") or "")
                if any(kw.lower() in t.lower() for kw in keywords):
                    return t[:60] + ("…" if len(t) > 60 else "")
    themes = snap.get("content_themes", [])
    for kw in keywords:
        for t in themes:
            if kw.lower() in t.lower():
                return t
    return snap.get("competitor", "") + " — " + (", ".join(snap.get("content_themes", [])[:2]))


# ──────────────────────────────────────────────
# Generate + Save radar
# ──────────────────────────────────────────────

def generate_radar() -> dict:
    snapshots = _load_latest_snapshots()
    if not snapshots:
        print("⚠️  ไม่พบ competitor snapshots — รัน /comp-track --snapshot ก่อน")
        return {}

    items = _match_opportunities(snapshots)

    # Sort: counter first, then mirror, own, expand
    order = {"counter": 0, "mirror": 1, "own": 2, "expand": 3}
    items.sort(key=lambda x: order.get(x["strategy"], 9))

    payload = {
        "generated_at":      date.today().isoformat(),
        "competitor_count":  len(snapshots),
        "opportunity_count": len(items),
        "competitors":       [s.get("competitor") for s in snapshots],
        "items":             items,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RADAR_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Content Radar: {len(items)} โอกาส จาก {len(snapshots)} คู่แข่ง → {RADAR_FILE.name}")
    return payload


def load_radar() -> dict:
    if RADAR_FILE.exists():
        try:
            return json.loads(RADAR_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ──────────────────────────────────────────────
# Show
# ──────────────────────────────────────────────

def show_radar() -> None:
    data = load_radar()
    if not data or not data.get("items"):
        print("ยังไม่มีข้อมูล — รัน: python src/content_radar.py generate")
        return

    print(f"\n🎯 Content Radar — อัปเดต {data.get('generated_at','')}")
    print(f"   {data.get('opportunity_count',0)} โอกาส จาก {data.get('competitor_count',0)} คู่แข่ง")
    print("═" * 60)

    for item in data.get("items", []):
        strat = STRATEGY_LABELS.get(item["strategy"], {})
        print(f"\n  {strat.get('icon','?')} [{item['strategy_label'].upper()}] vs {item['competitor']}")
        print(f"  เขา: {item['comp_theme']}")
        print(f"  เรา: {item['our_angle']}")
        print(f"  Hook: {item['hook'][:70]}...")
        print(f"  Platform: {item['platform'].upper()} | บริการ: {item['service']}")
    print()


# ──────────────────────────────────────────────
# Dashboard inject
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    data = load_radar()
    if not data:
        data = generate_radar()
    return f"const CONTENT_RADAR = {json.dumps(data, ensure_ascii=False)};"


def inject_into_dashboard(html_path) -> bool:
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html     = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()
    marker   = "// ── Content Radar Data ──"

    pattern = r"const CONTENT_RADAR\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต CONTENT_RADAR ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{marker}\n{js_const}", 1)
        print(f"✅ เพิ่ม CONTENT_RADAR ใน {html_path.name}")
    else:
        fallback = "// ── Ad Campaign Data ──"
        if fallback in html:
            html = html.replace(fallback, f"{marker}\n{js_const}\n\n{fallback}", 1)
        else:
            html = html.replace("<script>", f"<script>\n{marker}\n{js_const}\n", 1)
        print(f"✅ เพิ่ม CONTENT_RADAR (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_radar()
    elif args[0] == "generate":
        generate_radar()
        show_radar()
    elif args[0] == "inject" and len(args) >= 2:
        if not RADAR_FILE.exists():
            generate_radar()
        inject_into_dashboard(args[1])
    else:
        print("Usage:")
        print("  python src/content_radar.py show")
        print("  python src/content_radar.py generate")
        print("  python src/content_radar.py inject dashboard/index.html")
