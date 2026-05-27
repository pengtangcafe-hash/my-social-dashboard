---
description: เขียน Ad Copy ภาษาไทยพร้อมใช้ — หลาย variation สำหรับ A/B test
---

ใช้ agent `advertising-agent` เพื่อเขียน **Ad Copy จริงๆ** สำหรับโพสต์/โฆษณา

**Arguments:** $ARGUMENTS
รูปแบบ: `/ad-copy [บริการ] [platform] [type?]`

ตัวอย่าง:
- `/ad-copy จัดฟัน tiktok` — copy สำหรับ TikTok video (script + caption)
- `/ad-copy ฟอกสีฟัน facebook` — copy สำหรับ Facebook post/ad
- `/ad-copy รากเทียม facebook paid` — copy สำหรับ Facebook Ads paid
- `/ad-copy ขูดหินปูน instagram story` — copy สำหรับ IG Story
- `/ad-copy จัดฟันใส tiktok script` — script วิดีโอ TikTok เต็ม
- `/ad-copy โปรแม่ facebook` — copy โปรโมชั่นวันแม่

---

## ขั้นตอน:

### Phase 1: โหลดบริบท
1. อ่าน `data/content-log.json` — category ที่เคย perform ดีของเรา
2. อ่าน `docs/intelligence-brief.md` — messaging และ hashtags ของคู่แข่ง
3. อ่าน `data/dental-calendar.json` — theme เดือนนี้ + วันสำคัญ + hashtag sets
4. ถ้ามี brief ใน `reports/ad-brief-*` ที่เกี่ยวข้อง ให้อ่านด้วย

### Phase 2: วิเคราะห์ก่อนเขียน
- Pain point หลักของกลุ่มเป้าหมายนี้คืออะไร
- คู่แข่งพูด angle ไหนอยู่แล้ว → เราต้องหลีกเลี่ยงหรือ counter
- Platform นี้ใช้ tone ไหน (TikTok = สนุก/เร็ว, Facebook = อ่านมากขึ้น, IG = visual)
- มีเทศกาล/วันสำคัญที่ควรผูก hook ไหม

### Phase 3: เขียน Copy ≥ 3 Variations

บันทึกใน `reports/ad-copy-{service}-{platform}-{YYYYMMDD}.md`:

---

```markdown
# Ad Copy: [บริการ] — [Platform]
**วันที่:** {วันที่}
**Tone:** [กันเอง / Professional / อีสาน-local]

---

## 🅐 Variation A — [Hook style: Pain-based]

**Hook (ประโยคแรก / 3 วินาทีแรก):**
> "..."

**Body Copy:**
```
[copy เต็ม — พร้อมวางเลย]
```

**CTA:**
> "..."

**Hashtags:**
#... #... #...

---

## 🅑 Variation B — [Hook style: Curiosity/Question]

**Hook:**
> "..."

**Body Copy:**
```
[copy เต็ม]
```

**CTA:**
> "..."

**Hashtags:**
#... #...

---

## 🅒 Variation C — [Hook style: Social Proof/Numbers]

**Hook:**
> "..."

**Body Copy:**
```
[copy เต็ม]
```

**CTA:**
> "..."

**Hashtags:**
#... #...

---

## 🎬 [ถ้าเป็น TikTok / Video] Script เต็ม

### Visual Timeline:

| วินาที | ภาพ/Action | Audio/Caption |
|--------|-----------|--------------|
| 0-3    | ... | Hook |
| 3-10   | ... | Problem |
| 10-20  | ... | Solution |
| 20-30  | ... | Proof/CTA |

### Voice-over Script:
```
[0:00] "..."
[0:05] "..."
[0:15] "..."
[0:25] "..."
```

---

## 📸 [ถ้าเป็น Image/Carousel] Caption ต่อ slide

### Slide 1 (Hook):
> "..."

### Slide 2-4 (Content):
> "..."

### Slide สุดท้าย (CTA):
> "..."

---

## 💬 Organic Post Version (ไม่ใช้งบโฆษณา)
[version ที่โพสต์เองโดยไม่ต้อง boost — tone กันเองกว่า]

```
[copy organic]
```

Hashtags organic:
#... #... #สกลนคร #...

---

## 🧪 A/B Test แนะนำ
- **ทดสอบ Hook A vs B** — รัน 3-5 วัน วัด CTR
- **ทดสอบ Image vs Video** — รัน 7 วัน วัด CPL
- ถ้า CTR < 1% → เปลี่ยน Hook ทันที
- ถ้า Frequency > 3 → เปลี่ยน Creative ใหม่

---

## 📋 Facebook Ad Policy Check
สิ่งที่ต้องระวัง (Facebook ห้าม):
- ❌ พูดว่า "รักษา" โรค — ใช้ "ดูแล" / "ปรับปรุง" แทน
- ❌ Before/After ที่ดูเกินจริง — ต้องมี disclaimer
- ❌ ราคาที่ misleading — ระบุเงื่อนไขชัดเจน
- ✅ "นัดปรึกษาฟรี" — ใช้ได้
- ✅ "ตรวจประเมินฟรี" — ใช้ได้
```

### Phase 4: สรุปใน chat
- บอก Variation ไหนที่แนะนำให้ทดสอบก่อน + เหตุผล
- Tip 1-2 ข้อสำหรับ platform นี้โดยเฉพาะ
- Next step: บันทึก campaign ด้วย `/ad-track` หลัง launch
