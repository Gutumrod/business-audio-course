# WSTERA Academy × Business Audio Courseware — AGY Task B1 Handoff & Test Evidence Report

- **สถานะงาน:** `READY FOR GPT INDEPENDENT REVIEW` (**ยังไม่ Merge เข้า `main` และยังไม่ Deploy Production**)
- **Repository:** `Gutumrod/business-audio-course` (`d:\AI-Workspace\learning\AGY-Business-Self-Study`)
- **Base Branch (`main`):** `6a855230644afdef93eac8644a4d7e788717b730` (คงเดิม ไม่มีการแก้ไขบน `main`)
- **Feature Branch:** `feat/b1-learning-hub-storage-guard`
- **Commit SHA:** `e0e4ce8fb411a4cee1a469dfb586d1418fad9f36` (`e0e4ce8`)
- **วันที่ส่งตรวจ:** `2026-10-10`

---

## 1. สรุปไฟล์ที่เปลี่ยนแปลง (Bounded B1 Scope — 4 ไฟล์เท่านั้น)

ตรวจด้วย `git diff main...feat/b1-learning-hub-storage-guard --stat`:

| ไฟล์ | สถานะ | รายละเอียดการเปลี่ยนแปลง |
| :--- | :--- | :--- |
| `index.html` | Modified | เพิ่ม Learning Hub (`#home`), Hash Router (`#home`, `#lesson/V00-L01..L10`, `#progress`, `#pretest/V00`, `#help`), แยกแสดงผล 4 มิติความคืบหน้า, คง `<audio id="audioElement">` ตัวเดิมข้ามหน้า |
| `js/storage-manager.js` | New | `window.LearningStore`: ระบบป้องกัน `localStorage` เสียหาย (Lossless Corrupt Storage Guard), ตรวจ Schema/Question IDs/Options `A\|B\|C\|D`, ป้องกัน `__proto__`, สำรองข้อมูลดิบฉบับเต็มก่อนกู้คืน |
| `data/v00-manifest.js` | New | `window.WSTERA_V00_MANIFEST`: ผูกรหัสมาตรฐาน `MBAI-SELF-01` / `V00` / `V00-L01..V00-L10` เข้ากับ `window.COURSE_CHAPTERS` โดยไม่แตะ `data/chapters.js`, ระบุเวลาเสียงรวมจริง `1,706 วินาที (28:26 นาที)` แยกจากเวลาเรียนรวม `8–12 ชั่วโมง`, และคลังคำศัพท์ภาษาไทยเข้าใจง่าย |
| `ARCHITECTURE-AND-ROADMAP.md` | Modified | อัปเดตเอกสารสถาปัตยกรรมให้ตรงกับรหัส `V00` (`vol-01` เป็นเพียง `legacy_agy_alias`), เส้นทาง Hash Router, สัญญา `SafeStorage`, และยกเลิกแนวคิดออกใบรับรองจำลองอัตโนมัติจากคะแนนควิซหน้าเว็บ |

### การยืนยันไฟล์ห้ามแตะในรอบ B1 (Zero Diff Check)
- `git diff main -- audio/ audio-course/ data/chapters.js` → **`0 bytes` (ไม่มีการแก้ไขหรือลบแม้แต่ไฟล์เดียว)**
- ไม่มีการสร้าง `data/v00-pretest-questions.js` และไม่มีการเชื่อม Supabase/Cloud ในรอบ B1
- ไม่มีคะแนน `66/100`, ไม่มี `ANSWER-KEY`, และไม่มีสถานะ `verified_external_import` อยู่ในโค้ดหรือคอมเมนต์ใดๆ

---

## 2. การปฏิบัติตามเงื่อนไข B1 C1–C8 และ Acceptance Checklist 9 ข้อ

