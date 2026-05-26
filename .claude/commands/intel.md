รัน intel-agent เพื่อค้นหาข้อมูลตลาด คู่แข่ง hashtags งาน events และอุปกรณ์ทันตกรรม

ขั้นตอน:
1. กำหนดค่า default:
   - topic = "คลินิกทันตกรรม"
   - city = "สกลนคร"
   - platforms = ["tiktok", "facebook", "instagram"]
   - ถ้ามี argument ให้ parse เป็น topic และ/หรือ city เช่น `/intel จัดฟัน` หรือ `/intel จัดฟัน นครพนม`

2. เรียก intel-agent โดยส่ง:
   - topic, city, platforms ที่กำหนดไว้

3. บันทึก report ที่ได้จาก intel-agent ลงไฟล์:
   reports/intel-[YYYYMMDD].md
   (ถ้ามีไฟล์ชื่อเดิมอยู่แล้วให้ใช้ reports/intel-[YYYYMMDD]-[topic].md)

4. **บันทึก update log** โดยรันคำสั่ง:
   ```
   python src/update_logger.py log intel pricing
   python src/update_logger.py inject dashboard/index.html
   ```
   (intel และ pricing อัปเดตพร้อมกันเพราะข้อมูลราคามาจาก intel)

5. สรุปสั้นๆ ใน chat:
   - topic และ city ที่ค้นหา
   - highlights 3 จุดที่น่าสนใจที่สุดจาก report
   - path ของ report ที่บันทึก
