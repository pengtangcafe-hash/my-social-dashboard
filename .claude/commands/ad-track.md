---
description: บันทึกและอัปเดต Ad Campaign — ติดตาม budget, reach, leads, และ ROI
---

ใช้ Python module `src/ad_tracker.py` เพื่อ **บันทึกและอัปเดต Ad Campaign**

**Arguments:** $ARGUMENTS
รูปแบบ:
- `/ad-track log [platform] [service] [budget]` — เริ่ม campaign ใหม่
- `/ad-track update [campaign_id] [reach] [leads]` — อัปเดตผลลัพธ์
- `/ad-track list` — ดู campaigns ทั้งหมด
- `/ad-track boost [platform] [post_url] [budget] [days]` — บันทึกการ boost post

ตัวอย่าง:
- `/ad-track log facebook จัดฟัน 3000` — บันทึก campaign Facebook ads จัดฟัน งบ 3000 บาท
- `/ad-track log tiktok ฟอกสีฟัน 1500 --days 14` — TikTok 14 วัน
- `/ad-track update camp-001 15000 23` — อัปเดต reach 15,000, leads 23 คน
- `/ad-track boost facebook 1500 7` — boost post Facebook 1,500 บาท 7 วัน
- `/ad-track list` — ดูรายการทั้งหมด

---

## ขั้นตอน:

### Parse Arguments
จาก `$ARGUMENTS` แยก subcommand และ parameters

### ถ้าเป็น `log`:
รัน:
```bash
python src/ad_tracker.py log [platform] "[service]" [budget] [--days X] [--start YYYY-MM-DD] [--objective awareness|leads|conversion]
```

### ถ้าเป็น `update`:
รัน:
```bash
python src/ad_tracker.py update [campaign_id] --reach [N] --leads [N] [--spend [N]]
```

### ถ้าเป็น `boost`:
รัน:
```bash
python src/ad_tracker.py log [platform] "boost" [budget] --days [N] --objective awareness
```

### ถ้าเป็น `list` หรือไม่มี args:
รัน:
```bash
python src/ad_tracker.py show
```

### หลังรัน command:
แสดงผลลัพธ์จาก stdout ให้ user เห็น
แนะนำ: ถ้าต้องการดู report รวม ใช้ `/ad-report`
