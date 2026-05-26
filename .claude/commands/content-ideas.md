สร้างแผน Content Ideas 7 วัน สำหรับคลินิกทันตกรรมสกลนคร

---

## Parse Arguments

| Argument | ความหมาย |
|----------|----------|
| (ไม่มี) | สร้างแผน 7 วันทั่วไป วิเคราะห์จาก context ปัจจุบัน |
| `[topic]` | เน้น content ในหมวดที่ระบุ เช่น "จัดฟัน", "ฟอกสีฟัน", "โปรโมชั่น", "ความรู้" |
| `--platform tiktok/facebook/instagram` | สร้างแผนเฉพาะ platform ที่ระบุ |
| `--show` | แสดง content plan ล่าสุดจาก reports/ |

**ตัวอย่าง:**
- `/content-ideas` → แผนทั่วไป 7 วัน
- `/content-ideas จัดฟัน` → เน้น content เรื่องจัดฟัน
- `/content-ideas โปรโมชั่น` → เน้น content โปรโมชั่น
- `/content-ideas --platform tiktok` → แผนเฉพาะ TikTok

---

## ขั้นตอนการทำงาน

### 1. ตรวจสอบ --show

ถ้ามี `--show`:
- หาไฟล์ล่าสุดใน `reports/content-ideas-*.md`
- แสดงเนื้อหาใน chat
- จบการทำงาน

### 2. กำหนดช่วงเวลา

```python
from datetime import date, timedelta
today = date.today()
# หาวันจันทร์ถัดไป (หรือวันจันทร์นี้ถ้าวันนี้คือจันทร์)
days_ahead = (7 - today.weekday()) % 7
if days_ahead == 0:
    days_ahead = 7
start_date = today + timedelta(days=days_ahead)
end_date = start_date + timedelta(days=6)
```

### 3. อ่าน Context

อ่านไฟล์เหล่านี้เพื่อเตรียมข้อมูล:
- `data/dental-calendar.json` — ธีมเดือน, วันสำคัญ, hashtags
- `data/history/` — ดูว่า content ประเภทไหน perform ดีล่าสุด
- `data/competitors/` — ดูว่าคู่แข่งทำ content อะไรอยู่ (ถ้ามี)
- reports/intel-*.md ล่าสุด — trends และ hashtags ที่กำลังมา

### 4. เรียก content-ideas-agent

ส่งให้ agent:
- `topic`: topic ที่ผู้ใช้ระบุ (หรือ null)
- `platform`: platform ที่เลือก (หรือ "all")
- `start_date`: วันเริ่มต้นสัปดาห์
- `context_files`: รายชื่อไฟล์ที่ต้องอ่าน

Agent จะสร้าง Markdown report พร้อม:
- แผน 7 วัน (หัวข้อ, caption ไทย, hashtags, เวลา)
- ตารางสรุป
- Tips และ opportunities

### 5. บันทึก Report

```
reports/content-ideas-{YYYYMMDD}.md
```
(ถ้ามีไฟล์วันเดียวกัน และมี topic ให้ใช้ `content-ideas-{YYYYMMDD}-{topic}.md`)

### 6. สรุปใน Chat

```
## 🗓️ Content Plan พร้อมแล้ว! ({start_date} – {end_date})

**Highlights สัปดาห์นี้:**
• ธีม: {monthly_theme}
• วันสำคัญที่ใกล้มา: {special dates หรือ "ไม่มี"}
• วันที่ควรโพสต์มากที่สุด: เสาร์ 🔴

**Top 3 Content Ideas:**
1. {วัน}: {หัวข้อ} [{platform}]
2. {วัน}: {หัวข้อ} [{platform}]
3. {วัน}: {หัวข้อ} [{platform}]

**ช่องว่างที่คู่แข่งยังไม่ทำ:**
- {opportunity}

📁 แผน 7 วันเต็ม: reports/content-ideas-{YYYYMMDD}.md
```

---

## หมายเหตุ

- Content plan เน้น **ความเป็นไปได้จริง** — หัวข้อที่คลินิกเล็กสามารถสร้างได้โดยไม่ต้องใช้ทีม production ใหญ่
- Caption ต้องเป็น **ภาษาไทย** ที่เป็นธรรมชาติ ไม่เป็นทางการเกินไป
- ทุกแผนต้องมีโพสต์วัน **เสาร์** ที่มีคุณภาพสูงที่สุด
- ถ้าใกล้วันสำคัญ (เช่น วันแม่, สงกรานต์) ให้เน้น content ที่เกี่ยวข้อง
