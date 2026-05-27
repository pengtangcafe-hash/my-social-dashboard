# Social Analytics App — คลินิกทันตกรรม สกลนคร

## โปรเจกต์นี้คืออะไร
เครื่องมือวิเคราะห์ Social Media + ระบบ Advertising Intelligence สำหรับคลินิกทันตกรรม จังหวัดสกลนคร
สร้างด้วย Claude Code — วิเคราะห์ performance, ติดตามคู่แข่ง, วางกลยุทธ์โฆษณา, สร้าง content

## Business Context
- ธุรกิจ: คลินิกทันตกรรม จังหวัดสกลนคร
- เป้าหมาย: วิเคราะห์ social media + ยิง Ads อย่างแม่นยำ + ตีตลาด
- Platforms หลัก: TikTok, Facebook, Instagram
- พื้นที่: จังหวัดสกลนคร และจังหวัดใกล้เคียง
- คู่แข่ง: หมอจั่นเจา, Dio Dental, Toothmate, Dental Park

## Dashboard (GitHub Pages)
- URL: `docs/index.html` → GitHub Pages
- รัน `update-dashboard.bat` เพื่อ regenerate + inject + push
- Views หลัก: Home | TikTok | Facebook | Instagram | Intel | Pricing | Competitor | ⚡ Ad Campaigns

### หน้า ⚡ Ad Campaigns ประกอบด้วย:
1. Hero KPI banner (Spent / Reach / Leads / CPL)
2. Campaign cards (budget burn bar + KPI pills)
3. Platform summary grid
4. 📚 ROI/ROAS Education card (สูตร + ตาราง daily/monthly + funnel)
5. 🔢 Metrics card (CPR · CPL · CTR · Reach · Lead + tips + quick reference)
6. 📡 Content Radar card (competitor content → our parallel ideas)
7. Tips banner

---

## KPIs สำคัญ (Organic + Paid)
| Metric | ความหมาย | ดี | เยี่ยม |
|--------|---------|-----|-------|
| Reach | คนที่เห็น | 10K+/campaign | 50K+ |
| Lead | คนสนใจ | 10+/3,000฿ | 20+ |
| CTR | % คลิก | >1.5% | >3% |
| CPR | ต้นทุน/reach | <0.30฿ | <0.15฿ |
| CPL | ต้นทุน/lead | <300฿ | <150฿ |
| ROAS | revenue/spend | >5x | >20x |

---

## Commands ทั้งหมด

### 📊 Analytics
- `/analyze FILE` — วิเคราะห์ CSV จาก social platform
- `/compare` — เปรียบเทียบ platform performance ของเรา
- `/weekly` — weekly report + แนะนำสัปดาห์ถัดไป | `/weekly --show`

### 🕵️ Intelligence
- `/intel [topic] [city]` — ค้นหาข้อมูลคู่แข่ง, hashtags, trends
- `/comp-track --snapshot` — บันทึก snapshot คู่แข่งทุกราย
- `/comp-track --compare week/month/year` — เปรียบเทียบ
- `/comp-track --list | --report`

### 💡 Content
- `/content-ideas [topic] [--platform tiktok] [--show]` — แผน 7 วัน + caption + hashtags
- `/content-radar` — วิเคราะห์คู่แข่งกำลังโพสต์อะไร → สร้าง parallel content ของเรา
  - `/content-radar DentalPark` — เฉพาะคู่แข่งนั้น
  - `/content-radar tiktok` — เฉพาะ platform
  - `/content-radar จัดฟัน` — เฉพาะบริการ

### ⚡ Advertising
- `/ad-strategy` — กลยุทธ์โฆษณาฉบับเต็ม (competitor gap + organic + paid + 30-day plan)
- `/ad-brief [บริการ] [platform]` — Creative Brief ละเอียดสำหรับ 1 campaign
- `/ad-copy [บริการ] [platform]` — Hook + Copy ≥3 แบบ พร้อม reel script
- `/ad-track [subcommand]` — CLI wrapper สำหรับ ad_tracker.py
- `/ad-report [filter]` — ROI report ทุก campaign | `month | facebook | จัดฟัน | vs-organic`

---

## Python Scripts (src/)

| Script | หน้าที่ | CLI |
|--------|---------|-----|
| `generate_dashboard.py` | สร้าง dashboard HTML จาก CSV | `python src/generate_dashboard.py sample-data/` |
| `posting_time_analyzer.py` | Best day to post (6 months) | `inject dashboard/index.html` |
| `update_logger.py` | บันทึก update history | `inject dashboard/index.html` |
| `competitor_tracker.py` | save/load/compare competitor snapshots | `inject dashboard/index.html` |
| `goal_tracker.py` | ตั้ง + ติดตาม KPI รายเดือน | `show | set tiktok total_reach 200000 | inject` |
| `monthly_trend.py` | แนวโน้ม reach/engagement รายสัปดาห์/เดือน | `show | inject` |
| `content_category_analyzer.py` | วิเคราะห์ format FB + category ของเรา | `show | log | inject` |
| `ad_tracker.py` | บันทึก + คำนวณ KPI ทุก campaign | `show | log | update | inject` |
| `content_radar.py` | Competitor content → parallel ideas | `generate | show | inject` |

---

## Data Files

