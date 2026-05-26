# Social Analytics App

## โปรเจกต์นี้คืออะไร
เครื่องมือวิเคราะห์ข้อมูล Social Media สำหรับคลินิกทันตกรรม จังหวัดสกลนคร
สร้างด้วย Claude Code เพื่อนำเข้าข้อมูลจาก TikTok, Facebook, Instagram
แล้ววิเคราะห์ performance, เปรียบเทียบ platform และติดตามคู่แข่ง

## Business Context
- ธุรกิจ: คลินิกทันตกรรม จังหวัดสกลนคร
- เป้าหมาย: วิเคราะห์ social media เพื่อปรับกลยุทธ์การตลาด
- Platforms หลัก: TikTok, Facebook, Instagram
- พื้นที่ที่สนใจ: จังหวัดสกลนคร และจังหวัดใกล้เคียง
- คู่แข่ง: คลินิกทันตกรรมอื่นๆ ในสกลนคร

## KPIs ที่สำคัญที่สุด
1. Follower Growth Rate (%) — ติดตามการเติบโตรายสัปดาห์/รายเดือน
2. Engagement Rate (%) = (Likes + Comments + Shares) / Views * 100
3. Video/Post View Count — ดูว่า content ไหน perform ดี
4. Reach per Post — เฉลี่ยคนที่เห็นต่อโพสต์
5. Best Posting Time — ช่วงเวลาที่ engagement สูงสุด

## Data Location
- sample-data/TikTok/ — ข้อมูล TikTok
- sample-data/Facebook/ — ข้อมูล Facebook
- sample-data/Instagram/ — ข้อมูล Instagram
- data/imports/ — ไฟล์ CSV/XLS ที่นำเข้าจริง
- data/history/ — ข้อมูล normalized เก็บย้อนหลัง
- data/schema.json — mapping ชื่อ column จากแต่ละ platform

## Report Format
ทุก report ที่ /analyze สร้างต้องมี sections เหล่านี้เสมอ:
1. Executive Summary (3-5 bullet points ที่สำคัญที่สุด)
2. Key Metrics Table (ตาราง metrics หลัก)
3. Top Performing Content (ถ้ามีข้อมูล content)
4. Audience Insights (ถ้ามีข้อมูล demographics)
5. Recommendations (2-3 ข้อที่ทำได้จริง)

## Commands
- /analyze FILE — วิเคราะห์ไฟล์ CSV จาก social platform
- /intel [topic] [city] — ค้นหาข้อมูลคู่แข่ง, hashtags, trends, events, equipment
- /compare — เปรียบเทียบ platform performance ของเราเอง
- /comp-track — ติดตามและเปรียบเทียบคู่แข่ง before/after
  - `/comp-track --snapshot` — บันทึก snapshot คู่แข่งทุกราย (ค้นหาจาก web)
  - `/comp-track --compare week` — เปรียบเทียบสัปดาห์นี้ vs สัปดาห์ก่อน
  - `/comp-track --compare month` — เปรียบเทียบเดือนนี้ vs เดือนก่อน
  - `/comp-track --compare year` — เปรียบเทียบปีนี้ vs ปีก่อน
  - `/comp-track --list` — ดู snapshots ที่มีทั้งหมด
  - `/comp-track --report` — สร้าง report รวมบันทึกไฟล์

## Tech Stack
- Python 3 + pandas สำหรับ data processing
- HTML + Chart.js สำหรับ dashboard visualization
- JSON สำหรับ historical data storage

## Intelligence Module

### คู่แข่งหลักที่ติดตาม (สกลนคร)
1. **หมอจั่นเจา** — FB: JunjaoDentalClinic | TikTok: @dr.piyawat5 | Website: junjaodentalclinic.com | 2 สาขา + มุกดาหาร
2. **Dio Dental** — FB: DioDentalClinicEsan, diodentalsakhon | TikTok: @diodental | Chain 21+ สาขา, ISO 9001, รับบัตรทอง
3. **Toothmate** — FB: ToothmateDC | IG: @toothmate_dc | หมอจบมหิดล+จุฬา | มี Price list บนเว็บ
4. **Dental Park** — FB: Dentalpark2020 | TikTok: @dental.park.clinic | "แม่แฝดหมอจัดฟัน" | ใช้ภาษาอีสาน

### Intel Reports Location
- `reports/intel-*.md` — รายงานคู่แข่งและตลาด
- `reports/intel-20260518-DentalParkClinic.md` — Deep-dive Dental Park
- `reports/intel-20260518-หมอจั่นเจา.md` — Deep-dive หมอจั่นเจา

### Intelligence Context (อ่านก่อนสร้าง Intel Dashboard)
→ `docs/intelligence-brief.md` — Framework, ข้อมูลคู่แข่งครบ 4 ราย, hashtags, market gaps, UI requirements

### Intel Agent
- `.claude/agents/intel-agent.md` — ค้นหาข้อมูลแล้วส่งคืน JSON structure
- JSON fields: `category`, `pricing`, `strengths`, `social_trend`, `promotions`
- categories: `competitor` | `dental_knowledge` | `news_events` | `equipment`

### Competitor Tracking Agent (ใหม่)
- `.claude/agents/comp-track-agent.md` — ค้นหา + บันทึก + เปรียบเทียบ snapshot คู่แข่ง
- Storage: `data/competitors/{ชื่อ}/{YYYY-WXX}.json` (weekly) หรือ `{YYYY-MM}.json` (monthly)
- Python module: `src/competitor_tracker.py` — save/load/compare/report
- Command: `/comp-track` — ดู, snapshot, เปรียบเทียบ week/month/year
- Tracks: promotions, content themes, platform activity, followers, top content
