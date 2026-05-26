# คู่มือการใช้งาน Social Analytics Dashboard
**คลินิกทันตกรรม สกลนคร**
อัปเดตล่าสุด: 27 พฤษภาคม 2569

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

### ติดตามคู่แข่ง Before/After (ใหม่)

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

## Workflow ประจำสัปดาห์ (แนะนำ)

```
1. Export CSV จาก TikTok / Facebook / Instagram
2. วางไฟล์ใน sample-data/
3. พิมพ์ /analyze          ← วิเคราะห์ของเรา
4. พิมพ์ /comp-track --snapshot   ← บันทึกสถานะคู่แข่งสัปดาห์นี้
5. พิมพ์ /intel            ← อัปเดตข่าว (ถ้าต้องการ)
6. ดับเบิลคลิก update-dashboard.bat
   → dashboard บน GitHub Pages อัปเดตภายใน 2 นาที
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
| `src/competitor_tracker.py` | Python engine ของระบบติดตามคู่แข่ง |
| `.claude/agents/comp-track-agent.md` | Agent ค้นหา + บันทึก snapshot |
| `.claude/agents/intel-agent.md` | Agent ค้นหาข่าวตลาด |
| `docs/intelligence-brief.md` | ฐานข้อมูลคู่แข่งหลัก |

---

## Dashboard Sections

| หน้า | เนื้อหา |
|---|---|
| ภาพรวม | KPI cards + Platform Comparison + 4 doughnut charts |
| TikTok / Facebook / Instagram | line chart + engagement breakdown + data table |
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
