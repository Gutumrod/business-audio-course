# 📚 Business Audio Courseware: Architecture & Scalability Roadmap
*เอกสารแผนงานสถาปัตยกรรมระบบคอร์สบทเรียนเสียงเพื่อการเรียนรู้ธุรกิจด้วยตนเอง*  
*บันทึกเมื่อ: 2026-10-10 | อนุมัติโดย: คุณฟรี (CEO) | ดูแลโดย: Antigravity (AGY)*

---

## 🎯 1. ภาพรวมและวิสัยทัศน์ของระบบ (Vision & Goals)
สร้างเว็บแอปพลิเคชันคอร์สบทเรียนเสียง (Audio Courseware) ที่:
1. **Zero AI-Slop & Editorial Clean:** ดีไซน์สไตล์นิตยสารธุรกิจเพื่อการเรียนรู้จริงจัง สะอาดตา อ่านสบาย ไม่ฉูดฉาด
2. **Offline-First & Fast:** โหลดเร็ว ทำงานได้บนมือถือทุกรุ่น (iOS Safari / Android) ฟังต่อเนื่องได้แม้ออกนอกบ้าน
3. **Data-Driven & Scalable:** หน้าจอเดียวสามารถสลับบทเรียนและข้อสอบได้อัตโนมัติ และรองรับการขยายเป็น "หอสมุดเสียงหลายเล่ม (Multi-Volume Academy)" ได้ไม่จำกัด

---

## 📂 2. โครงสร้างระบบรองรับหลายเล่ม (Multi-Volume Directory Architecture)

เมื่อขยายผลจากเล่ม 1 ไปสู่เล่มต่อๆ ไป ให้จัดวางโครงสร้างแบบแยกเล่มชัดเจน:

```text
business-audio-course/
│
├── index.html                      # หน้า Hub รวมทุกเล่ม (Library Dashboard)
├── ARCHITECTURE-AND-ROADMAP.md    # เอกสารสถาปัตยกรรมฉบับนี้
│
├── vol-01/                         # เล่ม 1: พื้นฐานธุรกิจ (Business Foundations)
│   ├── index.html                  # Player ของเล่ม 1 (สลับบท 1-10 ในตัว)
│   ├── audio/                      # ไฟล์เสียง MP3 ของบทที่ 1–10
│   │   ├── ch01_full.mp3
│   │   ├── ch02_full.mp3
│   │   └── ...
│   ├── data/
│   │   └── chapters.js             # ฐานข้อมูลเนื้อหา สรุป อินโฟกราฟิก และ Quiz ทั้ง 10 บท
│   └── images/                     # ภาพประกอบ/ไดอะแกรมประจำบท
│
├── vol-02/                         # เล่ม 2: การตลาดและการขาย (Marketing & Sales)
│   ├── index.html                  # Player ของเล่ม 2
│   ├── audio/
│   ├── data/
│   └── images/
│
├── vol-03/                         # เล่ม 3: การเงินและกระแสเงินสด (Finance & Cashflow)
│   └── ...
│
└── shared/                         # แอสเซทส่วนกลางที่ใช้ร่วมกันทุกเล่ม
    ├── css/                        # Global Editorial Styles, Tokens
    ├── js/                         # Audio Engine, LocalStorage Manager
    └── icons/                      # SVG Icons
```

---

## 🛠️ 3. กลไกการทำงานของระบบ (Core Mechanisms)

### 3.1 Data-Driven Chapter Switching (สลับบทในหน้าเดียว)
- **ไม่สร้างไฟล์ HTML ซ้ำซ้อน:** แต่ละเล่มจะมี `index.html` เพียงหน้าเดียว
- ข้อมูลของแต่ละบทจะอยู่ใน `chapters.js` ในรูปแบบ Object เช่น:
  ```javascript
  const CHAPTERS = [
    {
      id: 1,
      title: "ธุรกิจคืออะไร และผู้บริหารทำอะไร",
      audio: "audio/ch01_full.mp3",
      duration: "3:34",
      objective: "อธิบายความต่างระหว่างรายได้ ต้นทุน กำไร และบทบาทผู้บริหาร",
      sections: [...],
      diagrams: [...],
      quiz: [...]
    },
    ...
  ];
  ```