| ข้อ | เกณฑ์ตรวจรับตาม `05-B0-AGY-INDEPENDENT-REVIEW.md` & `06-B1-IMPLEMENTATION-BRIEF-DRAFT.md` | ผลตรวจ | หลักฐานยืนยัน |
| :--- | :--- | :--- | :--- |
| **1** | โหลด `/` และ `/?v=2` ได้; `#home`, `#lesson/V00-L01`, `#lesson/V00-L10`, `#progress`, `#pretest/V00`, `#help` ทำงานครบ; รองรับ Refresh / Deep-link / Back-Forward; Hash แปลกหรือรหัสบทผิด (`#unknown-route-xyz`, `#lesson/V00-L99`) fallback กลับอย่างปลอดภัย | **PASS** | `routes_and_ux.passed = true` ใน `qa/b1/B1-QA-EVIDENCE.json` |
| **2** | ชื่อบท เนื้อหา ควิซทบทวน 10 บท และพาธ MP3 คงเดิม 100%; ไม่แตะ `audio/*`, `audio-course/*`, `data/chapters.js` | **PASS** | `untouched_protected_paths.diff_bytes = 0` |
| **3** | ทดสอบ `agy_ch01_quiz_answers` เสียหายทั้ง 7 รูปแบบ (`invalid_json`, `null`, `[]`, `primitive_number`, `primitive_string`, `__proto__`, รหัสข้อ/ตัวเลือกผิด) → ไม่เกิด JS crash, เรนเดอร์ชิปครบ `10/10 บท`, ข้อมูลบทที่ 2 (`ch02`) อยู่ครบ, และ**ไม่ลบหรือตัดทอนค่าดิบเดิมขณะอ่าน** | **PASS** | `corrupt_storage_matrix` ผ่านครบ 7/7 เคส (`ch_chip_count = 10`, `raw_preserved_on_read = true`) |
| **4** | ทดสอบกู้คืนข้อมูลเสีย (`backupAndRecoverCorruptedChapter`) สำรองข้อมูลดิบความยาว 377 ตัวอักษรลง `agy_ch01_quiz_answers_corrupt_backup` ครบ 377 ตัวอักษร (ไม่มี `.slice(0,200)`) และทดสอบจำลอง `QuotaExceededError` บน `localStorage.setItem` → ระบบไม่ล่มและไม่ลบคีย์ต้นฉบับเมื่อสำรองไม่สำเร็จ | **PASS** | `lossless_recovery_check.passed = true` (`377 == 377`), `quota_blocked_safety_check.passed = true` |
| **5** | เครื่องเล่นเสียง `audio/ch01_full.mp3..ch10_full.mp3`, ปุ่ม `-10s`/`+10s`, ความเร็วเสียง `1.0x..2.0x` ทำงานครบ และคง `<audio id="audioElement">` DOM instance เดิมไว้เมื่อสลับหน้า `#lesson/V00-L01` ↔ `#progress` ↔ `#home` โดยไม่รีเซ็ตเสียง | **PASS** | `audio_retention_check.passed = true` (`same_dom_instance = true`) |
| **6** | แยกนับ `ฟังจบ X/10`, `ส่งควิซทบทวน Y/10` (คำนวณจาก `agy_chXX_quiz_submitted === 'true'` แม้ได้ `0/3` คะแนนก็นับว่าส่งแล้ว `1/10`), `คะแนนควิซทบทวน Z/30`, และ `การประเมินผ่านเล่ม: ยังไม่ได้ประเมิน` (แม้ฟังครบ `10/10` และได้คะแนนเต็ม `30/30` ก็ยังแสดง `ยังไม่ได้ประเมิน` ไม่ขึ้นว่าผ่านหลักสูตร) | **PASS** | `separated_progress_check.passed = true` (`zero_score_submitted_count = "1 / 10"`, `perfect_gate_status = "ยังไม่ได้ประเมิน"`) |
| **7** | ทดสอบ Responsive และ Smoke บน 5 ขนาดหน้าจอ (`375x812`, `390x844`, `430x932`, `768x1024`, `1280x900`) ทุกหน้าไม่มี Horizontal Overflow (`scrollWidth <= innerWidth`), มี `:focus-visible` ชัดเจน, และ `page_errors = []` | **PASS** | `responsive_viewports` ผ่านครบ 5/5 ขนาดหน้าจอ |
| **8** | ไม่มีระบบจำลอง Cloud Sync, ไม่มี Auth ปลอม, ไม่มีการตรวจให้คะแนนฝั่งเซิร์ฟเวอร์ปลอม, ไม่มีใบรับรองจำลอง, ไม่มีข้อสอบ Pre-Test จริงใน B1, และไม่มีข้อมูล `66/100` ใน Repo สาธารณะ | **PASS** | `no_private_data_or_forbidden_tokens.passed = true` |
| **9** | ไม่มีการ Merge เข้า `main` และไม่มีการ Deploy Production; ส่งมอบ Branch, Commit SHA, PR, ผลทดสอบ, ภาพหน้าจอ และแผน Rollback ครบถ้วน | **PASS** | ดูรายละเอียดด้านล่าง |

