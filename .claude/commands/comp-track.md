ระบบติดตามและเปรียบเทียบคู่แข่งคลินิกทันตกรรม สกลนคร

---

## Parse Arguments

รับ argument ต่อไปนี้ (case-insensitive):

| Argument | ความหมาย |
|----------|----------|
| (ไม่มี) | แสดง comparison week ล่าสุดของทุก competitor |
| `--snapshot` | ค้นหาและบันทึก snapshot ปัจจุบันของทุก competitor |
| `--snapshot [ชื่อ]` | snapshot เฉพาะ competitor ที่ระบุ |
| `--compare week` | เปรียบเทียบสัปดาห์นี้ vs สัปดาห์ก่อน |
| `--compare month` | เปรียบเทียบเดือนนี้ vs เดือนก่อน |
| `--compare year` | เปรียบเทียบปีนี้ vs ปีก่อน |
| `--compare [ชื่อ]` | เปรียบเทียบเฉพาะ competitor ที่ระบุ (week default) |
| `--list` | แสดง snapshot ทั้งหมดที่มีใน data/competitors/ |
| `--report` | สร้าง report รวมทุก competitor บันทึกไฟล์ |

---

## ขั้นตอนการทำงาน

### กรณี: `--snapshot` (หรือ `--snapshot [ชื่อ]`)

1. กำหนด competitors ที่จะ snapshot:
   - ถ้าระบุชื่อ → เฉพาะ competitor นั้น
   - ถ้าไม่ระบุ → ทั้ง 4 รายคือ หมอจั่นเจา, DioDental, Toothmate, DentalPark

2. กำหนด period_label ของสัปดาห์ปัจจุบัน:
   ```python
   from datetime import date
   d = date.today()
   period_label = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
   ```

3. **เรียก comp-track-agent** โดยส่ง:
   - `competitors`: list ของ competitors
   - `mode`: "snapshot"
   - `period_label`: ค่าที่คำนวณได้

4. Agent จะค้นหา + สร้าง JSON + บันทึกลง `data/competitors/{name}/{period}.json`

5. แสดงสรุปใน chat:
   - รายชื่อ competitor ที่ snapshot สำเร็จ
   - จำนวนโปรโมชันและ content theme ที่พบ
   - path ไฟล์ที่บันทึก

---

### กรณี: `--compare week|month|year` (หรือ ไม่มี argument)

1. กำหนด mode: week (default), month, หรือ year

2. กำหนด competitors ที่มีข้อมูล:
   ```
   python src/competitor_tracker.py list
   ```

3. สำหรับแต่ละ competitor ที่มีข้อมูล ให้:
   ```
   python src/competitor_tracker.py compare {competitor} {mode}
   ```

4. รวม output เป็น report เดียว บันทึกที่:
   `reports/comp-track-{YYYYMMDD}.md`

5. สรุปใน chat ใน format:

```
## สรุปการเปลี่ยนแปลงคู่แข่ง ({period_old} → {period_new})

| คู่แข่ง | Activity | Followers | โปรใหม่ | Content ที่น่าสนใจ |
|---------|---------|-----------|---------|------------------|
| หมอจั่นเจา | ... | ... | ... | ... |
| DioDental | ... | ... | ... | ... |
| Toothmate | ... | ... | ... | ... |
| DentalPark | ... | ... | ... | ... |

📁 รายงานเต็ม: reports/comp-track-{YYYYMMDD}.md
```

---

### กรณี: `--list`

รัน: `python src/competitor_tracker.py list`

แสดงผลใน chat:
- รายชื่อ competitor ที่มี snapshot
- จำนวน snapshots และวันล่าสุด

---

### กรณี: `--report`

1. รัน: `python src/competitor_tracker.py report`
2. แจ้ง path ของไฟล์ที่บันทึก

---

## หมายเหตุสำคัญ

- **ถ้ายังไม่มี snapshot เลย**: แจ้งผู้ใช้ว่า "ยังไม่มีข้อมูล snapshot" และแนะนำให้ใช้ `/comp-track --snapshot` ก่อน
- **ถ้ามี snapshot แค่ 1 ช่วง**: แสดงข้อมูล snapshot ล่าสุดโดยตรง โดยไม่ต้องเปรียบเทียบ
- **ถ้าข้อมูลใน snapshot เป็น null**: แสดงเป็น "—" และไม่ต้องคำนวณ %
- **Snapshot ใหม่ทับเก่าในช่วงเดียวกัน**: ถ้า snapshot ของสัปดาห์เดิมมีอยู่แล้ว จะ overwrite โดยอัตโนมัติ
