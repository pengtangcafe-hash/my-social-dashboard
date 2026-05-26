# คู่มือการใช้งาน Social Analytics Dashboard
**คลินิกทันตกรรม สกลนคร**
อัปเดตล่าสุด: 27 พฤษภาคม 2569 (v2 — Goal Tracker + Monthly Trend + Content Analyzer)

---

## Dashboard URL
**https://pengtangcafe-hash.github.io/my-social-dashboard/**

---

## คำสั่งหลัก (พิมพ์ใน Claude Code)

### วิเคราะห์ข้อมูล Social Media ของเรา

| คำสั่ง | ทำอะไร |
|---|---|
| `/analyze` | วิเคราะห์ทุก platform จาก sample-data/ + อัปเดต dashboard |
| `/analyze FILE` | วิเคราะห์ไฟล์เฉพาะ เช่น `/analyze sample-data/tiktok-overview.csv` |
| `/analyze --refresh` | วิเคราะห์ข้อมูล + ค้นหา intel ใหม่ทั้งหมด (ไม่ใช้ cache เดิม) |
| `/compare` | เปรียบเทียบ platform performance ย้อนหลัง สัปดาห์/เดือน/ปี |

### ข่าวกรองตลาดและคู่แข่ง

| คำสั่ง | ทำอะไร |
|---|---|
| `/intel` | ดึงข่าว/คู่แข่งล่าสุด (ใช้ข้อมูลเดิมถ้ามีอยู่แล้ว ประหยัด token) |
| `/intel --refresh` | บังคับค้นหาใหม่ทั้งหมด ไม่ใช้ cache |
| `/intel TOPIC CITY` | ค้นหาเจาะจง เช่น `/intel จัดฟัน สกลนคร` |
| `/intel-deep` | วิเคราะห์คู่แข่งเชิงลึก 5 มิติ + บันทึก history + push GitHub |

### สรุปและวางแผน

| คำสั่ง | ทำอะไร |
|---|---|
| `/weekly` | สร้าง weekly report — performance สัปดาห์นี้ vs ก่อน + แนะนำสัปดาห์หน้า |
| `/weekly --show` | แสดง report ล่าสุดโดยไม่สร้างใหม่ |
| `/content-ideas` | สร้างแผน content 7 วัน พร้อม caption ไทย + hashtags + เวลาโพสต์ |
| `/content-ideas จัดฟัน` | เน้น content เรื่องจัดฟัน |
| `/content-ideas โปรโมชั่น` | เน้น content โปรโมชั่น |
| `/content-ideas --show` | แสดงแผนล่าสุดโดยไม่สร้างใหม่ |

---

### ติดตามคู่แข่ง Before/After

| คำสั่ง | ทำอะไร |
|---|---|
| `/comp-track --snapshot` | ค้นหาและบันทึกสถานะคู่แข่งทุกราย ณ วันนี้ |
| `/comp-track --snapshot หมอจั่นเจา` | บันทึกเฉพาะคู่แข่งที่ระบุ |
| `/comp-track --compare week` | เปรียบเทียบสัปดาห์นี้ vs สัปดาห์ก่อน |
| `/comp-track --compare month` | เปรียบเทียบเดือนนี้ vs เดือนก่อน |
| `/comp-track --compare year` | เปรียบเทียบปีนี้ vs ปีก่อน |
| `/comp-track --list` | ดู snapshots ทั้งหมดที่เก็บไว้ |
| `/comp-track --report` | สร้าง report รวมทุก competitor บันทึกไฟล์ |
| `/comp-track` (ไม่มี args) | แสดง comparison สัปดาห์ล่าสุดของทุกคู่แข่ง |

**ข้อมูลที่ track ต่อคู่แข่ง:**
- Followers (Facebook / TikTok / Instagram)
- จำนวน posts/videos + Content Themes
- โปรโมชันที่ active — เห็น added / removed / kept เทียบช่วงก่อน
- Activity Level + Primary Platform
- Top content ที่ปัง

---

## ตั้งเป้าหมาย KPI รายเดือน

แก้ไขไฟล์ `data/goals.json` โดยตรง หรือใช้ CLI:

```bash
# ตั้งเป้า reach TikTok ที่ 200,000
python src/goal_tracker.py set tiktok total_reach 200000

# ตั้งเป้า engagement rate Facebook
python src/goal_tracker.py set facebook avg_engagement_rate 1.5

# ตั้งเป้า followers ใหม่ Instagram
python src/goal_tracker.py set instagram total_new_followers 150

# ดูความก้าวหน้า KPI ทุก platform ใน terminal
python src/goal_tracker.py show
```

**KPI ที่ track ได้:** `total_reach` | `avg_engagement_rate` | `total_new_followers`
**ผลลัพธ์:** แสดงใน dashboard หน้าแรก การ์ด "🎯 เป้าหมายเดือนนี้" พร้อม progress bar