| ไฟล์ | เนื้อหา |
|------|---------|
| `data/ad-campaigns.json` | Ad campaigns ทั้งหมด (camp-001, camp-002 …) |
| `data/content-log.json` | Manual post log (platform, category, reach, engagement) |
| `data/content-radar.json` | Radar output: 10 โอกาส content จาก 4 คู่แข่ง |
| `data/goals.json` | KPI เป้าหมายรายเดือนต่อ platform |
| `data/competitors/{ชื่อ}/{YYYY-WXX}.json` | Competitor snapshots รายสัปดาห์ |
| `data/dental-calendar.json` | ธีมรายเดือน, วันสำคัญ, hashtag sets |
| `data/history/` | Normalized daily data จากทุก platform |
| `data/schema.json` | Column mapping ต่อ platform |

---

## Agents

| Agent | ไฟล์ | ใช้กับ command |
|-------|------|--------------|
| Intel Agent | `.claude/agents/intel-agent.md` | `/intel` |
| Comp Track Agent | `.claude/agents/comp-track-agent.md` | `/comp-track` |
| Weekly Agent | `.claude/agents/weekly-agent.md` | `/weekly` |
| Content Ideas Agent | `.claude/agents/content-ideas-agent.md` | `/content-ideas` |
| **Advertising Agent** | `.claude/agents/advertising-agent.md` | `/ad-*` + `/content-radar` |

### Advertising Agent — ความรู้หลัก
- รู้จักคู่แข่ง 4 ราย + จุดแข็ง/อ่อน + content strategy ของแต่ละราย
- KPI targets: CPR<0.30฿, CPL<150฿, CTR>1.5%, ROAS>3x
- Budget framework: Starter 3-5K/mo, Growth 8-15K/mo, Scale 20K+
- Hook formula: Pain + Local (สกลนคร) + Solution + Proof

---

## Intelligence Module

### คู่แข่งหลักที่ติดตาม (สกลนคร)
1. **หมอจั่นเจา** — FB: JunjaoDentalClinic | TikTok: @dr.piyawat5 | Website: junjaodentalclinic.com | 2 สาขา + มุกดาหาร | content: denture edu + pricing + before/after
2. **Dio Dental** — FB: DioDentalClinicEsan, diodentalsakhon | TikTok: @diodental | Chain 21+ สาขา, ISO 9001, รับบัตรทอง | FB 17K followers | content: clinic tour + brand doctor + before/after
3. **Toothmate** — FB: ToothmateDC | IG: @toothmate_dc (111 followers) | หมอจบมหิดล+จุฬา | Price list บนเว็บ | content: composite veneer + team intro
4. **Dental Park** — FB: Dentalpark2020 | TikTok: @dental.park.clinic | "แม่แฝดหมอจัดฟัน" | ใช้ภาษาอีสาน | content: before/after + clear aligner + adult ortho | **ไม่มี Instagram**

### Market Gaps (สำคัญมาก)
- **Longevity Dental** — ไม่มีใครในสกลนครทำ content เรื่องฟัน + อายุยืน (เทรนด์ #1 ปี 2026)
- **Instagram** — Dental Park = 0, DENTAFe = 10 followers → IG Reels อีสานคือ Blue Ocean
- **#ฟอกสีฟันสกลนคร** — hashtag ว่างเปล่า ยังไม่มีใคร claim
- **Price Transparency** — มีแค่ Dio + Toothmate ที่ราคาชัดเจน

### Reports
- `reports/intel-*.md` — Intel reports
- `reports/ad-strategy-20260527.md` — กลยุทธ์โฆษณาฉบับเต็ม (11 sections)
- `reports/content-radar-*.md` — Content radar reports

---

## Active Ad Campaigns (ข้อมูล ณ 27 พ.ค. 2569)
| ID | Platform | บริการ | งบ | Leads | CPR | CPL | ROAS | Status |
|----|---------|--------|-----|-------|-----|-----|------|--------|
| camp-001 | Facebook | จัดฟัน | 3,000฿ | 12 | 0.15฿ | 229฿ | ~39x | Active |
| camp-002 | TikTok | ฟอกสีฟัน | 1,500฿ | 0 | — | — | — | Active |

อัปเดตผลลัพธ์: `python src/ad_tracker.py update camp-001 --reach X --leads X --spend X`

---

## Content Radar — 4 กลยุทธ์ (อัปเดต W22-2026)
- ⚔️ **Counter**: ตอบโต้โดยตรง (Clear Aligner comparison, Price transparency)
- 🪞 **Mirror**: เรื่องเดิม มุมต่าง (Adult ortho → จัดฟันใสไม่เห็นเหล็ก)
- 👑 **Own It**: Claim พื้นที่ว่าง (FAQ series, ฟอกสีฟัน, Longevity Dental)
- 🚀 **Expand**: ขยายหัวข้อที่คู่แข่งทำยังไม่ลึก (ฟันปลอม 3 แบบ, Veneer comparison)

---

## Tech Stack
- Python 3 + pandas สำหรับ data processing
- HTML + Chart.js สำหรับ dashboard visualization
- JSON สำหรับ historical data storage
- GitHub Pages สำหรับ deploy dashboard

## Security
- ❌ อย่า commit `.claude/settings.local.json` — มี hardcoded path ของเครื่อง
- ✅ ไฟล์ทั้งหมดใน `src/`, `data/`, `reports/`, `.claude/commands/`, `.claude/agents/` commit ได้