- มี **Chapter Drawer / Dropdown Menu** ให้ผู้เรียนเลือกเปลี่ยนบทได้ทันที พร้อมปุ่ม "← บทก่อนหน้า" และ "บทถัดไป →"

### 3.2 ระบบจำสถานะแยกเล่ม (LocalStorage Isolation)
- แยก Namespace ชัดเจนตามเล่ม เพื่อไม่ให้ข้อมูลทับซ้อนกัน:
  - `agy_v01_current_chapter`: บทล่าสุดที่กำลังเรียน
  - `agy_v01_ch01_time`: เวลาเสียงที่ฟังค้างไว้ของบทที่ 1
  - `agy_v01_ch01_completed`: สถานะฟังจบของบทที่ 1
  - `agy_v01_ch01_quiz_answers`: คำตอบควิซของบทที่ 1
  - `agy_v01_ch01_score`: คะแนนสอบของบทที่ 1

### 3.3 มาตรฐานการผลิตเสียง (TTS Production Standard)
- **Engine:** Gemini 3.1 Flash TTS Preview
- **Voice:** `Sadaltager` (Knowledgeable Business Mentor)
- **Director Prompt:** `"Style: Knowledgeable Business Mentor, calm, warm, authoritative, clear Thai articulation, steady and thoughtful pacing."`
- **Multi-Part Concat Rule:** เพื่อป้องกัน API Cutoff (~70s limit) ให้แบ่งสคริปต์เป็นท่อนละ 70-100 คำ (~40-50 วินาที) แล้วนำมาต่อด้วย `ffmpeg -f concat` เป็นไฟล์เดียว

---

## 🗺️ 4. แผนงานการพัฒนา (Action Roadmap)

### เฟส 1 (ปัจจุบัน): Pilot บทที่ 1 (เสร็จสมบูรณ์)
- [x] สคริปต์คำอ่านไทยธรรมชาติของบทที่ 1
- [x] เจนเสียง Sadaltager ตัวเต็ม 3:34 นาที (MP3)
- [x] Web Player สไตล์ Editorial สะอาดตา ไร้ AI-Slop
- [x] Interactive Quiz 3 ข้อ พร้อมเฉลยละเอียด
- [x] Deploy ขึ้น GitHub Pages ออนไลน์ 24 ชม. ([https://gutumrod.github.io/business-audio-course/](https://gutumrod.github.io/business-audio-course/))
- [x] แก้ไขบั๊ก Mobile Audio Playback บน iOS / Android

### เฟส 2: ยกระดับสู่ Data-Driven Player & ผลิตบทที่ 2
- [ ] แปลงโครงสร้าง `index.html` ให้รองรับ Data-Driven `chapters.js`
- [ ] เพิ่มเมนู **Chapter Navigation Drawer** เลือกบทที่ 1 และ 2
- [ ] เพิ่ม **ภาพประกอบ Infographic / Diagram** ประจำบทที่ 1 และ 2
- [ ] เรียบเรียงสคริปต์และเจนเสียง Sadaltager บทที่ 2 ("ลูกค้า ปัญหา และคุณค่าที่ขาย")
- [ ] เพิ่ม Interactive Quiz ของบทที่ 2
- [ ] ทดสอบและ Deploy ขึ้น GitHub Pages

### เฟส 3: ขยายผลให้ครบเล่ม 1 (บทที่ 3–10)
- ผลิตบทที่ 3 ถึง 10 ให้ครบถ้วนตามลำดับ
- สรุปผลคะแนนรวม 30 ข้อ และสร้างใบ Certificate จำลองผ่านหน้าเว็บ

### เฟส 4: Multi-Volume Academy Portal
- สร้างหน้า Dashboard Hub รวมเล่ม 1, เล่ม 2, เล่ม 3
- เตรียมพร้อมสำหรับการศึกษาต่อยอดและขยายผลในอนาคต
