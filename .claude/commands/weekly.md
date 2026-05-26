สร้าง Weekly Summary Report — สรุปสัปดาห์ที่ผ่านมา + แผนสัปดาห์ถัดไป

---

## Parse Arguments

| Argument | ความหมาย |
|----------|----------|
| (ไม่มี) | สร้าง report สัปดาห์ปัจจุบัน |
| `--week YYYY-WXX` | สร้าง report สำหรับสัปดาห์ที่ระบุ |
| `--show` | แสดง report ล่าสุดใน chat (ไม่สร้างใหม่) |

---

## ขั้นตอนการทำงาน

### 1. กำหนด Week Label

```python
from datetime import date
d = date.today()
iso = d.isocalendar()
week_label = f"{iso[0]}-W{iso[1]:02d}"
# ช่วงวันของสัปดาห์นี้ (Mon–Sun)
```

### 2. ตรวจสอบ Report เดิม (ถ้า --show)

ถ้ามี argument `--show`:
- หาไฟล์ล่าสุดใน `reports/weekly-*.md`
- แสดงเนื้อหาใน chat
- จบการทำงาน

### 3. เรียก weekly-agent

ส่งให้ agent:
- `week_label`: สัปดาห์ปัจจุบัน เช่น "2026-W22"
- `mode`: "full" (วิเคราะห์ครบทุก section)

Agent จะ:
- โหลด history data ของแต่ละ platform
- เปรียบเทียบ 7 วันนี้ vs 7 วันก่อน
- โหลด competitor snapshots ที่มี
- สร้าง Markdown report พร้อม recommendations

### 4. บันทึก Report

บันทึก report ที่ได้ลงไฟล์:
```
reports/weekly-{YYYYMMDD}.md
```
(ใช้วันที่วันนี้)

ถ้ามีไฟล์ชื่อเดิมให้ overwrite

### 5. อัปเดต Update Log

```bash
python src/update_logger.py log intel
python src/update_logger.py inject dashboard/index.html
```

(weekly report ถือว่า refresh intel section ด้วย)

### 6. สรุปใน Chat

แสดงสรุปในรูปแบบนี้:

```
## 📊 Weekly Report — {week_label} พร้อมแล้ว!

**Highlights:**
• [highlight 1]
• [highlight 2]  
• [highlight 3]

**Platform ที่ดีที่สุดสัปดาห์นี้:** {platform}

**แนะนำสัปดาห์หน้า:**
1. [recommendation 1]
2. [recommendation 2]

📁 รายงานเต็ม: reports/weekly-{YYYYMMDD}.md
```

---

## หมายเหตุ

- ถ้าไม่มีข้อมูล history เลย: แจ้งผู้ใช้ว่า "ยังไม่มีข้อมูล history — ใช้ `/analyze` เพื่อนำเข้าข้อมูลก่อน"
- ถ้าไม่มีข้อมูลคู่แข่ง: ข้าม section competitor และแจ้งว่า "ใช้ `/comp-track --snapshot` เพื่อเพิ่มข้อมูลคู่แข่ง"
- Weekly report ควรสร้างทุกสัปดาห์ (เช่น ทุกวันจันทร์เช้า)
