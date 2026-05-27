---
description: สร้าง Creative Brief สำหรับ Ad Campaign เดียว — พร้อม Persona, USP, Budget, Timeline
---

ใช้ agent `advertising-agent` เพื่อสร้าง **Creative Brief** สำหรับ campaign เฉพาะ

**Arguments:** $ARGUMENTS
รูปแบบ: `/ad-brief [บริการ] [platform]`

ตัวอย่าง:
- `/ad-brief จัดฟัน facebook` — brief สำหรับ Facebook Ads โปรจัดฟัน
- `/ad-brief รากเทียม tiktok` — brief TikTok Ads รากเทียม
- `/ad-brief ฟอกสีฟัน` — brief ทุก platform สำหรับ ฟอกสีฟัน
- `/ad-brief ขูดหินปูน instagram` — brief Instagram promotion
- `/ad-brief จัดฟันใส facebook paid` — เน้น paid ads

---

## ขั้นตอน:

### Phase 1: โหลดบริบท
1. อ่าน `docs/intelligence-brief.md` — ราคาและ messaging ของคู่แข่งต่อบริการนี้
2. อ่าน intel reports ที่เกี่ยวข้องกับ [บริการ]: `reports/intel-*.md` (grep หา keyword)
3. อ่าน `data/content-log.json` — เราเคยโพสต์ category นี้แล้วได้ผลแค่ไหน
4. อ่าน competitor snapshots — promotions ที่คู่แข่งใช้สำหรับบริการนี้

### Phase 2: วิเคราะห์ตลาดสำหรับบริการนี้
- ราคาตลาดคือเท่าไหร่ (จากข้อมูล intel)
- คู่แข่งสื่อสารบริการนี้ยังไง
- Pain point หลักของลูกค้าคืออะไร
- จุดขายที่เราต่างจากคู่แข่งคืออะไร

### Phase 3: สร้าง Creative Brief

บันทึกใน `reports/ad-brief-{service}-{platform}-{YYYYMMDD}.md`:

```markdown
# Creative Brief: [บริการ] — [Platform]
**วันที่สร้าง:** {วันที่}
**Campaign Period:** แนะนำ {ช่วงเวลา}

---

## 1. Campaign Objective
[ ] Awareness — เพิ่ม reach ให้คนรู้จักคลินิก
[ ] Consideration — ให้คนสนใจบริการนี้
[ ] Conversion — ให้คนนัดหมาย/ทักมา
[ ] Retention — ลูกค้าเก่า กลับมาใช้บริการ

**Primary Objective:** ...
**KPI:** Reach X คน | CTR > X% | Leads X คน

---

## 2. Target Audience (Persona)

### Persona หลัก: "[ชื่อ persona]"
- **อายุ:** ...
- **เพศ:** ...
- **อาชีพ/สถานะ:** ...
- **พื้นที่:** สกลนคร + รัศมี X กม.
- **Pain Point:** ...
- **Motivation:** ...
- **พฤติกรรม digital:** ใช้ ... มากที่สุด ช่วง ...

### Persona รอง (ถ้ามี): "[ชื่อ]"
...

### Targeting Settings ([Platform])
- **Location:** จ.สกลนคร + จ. [ใกล้เคียง]
- **Age:** ...
- **Interests:** ...
- **Behaviors:** ...
- **Custom Audience:** Retarget คนที่เคย engage กับ page (ถ้ามี)
- **Lookalike:** 1-3% จาก customer list (ถ้ามี)

---

## 3. Key Message & USP

**Core Message:**
> "[ประโยคเดียวที่สื่อสารคุณค่า]"

**USP เทียบกับคู่แข่ง:**
| เรา | หมอจั่นเจา | Dio Dental | Toothmate | Dental Park |
|-----|-----------|------------|-----------|-------------|
| ... | ... | ... | ... | ... |

**ข้อความที่ห้ามพูด:** (เพราะคู่แข่งพูดอยู่แล้ว)
- ...

---

## 4. Creative Direction

### Visual Style
- **โทนสี:** ...
- **สไตล์ภาพ:** [Real photo / Illustration / Before-After / TikTok-style]
- **ตัวอย่าง reference:** [อธิบายหรือ link ถ้ามี]

### Tone of Voice
- [ ] กันเอง ภาษาพูด
- [ ] ภาษาอีสานเบาๆ (local appeal)
- [ ] Professional แต่อบอุ่น
- [ ] Educational / Authority

### Ad Formats แนะนำ
1. **Primary:** [Video Reel / Single Image / Carousel / Story]
2. **Secondary:** [format อีกแบบสำหรับ A/B test]

---

## 5. Copy Guidelines

### Hook (ประโยคเปิด — 1-3 วินาที):
- แบบ A (Pain-based): "..."
- แบบ B (Curiosity): "..."
- แบบ C (Social proof): "..."

### Body Copy แนวทาง:
- ความยาว: [สั้น <50 คำ / กลาง 50-100 / ยาว >100]
- ต้องมี: [ราคา / โปร / รีวิว / ตัวเลข / deadline]
- Emoji: [ใช้เยอะ / ใช้พอดี / ไม่ใช้]

### CTA (Call-to-Action):
- Primary: "..."
- Button text: "..."
- Destination: [DM / Link / Call / Line OA]

---

## 6. Budget & Timeline

| รายการ | รายละเอียด |
|--------|-----------|
| **Platform** | [Facebook / TikTok / Instagram] |
| **Budget รวม** | X,XXX บาท |
| **Duration** | X สัปดาห์ (วันที่... ถึง...) |
| **Daily Budget** | ~XXX บาท/วัน |
| **Bid Strategy** | [Lowest Cost / Cost Cap / Bid Cap] |
| **Schedule** | ทุกวัน / เฉพาะ [วัน] ช่วง [เวลา] |

### Budget Breakdown:
- Awareness phase (X%): XXX บาท
- Conversion phase (X%): XXX บาท
- A/B test reserve (X%): XXX บาท

---

## 7. Success Metrics & Benchmarks

| Metric | เป้าหมาย | เตือนถ้า |
|--------|----------|---------|
| Reach | >X,XXX คน | <X,XXX |
| CTR | >X% | <X% |
| CPR | <X.XX บาท | >X.XX |
| Leads/DMs | >X ต่อสัปดาห์ | <X |
| CPL | <XXX บาท | >XXX |

---

## 8. Production Checklist

**ก่อน launch:**
- [ ] สร้าง creative ตาม brief นี้
- [ ] เขียน copy ≥ 3 variations (ใช้ `/ad-copy`)
- [ ] ตรวจ Facebook Ad Policy (ข้อห้ามโฆษณาทางการแพทย์)
- [ ] ตั้ง Facebook Pixel / TikTok Pixel ถ้ามี website
- [ ] บันทึก campaign ด้วย `python src/ad_tracker.py log`

**ระหว่าง campaign (ดูทุก 3 วัน):**
- [ ] ตรวจ CTR — ถ้า <1% ให้เปลี่ยน creative
- [ ] ตรวจ Frequency — ถ้า >3x ให้ขยาย audience หรือเปลี่ยน ad
- [ ] ตรวจ Lead quality — DM คุยต่อได้ไหม
```

### Phase 4: สรุปใน chat
- Target Persona หลักคือใคร (สั้น 2-3 บรรทัด)
- USP ที่เลือก + เหตุผล
- Budget ที่แนะนำ
- Next step: `/ad-copy [บริการ] [platform]` เพื่อได้ copy จริง
