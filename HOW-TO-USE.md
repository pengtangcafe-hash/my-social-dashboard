# คู่มือการใช้งาน Social Analytics Dashboard
**คลินิกทันตกรรม สกลนคร**
อัปเดตล่าสุด: 19 พฤษภาคม 2569

---

## Dashboard URL
**https://pengtangcafe-hash.github.io/my-social-dashboard/**

---

## คำสั่งหลัก (พิมพ์ใน Window 2: my-social-project)

### วิเคราะห์ข้อมูล Social Media

| คำสั่ง | ทำอะไร |
|---|---|
| `/analyze` | วิเคราะห์ทุก platform จาก sample-data/ + อัปเดต dashboard |
| `/analyze FILE` | วิเคราะห์ไฟล์เฉพาะ เช่น `/analyze sample-data/tiktok-overview.csv` |
| `/analyze --refresh` | วิเคราะห์ข้อมูล + ค้นหา intel ใหม่ทั้งหมด (ไม่ใช้ cache เดิม) |
| `/compare` | เปรียบเทียบข้อมูลย้อนหลัง สัปดาห์/เดือน/ปี |

### ข่าวกรองและวิเคราะห์คู่แข่ง

| คำสั่ง | ทำอะไร |
|---|---|
| `/intel` | ดึงข่าว/คู่แข่งล่าสุด (ใช้ข้อมูลเดิมถ้ามีอยู่แล้ว ประหยัด token) |
| `/intel --refresh` | บังคับค้นหาใหม่ทั้งหมด ไม่ใช้ cache |
| `/intel TOPIC CITY` | ค้นหาเจาะจง เช่น `/intel จัดฟัน สกลนคร` |
| `/intel-deep` | วิเคราะห์คู่แข่งเชิงลึก 5 มิติ + บันทึก history + push GitHub |

---

## Workflow ประจำสัปดาห์ (Manual)

```
1. Export CSV จาก TikTok / Facebook / Instagram
2. วางไฟล์ใน sample-data/
3. พิมพ์ /analyze
4. พิมพ์ /intel (ถ้าอยากอัปเดตข่าว)
5. ดับเบิลคลิก update-dashboard.bat
   → dashboard บน GitHub Pages อัปเดตอัตโนมัติภายใน 2 นาที
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

### วิธีที่ 2: พิมพ์ใน Window 2
```
git add docs/index.html
git commit -m "Update dashboard"
git push
```

รอ 1-2 นาที แล้ว refresh browser

---

## ไฟล์สำคัญ

| ไฟล์/Folder | หน้าที่ |
|---|---|
| `CLAUDE.md` | ข้อมูลธุรกิจ KPIs context ของคลินิก (แก้ถ้าข้อมูลเปลี่ยน) |
| `sample-data/` | วาง CSV ใหม่ที่นี่ก่อนรัน /analyze |
| `data/schema.json` | mapping columns ของแต่ละ platform (เพิ่ม platform ใหม่ที่นี่) |
| `data/history/` | JSON snapshots ย้อนหลัง (อย่าลบ) |
| `data/competitor-history/` | snapshots คู่แข่งรายสัปดาห์ |
| `data/intel-cache/` | cache ข่าวกรองรายสัปดาห์ |
| `dashboard/index.html` | dashboard ล่าสุด (local) |
| `docs/index.html` | ไฟล์ที่แสดงบน GitHub Pages |
| `reports/` | รายงาน intel และ competitor changes |
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
2. ถ้ายังว่าง พิมพ์ใน Window 2:
   ```
   python src/generate_dashboard.py
   copy dashboard\index.html docs\index.html
   git add docs/index.html && git commit -m "Fix" && git push
   ```

---

## ถ้า Context เต็ม (Window 2 ช้าหรือแปลก)

เปิด Claude Code tab ใหม่ที่ folder `my-social-project` แล้วทำงานต่อได้เลย ข้อมูลทั้งหมดยังอยู่ในไฟล์ครบ
