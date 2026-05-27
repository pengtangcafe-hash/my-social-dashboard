---
description: วิเคราะห์คู่แข่ง + สร้างกลยุทธ์โฆษณา Organic + Paid ครบวงจร
---

ใช้ agent `advertising-agent` เพื่อสร้าง **Ad Strategy Report** ฉบับสมบูรณ์

**Arguments:** $ARGUMENTS
(ถ้าไม่มี = สร้าง strategy รวมทุก platform และบริการ)
(ถ้าระบุ เช่น "จัดฟัน" / "TikTok" / "ฟอกสีฟัน paid" = เน้น topic นั้น)

---

## ขั้นตอนที่ต้องทำ:

### Phase 1: โหลดข้อมูลทั้งหมด
1. อ่าน `docs/intelligence-brief.md` — framework คู่แข่ง 4 ราย
2. อ่าน reports intel ล่าสุด: `reports/intel-*.md` (glob ทั้งหมด อ่านไฟล์ใหม่สุด 3 ไฟล์)
3. อ่าน competitor snapshots ล่าสุดของแต่ละราย:
   - `data/competitors/หมอจั่นเจา/` — ไฟล์ล่าสุด
   - `data/competitors/DioDental/` — ไฟล์ล่าสุด
   - `data/competitors/Toothmate/` — ไฟล์ล่าสุด
   - `data/competitors/DentalPark/` — ไฟล์ล่าสุด
4. อ่าน `data/content-log.json` — content ที่เราโพสต์ไปและผลลัพธ์
5. อ่าน `data/history/` — performance ของเราเอง (ไฟล์ล่าสุดของแต่ละ platform)
6. อ่าน `data/ad-campaigns.json` ถ้ามี — campaign ที่เคยรัน

### Phase 2: วิเคราะห์ Competitive Gap
สร้างตาราง 4 มิติ:
- **Content Gap:** สิ่งที่คู่แข่งยังไม่ทำ หรือทำไม่ดี
- **Audience Gap:** กลุ่มที่คู่แข่งมองข้าม
- **Platform Gap:** platform ที่คู่แข่งอ่อนแอ
- **Message Gap:** มุมที่ยังไม่มีใครพูดถึง

### Phase 3: สร้าง Strategy Report

สร้างไฟล์ `reports/ad-strategy-{YYYYMMDD}.md` ที่มี sections:

```markdown
# กลยุทธ์โฆษณา — คลินิกทันตกรรม สกลนคร
**วันที่:** {วันที่ไทย}

## 1. Executive Summary
(3-5 bullet points ที่ต้องทำทันที)

## 2. Competitive Landscape
(ตาราง: คู่แข่ง × จุดแข็ง × จุดอ่อน × platform ที่ active)

## 3. Competitive Gap — โอกาสของเรา
### Content Gaps
### Audience Gaps  
### Platform Gaps
### Message Gaps

## 4. Positioning Statement
"สำหรับ [กลุ่มเป้าหมาย] ที่ [pain point]
คลินิกของเราคือ [ตำแหน่ง] ที่ [จุดขาย]
ต่างจากคู่แข่งตรงที่ [differentiator]"

## 5. แผน Organic Content (ไม่เสียค่าโฆษณา)
### TikTok Strategy
- Theme หลัก 3 อย่าง + Hook formula
- ความถี่และเวลาโพสต์

### Facebook Strategy
- Format ที่ควรเน้น (จากข้อมูล format analyzer)
- Content pillars

### Instagram Strategy

## 6. แผน Paid Advertising

### Campaign 1: [ชื่อ campaign แรกที่แนะนำ]
- Platform: ...
- Objective: ...
- Target Audience: ...
- Budget แนะนำ: ...
- Duration: ...
- Key Message: ...
- Ad Format: ...

### Campaign 2: [ชื่อ campaign ที่สอง]
...

### Campaign 3: [ชื่อ campaign ที่สาม]
...

## 7. Hook & Copy Ideas (Top 5)
(hooks ที่น่าสนใจที่สุดสำหรับ platform หลัก)

## 8. Budget Allocation (ต่อเดือน)

| Platform | งบแนะนำ | Objective | KPI เป้าหมาย |
|---|---|---|---|

## 9. 30-Day Action Plan

### สัปดาห์ที่ 1 (ทำทันที)
### สัปดาห์ที่ 2-3 (เริ่ม campaign)
### สัปดาห์ที่ 4 (วัดผล + ปรับ)

## 10. Success Metrics
```

### Phase 4: สรุปใน chat
หลังบันทึกไฟล์แล้ว แสดงสรุปใน chat:
- 3 insight ที่สำคัญที่สุดจาก competitor gap
- Campaign ที่แนะนำให้ทำก่อน (prioritized)
- บอก path ไฟล์รายงาน
- แนะนำ next command: `/ad-brief [บริการ] [platform]` สำหรับ campaign แรก