---

## บันทึก Content Log (สำหรับ Content Category Analyzer)

หลังโพสต์ content แต่ละชิ้น บันทึกผลลัพธ์เพื่อวิเคราะห์ว่า content ประเภทไหน perform ดีที่สุด:

```bash
python src/content_category_analyzer.py log [platform] [category] "ชื่อ post" --reach [จำนวน] --engagement [จำนวน]
```

**ตัวอย่าง:**
```bash
python src/content_category_analyzer.py log tiktok education "วิธีแปรงฟันที่ถูกต้อง" --reach 5200 --engagement 312
python src/content_category_analyzer.py log facebook before_after "จัดฟัน 6 เดือน เปลี่ยนไปแค่ไหน" --reach 2100 --engagement 198
python src/content_category_analyzer.py log instagram promotion "โปรฟอกสีฟัน 2 คนราคาพิเศษ" --reach 950 --engagement 67

# ดูสรุป category performance ใน terminal
python src/content_category_analyzer.py show
```

**Categories ที่ใช้ได้:**

| Category | ความหมาย |
|---|---|
| `education` | ความรู้ทันตกรรม (วิธีแปรงฟัน, อาหารที่ดีต่อฟัน ฯลฯ) |
| `before_after` | ก่อน-หลังรักษา (จัดฟัน, ฟอกสีฟัน, รากเทียม) |
| `faq` | ตอบคำถามที่พบบ่อย (จัดฟันเจ็บไหม, ราคาเท่าไหร่) |
| `promotion` | โปรโมชั่น, ราคาพิเศษ, แพ็กเกจ |
| `behind_scenes` | เบื้องหลังคลินิก, ทีมหมอ, เครื่องมือ |
| `local` | Content ท้องถิ่นสกลนคร |

**ผลลัพธ์:** dashboard หน้าแรก การ์ด "📊 Content Performance" แท็บ "หมวด Content" จะแสดง average reach + engagement rate ต่อ category เรียงลำดับ

---

## Workflow ประจำสัปดาห์ (แนะนำ)

```
── วันจันทร์ (เริ่มสัปดาห์) ──────────────────────────
1. พิมพ์ /weekly               ← สรุปสัปดาห์ที่แล้ว + แนะนำสัปดาห์นี้
2. พิมพ์ /content-ideas        ← ได้แผน content 7 วัน พร้อม caption

── ระหว่างสัปดาห์ ─────────────────────────────────────
3. Export CSV จาก TikTok / Facebook / Instagram
4. วางไฟล์ใน sample-data/
5. พิมพ์ /analyze              ← วิเคราะห์ performance ของเรา

── วันศุกร์/เสาร์ (ปิดสัปดาห์) ────────────────────────
6. บันทึก content log ที่โพสต์ในสัปดาห์นี้:
   python src/content_category_analyzer.py log tiktok education "ชื่อ post" --reach 5000 --engagement 300
7. พิมพ์ /comp-track --snapshot    ← บันทึกสถานะคู่แข่งสัปดาห์นี้
8. ดับเบิลคลิก update-dashboard.bat
   → inject ข้อมูลใหม่ทั้งหมด + push ขึ้น GitHub Pages ภายใน 2 นาที
```

**สัปดาห์หน้า:** ทำซ้ำ แล้วพิมพ์ `/comp-track --compare week` เพื่อดูว่าคู่แข่งเปลี่ยนอะไร

---

## การเริ่มต้นระบบ Competitor Tracking ครั้งแรก

ถ้ายังไม่เคย snapshot เลย ทำแค่นี้:

```
1. พิมพ์ /comp-track --snapshot
   → agent จะค้นหาข้อมูลจาก web ทุกราย
   → บันทึกลง data/competitors/{ชื่อ}/{YYYY-WXX}.json

2. สัปดาห์หน้าทำซ้ำ แล้วพิมพ์:
   /comp-track --compare week
   → เห็น before/after ทันที
```

---

## Automated Schedule (ทำงานอัตโนมัติ ไม่ต้องทำเอง)

| วัน | เวลา | งาน |
|---|---|---|
| ทุกอาทิตย์ | 9:00 น. | ค้นข่าว + คู่แข่ง + ราคา + events → push GitHub |
| ทุกจันทร์ | 9:00 น. | วิเคราะห์เชิงลึกโดยใช้ข้อมูลเมื่อวาน → push GitHub |

จัดการ routines: **https://claude.ai/code/routines**

---

## อัปเดต Dashboard ขึ้น Web

### วิธีที่ 1: ดับเบิลคลิกไฟล์ (ง่ายสุด)
```
ดับเบิลคลิก update-dashboard.bat
```

