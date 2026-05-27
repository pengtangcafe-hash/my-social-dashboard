---
description: วิเคราะห์คู่แข่งกำลังโพสต์อะไร แล้วสร้างไอเดีย content ของเราที่ตอบโต้/parallel — พร้อม hook, caption, hashtag, reel script
---

ใช้ agent `advertising-agent` เพื่อสร้าง **Content Radar Report** — วิเคราะห์ content คู่แข่งแล้วสร้าง content ของเราที่แม่น

**Arguments:** $ARGUMENTS
- `/content-radar` — วิเคราะห์ทุกคู่แข่ง ทุก platform
- `/content-radar DentalPark` — เน้นคู่แข่งรายนั้น
- `/content-radar tiktok` — เฉพาะ TikTok
- `/content-radar จัดฟัน` — เฉพาะบริการนั้น
- `/content-radar quick` — แค่ hook + caption ไม่ต้องมี script

---

## ขั้นตอน:

### Phase 1: โหลดข้อมูลคู่แข่ง
```bash
python src/content_radar.py generate
```
อ่าน `data/competitors/*/` — snapshot ล่าสุดของแต่ละคู่แข่ง  
อ่าน `data/content-log.json` — content ของเราที่ perform ดีแล้ว  
อ่าน `data/content-radar.json` — radar ที่ generate แล้ว

### Phase 2: Filter ตาม argument
- ถ้าระบุชื่อคู่แข่ง → filter items ที่ competitor field ตรง
- ถ้าระบุ platform → filter ตาม platform field  
- ถ้าระบุบริการ → filter ตาม service field
- ถ้า `quick` → ข้าม reel_outline section

### Phase 3: สร้าง Content Radar Report

บันทึกใน `reports/content-radar-{YYYYMMDD}.md`:

```markdown
# Content Radar — {วันที่ไทย}
**จาก:** {competitor_count} คู่แข่ง | **โอกาส:** {opportunity_count} ไอเดีย

---

## 📡 Radar Overview
สรุปว่าคู่แข่งแต่ละรายกำลังทำอะไรอยู่ week นี้:

| คู่แข่ง | Platform | Content ล่าสุด | Strategy เรา |
|---------|---------|--------------|-------------|
| DentalPark | TikTok | รุ่นใหญ่ก็จัดฟันได้ | Mirror + Counter |
| หมอจั่นเจา | TikTok | ฟันปลอมฐานโลหะ | Expand |
| Dio | Facebook | Before/After รีวิว | Own It |
| Toothmate | Facebook | Composite Veneer | Expand |

---

## ⚔️ Counter Moves (ตอบโต้โดยตรง)

### [บริการ] vs [คู่แข่ง]
**เขาโพสต์:** [title/topic]  
**เราทำ:** [our_angle]

**🎣 Hook:**
> "[hook text]"

**📝 Caption:**
```
[caption text พร้อมใช้]
```

**🏷️ Hashtags:**
[hashtags]

**🎬 Reel Script (60 วิ):**
- [0-3s] ...
- [4-10s] ...
- [11-14s] ...
- [15s] CTA

---

## 🪞 Mirror Content (เรื่องเดิม มุมต่าง)

[เหมือนด้านบนแต่ mirror items]

---

## 👑 Own It (พื้นที่ที่คู่แข่งไม่มี)

[เหมือนด้านบนแต่ own items]

---

## 🚀 Expand (ขยายหัวข้อที่เขาทำยังไม่ลึก)

[เหมือนด้านบนแต่ expand items]

---

## 📅 Content Calendar แนะนำ (7 วัน)

| วัน | Platform | ประเภท | หัวข้อ | Inspired by |
|-----|---------|--------|--------|------------|
| จันทร์ | TikTok | Counter | ... | DentalPark |
| อังคาร | Facebook | Mirror | ... | Dio |
| พุธ | TikTok | Own It | ... | (ช่องว่าง) |
| พฤหัส | Instagram | Expand | ... | Toothmate |
| ศุกร์ | TikTok | Mirror | ... | DentalPark |
| เสาร์ | Facebook | Counter | ... | หมอจั่นเจา |
| อาทิตย์ | Instagram | Own It | ... | (ช่องว่าง) |

---

## ⚡ ทำทันที (ง่ายที่สุด ผลดีที่สุด)
1. [content idea ที่ทำได้เร็วที่สุด]
2. [content idea ที่มี potential สูงสุด]
3. [content idea ที่ตอบโต้คู่แข่งได้ทันที]
```

### Phase 4: แสดงสรุปใน chat
- Radar overview ตาราง 4 คู่แข่ง
- Top 3 content ที่ควรทำก่อน + เหตุผล
- Hook ที่คิดว่าจะ viral ที่สุด 1 อัน
- บอก path ไฟล์รายงาน
- แนะนำ next: `/content-radar quick` ถ้าอยากได้ caption ด่วน