---

## 3. คำสั่งที่ใช้ทดสอบและเส้นทางไฟล์หลักฐาน (Test Commands & Evidence Paths)

### คำสั่งรันชุดทดสอบซ้ำได้ทันที
```powershell
node --check data/chapters.js
node --check data/v00-manifest.js
node --check js/storage-manager.js
python qa/b1/b1-verify.py
```

### ไฟล์หลักฐานและภาพหน้าจอในโฟลเดอร์งาน AGY
- **สคริปต์ทดสอบอัตโนมัติ Playwright:** `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\b1-verify.py`
- **ผลลัพธ์ JSON ครบทุกเคส:** `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\B1-QA-EVIDENCE.json`
- **ภาพหน้าจอ (Screenshots):**
  1. `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\screenshots\b1-desktop-1280-home.png` — หน้าแรก Learning Hub บน Desktop (`1280x900`)
  2. `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\screenshots\b1-mobile-390-home.png` — หน้าแรก Learning Hub บนมือถือ (`390x844`)
  3. `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\screenshots\b1-mobile-390-lesson-V00-L01.png` — หน้าเรียนรายบท `V00-L01` บนมือถือ (`390x844`)
  4. `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\screenshots\b1-mobile-390-progress.png` — หน้าความคืบหน้ารายบท (`#progress`) แบบการ์ดเรียงอ่านง่ายบนมือถือ (`390x844`)
  5. `d:\AI-Workspace\learning\AGY-Business-Self-Study\qa\b1\screenshots\b1-corrupt-storage-recovery.png` — แถบแจ้งเตือนและปุ่มสำรอง/กู้คืนเมื่อ `agy_ch01_quiz_answers` เสียหาย โดยที่ชิปทั้ง 10 บทและความคืบหน้าบทที่ 2 ยังอยู่ครบ

---

## 4. ข้อจำกัดของสภาพแวดล้อมทดสอบและแผนย้อนกลับ (Device Limitations & Rollback Strategy)

- **ข้อจำกัดการทดสอบอุปกรณ์จริง:** ทดสอบผ่าน Chromium Headless ด้วย Playwright จำลอง Viewport มือถือ (`375px`, `390px`, `430px`), แท็บเล็ต (`768px`), และเดสก์ท็อป (`1280px`) ครบทุกเส้นทางแล้ว สำหรับพฤติกรรมเฉพาะของ iOS Safari จริง (เช่น Autoplay Policy ที่ต้องให้ผู้ใช้กดปุ่ม Play เองครั้งแรก) โค้ดยังคงใช้ `<audio id="audioElement" preload="metadata" playsinline webkit-playsinline>` ตัวเดิมที่ผ่านการทดสอบบนมือถือในเฟสก่อนหน้าแล้ว 100%
- **แผนย้อนกลับ (Rollback Strategy):**
  1. ขณะนี้ `main` ยังอยู่ที่ `6a855230644afdef93eac8644a4d7e788717b730` จึงยังไม่มีผลกระทบใดๆ ต่อ Production (GitHub Pages)
  2. เนื่องจาก `js/storage-manager.js` ไม่มีการลบหรือเปลี่ยนชื่อคีย์เดิม (`agy_v00_current_chapter`, `agy_ch01..10_*`) หากต้องสลับกลับไปใช้ `main` ข้อมูลความคืบหน้าเดิมของผู้เรียนในเบราว์เซอร์จะยังคงใช้งานกับโค้ดบน `main` ได้ทันที 100%