### วิธีที่ 2: พิมพ์ใน Claude Code
```
git add .
git commit -m "Update"
git push
```

รอ 1-2 นาที แล้ว refresh browser

---

## ไฟล์สำคัญ

| ไฟล์/Folder | หน้าที่ |
|---|---|
| `CLAUDE.md` | ข้อมูลธุรกิจ KPIs context ของคลินิก (แก้ถ้าข้อมูลเปลี่ยน) |
| `sample-data/` | วาง CSV ใหม่ที่นี่ก่อนรัน /analyze |
| `data/schema.json` | mapping columns ของแต่ละ platform |
| `data/history/` | JSON snapshots ย้อนหลัง ของเราเอง (อย่าลบ) |
| `data/competitors/` | JSON snapshots คู่แข่งรายสัปดาห์ (ระบบใหม่) |
| `dashboard/` | HTML dashboards ล่าสุด (local preview) |
| `reports/` | รายงาน intel, comparison, comp-track ทั้งหมด |
| `src/competitor_tracker.py` | Python engine ติดตามคู่แข่ง + inject COMP_TRACK เข้า dashboard |
| `src/goal_tracker.py` | ติดตาม KPI vs เป้าหมายรายเดือน + inject GOAL_DATA |
| `src/monthly_trend.py` | แนวโน้ม Reach/Engagement รายสัปดาห์-รายเดือน + inject MONTHLY_TREND |
| `src/content_category_analyzer.py` | วิเคราะห์ content format/category performance + inject CONTENT_PERF |
| `src/posting_time_analyzer.py` | วิเคราะห์วันดีที่สุดในการโพสต์ + inject BEST_DAYS |
| `src/update_logger.py` | บันทึกประวัติการอัปเดตแต่ละ section + inject UPDATE_LOG |
| `data/goals.json` | เป้าหมาย KPI รายเดือน (แก้ตรงหรือผ่าน goal_tracker.py set) |
| `data/content-log.json` | บันทึก post รายหมวด (เพิ่มผ่าน content_category_analyzer.py log) |
| `data/dental-calendar.json` | ปฏิทินทันตกรรม: ธีมรายเดือน, วันสำคัญ, hashtags |
| `.claude/agents/comp-track-agent.md` | Agent ค้นหา + บันทึก snapshot คู่แข่ง |
| `.claude/agents/weekly-agent.md` | Agent สร้าง weekly summary report |
| `.claude/agents/content-ideas-agent.md` | Agent สร้างแผน content 7 วัน |
| `.claude/agents/intel-agent.md` | Agent ค้นหาข่าวตลาด |
| `docs/intelligence-brief.md` | ฐานข้อมูลคู่แข่งหลัก |
| `update-dashboard.bat` | ดับเบิลคลิกเพื่อ regenerate + inject + push GitHub Pages |

---

## Dashboard Sections

| หน้า | เนื้อหา |
|---|---|
| ภาพรวม (Home) | KPI cards + Platform Comparison + 4 doughnut charts |
| ↳ Best Day to Post | bar chart วันที่ควรโพสต์ต่อ platform (auto จาก history) |
| ↳ Competitor Tracker | สถานะคู่แข่งล่าสุด — activity, theme, โปรโมชั่น |
| ↳ เป้าหมายเดือนนี้ | KPI progress bar (actual vs target) ทุก platform |
| ↳ แนวโน้ม Reach | line chart รายสัปดาห์/รายเดือน ต่อ platform (Reach + Engagement toggle) |
| ↳ Content Performance | Facebook format breakdown (Reels/Image/Story) + Category log ranking |
| TikTok / Facebook / Instagram | line chart + engagement breakdown + data table รายวัน |
| ข่าวกรอง | คู่แข่ง + ความรู้ + Events + อุปกรณ์ (card feed) |
| ราคาทำฟัน | ตารางราคาแยกตามประเภทบริการ + Social Trend |
| เชิงลึก | วิเคราะห์คู่แข่ง 5 มิติ + Timeline การเปลี่ยนแปลง |
| นำเข้าข้อมูล | import CSV ผ่าน browser โดยตรง |

---

## GitHub Repository
**https://github.com/pengtangcafe-hash/my-social-dashboard**

---

## ถ้า Dashboard ว่าง ไม่แสดงข้อมูล

1. กด Ctrl+Shift+R (force refresh)
2. ถ้ายังว่าง พิมพ์ใน Claude Code:
   ```
   python src/generate_dashboard.py
   copy dashboard\index.html docs\index.html
   git add docs/index.html && git commit -m "Fix" && git push
   ```

---

## ถ้า Context เต็ม (Claude Code ช้าหรือแปลก)

เปิด Claude Code tab ใหม่ที่ folder `my-social-project` แล้วทำงานต่อได้เลย ข้อมูลทั้งหมดยังอยู่ในไฟล์ครบ
