---
description: สรุป Performance ทุก Ad Campaign — ROI, CPR, CPL, Organic vs Paid เปรียบเทียบ
---

ใช้ agent `advertising-agent` เพื่อสร้าง **Ad Performance Report** รวมทุก campaign

**Arguments:** $ARGUMENTS
- `/ad-report` — report ทุก campaign ที่มี
- `/ad-report month` — เฉพาะเดือนนี้
- `/ad-report [platform]` — เฉพาะ facebook / tiktok / instagram
- `/ad-report [service]` — เฉพาะบริการ เช่น "จัดฟัน"
- `/ad-report vs-organic` — เปรียบเทียบ paid vs organic performance

---

## ขั้นตอน:

### Phase 1: โหลดข้อมูล
```bash
python src/ad_tracker.py show-json
```
อ่าน `data/ad-campaigns.json` — campaigns ทั้งหมด
อ่าน `data/content-log.json` — organic content performance
อ่าน `data/history/` — account-level metrics ในช่วงที่ campaign รัน

### Phase 2: Filter ตาม argument
- ถ้า `month` → filter campaigns ที่ start_date อยู่ในเดือนนี้
- ถ้า platform → filter ตาม platform field
- ถ้า service name → filter ตาม service field
- ถ้า `vs-organic` → เตรียม comparison data

### Phase 3: คำนวณ KPIs ต่อ campaign

สำหรับแต่ละ campaign:
```
CPR  = budget_spent / reach          (ต่ำ = ดี)
CPL  = budget_spent / leads          (ต่ำ = ดี)
CTR  = clicks / impressions * 100    (สูง = ดี)
ROAS = (leads * avg_order) / budget_spent  (สูง = ดี)
Eng% = engagements / reach * 100
```

### Phase 4: สร้าง Report

บันทึกใน `reports/ad-report-{YYYYMMDD}.md`:

```markdown
# Ad Performance Report
**วันที่:** {วันที่}
**ช่วงที่วิเคราะห์:** {from} — {to}

---

## Executive Summary

| KPI | ผลรวม | เฉลี่ยต่อ campaign |
|-----|-------|------------------|
| งบรวมที่ใช้ | X,XXX บาท | XXX บาท |
| Reach รวม | X,XXX คน | X,XXX |
| Leads รวม | XX คน | X.X |
| CPR เฉลี่ย | X.XX บาท | — |
| CPL เฉลี่ย | XXX บาท | — |

**สรุปคำเดียว:** [ดีกว่า / แย่กว่า / เท่ากัน] กับเป้าหมายที่ตั้งไว้

---

## Campaign Performance Table

| ID | Platform | บริการ | งบ | Reach | Leads | CPR | CPL | Status |
|----|----------|-------|-----|-------|-------|-----|-----|--------|
| ... | | | | | | | | |

---

## Top Performer 🏆
**Campaign:** [ชื่อ]
- เหตุผล: CPL ต่ำสุด / ROAS สูงสุด / Engagement ดีที่สุด
- ควร Scale Budget ขึ้น: แนะนำ X บาท/วัน

## Worst Performer ⚠️
**Campaign:** [ชื่อ]
- ปัญหา: [CPL สูงเกิน / CTR ต่ำ / Audience Fatigue]
- แนะนำ: [หยุด / เปลี่ยน creative / ปรับ targeting]

---

## Organic vs Paid Comparison

| Metric | Organic | Paid | ดีกว่า |
|--------|---------|------|-------|
| Reach เฉลี่ย/post | X,XXX | X,XXX | ✅ |
| Engagement Rate | X% | X% | ✅ |
| Cost per Reach | 0 บาท | X.XX บาท | Organic ✅ |
| ความเร็ว | ช้า | เร็ว | Paid ✅ |
| ความยั่งยืน | สูง | ต่ำ | Organic ✅ |

**สรุป:** [แนะนำ ratio organic:paid ที่เหมาะสม]

---

## Platform Breakdown

### Facebook
- Campaigns: X | งบรวม: X,XXX บาท | CPL: XXX บาท

### TikTok  
- Campaigns: X | งบรวม: X,XXX บาท | CPL: XXX บาท

---

## Service Breakdown

| บริการ | Campaigns | งบ | CPL | ประสิทธิภาพ |
|--------|-----------|-----|-----|-----------|
| จัดฟัน | X | X,XXX | XXX | ⭐⭐⭐ |
| ฟอกสีฟัน | X | XXX | XXX | ⭐⭐ |

---

## ROI Analysis (ถ้ามีข้อมูลรายได้)
[section นี้แสดงเฉพาะถ้ามี actual_revenue ใน campaign data]

---

## Recommendations

### ทำทันที:
1. [action ที่ต้องทำเลย]
2. [action ที่ 2]

### เดือนหน้า:
- Budget allocation แนะนำ: [breakdown]
- Campaign ใหม่ที่ควรทดสอบ: [idea]
- Platform ที่ควรเพิ่มงบ: [เหตุผล]

### หยุดทำ:
- [สิ่งที่ไม่ได้ผล และทำไม]
```

### Phase 5: แสดงสรุปใน chat
- Key numbers 3-5 ตัวที่สำคัญที่สุด
- Top win + Top miss
- Budget แนะนำสำหรับเดือนหน้า
- Next campaign ที่ควรเริ่ม
