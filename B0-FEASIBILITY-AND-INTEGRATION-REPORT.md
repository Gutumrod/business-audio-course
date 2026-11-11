# WSTERA Academy × AGY Business Audio Courseware — B0 Integration & Feasibility Report

- **Document ID:** `AGY-B0-FEASIBILITY-v1.0`
- **Date:** 2026-10-10
- **Author:** AGY (Implementation Lead / Audio Specialist)
- **Reviewed Against:** `D:\AI-Workspace\learning\Business-Self-Study\platform\` (`00` through `04` + `B0-LEARNER-FLOW-PROTOTYPE.html` + `curriculum/COURSE-MANIFEST.json`)
- **Inspected AGY Repo:** `Gutumrod/business-audio-course` (`d:\AI-Workspace\learning\AGY-Business-Self-Study`, branch `main` @ `6a85523`)
- **Scope Status:** **B0 READ-ONLY RECON & ARCHITECTURE PLAN ONLY** (No website code modified, no database created, no deploy/merge executed in this step)

---

## Executive Summary (สรุปผลการประเมินความเป็นไปได้)

จากการตรวจสอบโครงสร้างปัจจุบันของ `Gutumrod/business-audio-course` เทียบกับแผนสถาปัตยกรรมของ GPT (`00-LEARNING-PLATFORM-MASTER-PLAN.md` ถึง `04-B0-HANDOFF-TO-AGY.md`) สรุปได้ว่า **สามารถต่อยอด (Wrap & Extend) จากฐานโค้ดเดิมได้ทันทีโดยไม่ต้องรื้อสร้างระบบเสียงหรือคลังเนื้อหา V00 ใหม่** โดยมีหัวใจสำคัญดังนี้:

1. **Reuse ได้ทันที 100%:** ไฟล์เสียง `audio/ch01_full.mp3` – `ch10_full.mp3`, `audio/durations.json`, โครงสร้างข้อมูล `data/chapters.js`, และกลไก Audio Engine ใน `index.html` นำมาใช้ต่อได้ทั้งหมดโดยไม่แตะต้องสายพานการผลิตเสียง
2. **จุดที่ต้องแก้ด่วนใน B1:**
   - แก้บั๊ก `JSON.parse(localStorage.getItem(...))` ที่ไม่มี `try/catch` และ Schema Guard (บรรทัด `1462` และ `1594` ของ `index.html`) ซึ่งทำให้หน้าเว็บล่ม (`0 chapters rendered`) หากค่าใน `localStorage` เสียหาย
   - ปรับข้อความสรุปผลและแยกสถานะ **ฟังจบ (`audio_completed`)** ออกจาก **ทำแบบฝึกท้ายบท (`practice_quiz_submitted`)** และ **ผ่านเกณฑ์หลักสูตร (`mastery_confirmed`)** อย่างเด็ดขาด
   - ยกเลิกการซิงก์ไฟล์ซ้ำซ้อนใน `audio-course/` และกำหนดให้ Root (`index.html`, `data/`, `audio/`) เป็น Canonical Publish Path เพียงจุดเดียวบน GitHub Pages

---

## 1. ระบบเดิมส่วนไหนนำมาใช้ต่อได้โดยไม่ต้องเขียนใหม่ (Mapping to Handoff Section A & E)

### 1.1 แผนผังไฟล์และฟังก์ชันเดิมใน `Gutumrod/business-audio-course` (Section A: Source File Map)

| หมวดหมู่ | ไฟล์ใน Repo ปัจจุบัน | ฟังก์ชัน / โครงสร้างหลัก (พร้อมบรรทัดใน `index.html` @ `6a85523`) | สถานะการนำมาใช้ต่อ (Reuse Status) |
| :--- | :--- | :--- | :--- |
| **Canonical Entry** | `index.html` (Root) | SPA Shell, CSS Design Tokens (`:root` บรรทัด `19–46`), Layout & Responsive Grid | **Reuse + Wrap:** ใช้เป็นโครงหลักและเพิ่ม View Router (`home`, `pretest`, `lesson`, `progress`, `help`) |
| **Duplicate Copy** | `audio-course/index.html`, `audio-course/audio/ch01_full.mp3` | สำเนาซ้ำจากช่วงพัฒนา 초기 | **Deprecate:** ไม่ใช้เป็น Publish Path อีกต่อไป (ดูหัวข้อ 2.2) |
| **V00 Content Store** | `data/chapters.js` | `window.COURSE_CHAPTERS` (Array 10 บท: `id`, `code`, `tag`, `title`, `shortTitle`, `audio`, `duration`, `durationSec`, `objective`, `contentHtml`, `quiz[3]`) | **Reuse 100%:** คงเนื้อหาและโครงสร้างเดิมไว้ และห่อด้วย `V00` Manifest Adapter |
| **Audio Assets** | `audio/ch01_full.mp3` – `audio/ch10_full.mp3`, `audio/durations.json` | ไฟล์เสียงพากย์ `Sadaltager` 10 บท (รวม `30:06` นาที) + JSON ความยาวเสียงรายบท | **Freeze & Reuse 100%:** ห้ามย้ายพาธ ห้ามเรนเดอร์ใหม่ เพื่อให้ URL เดิมทำงานได้ต่อเนื่อง |
| **Audio Player Engine** | `index.html` (บรรทัด `1842–1929`) | `togglePlay()` (`1846`), `syncMetadata()` (`1885`), `seekBackBtn`/`seekForwardBtn` ±10s (`1871–1876`), `speedBtn` `[1.0, 1.25, 1.5, 2.0]` (`1878`), `scrubber` drag/input (`1905–1912`), `ended` listener (`1914`), `Spacebar` shortcut (`1924`) | **Reuse 100%:** เสถียรแล้ว รองรับ `playsinline` และ Resume จากจุดที่ฟังค้างไว้ |
| **Chapter Switcher & Reader** | `index.html` (บรรทัด `1510–1558`, `1702–1808`) | `selectChapter(chId, shouldScroll)` (`1702`), `renderNavigationUI()` (`1510`), `openDrawer()`/`closeDrawer()` (`1779–1786`), `editorialContent.innerHTML = ch.contentHtml` (`1717`) | **Reuse + Refactor:** แยกโหมดแสดงผลภายในบทเรียนเป็น Tabs (`read`, `listen`, `practice`, `verify`) |
| **Formative Quiz Engine** | `index.html` (บรรทัด `1461–1480`, `1560–1700`, `1809–1840`) | `getChapterQuizScore(ch)` (`1461`), `renderQuiz(ch)` (`1589`), `refreshQuizControls(ch)` (`1662`), `renderAnswerKeyPanel(ch, userAnswers)` (`1560`), Submit-before-key flow (`1810`) | **Reuse with Guard:** ใช้เป็น Formative Practice ประจำบท (ไม่ใช่ Gate ผ่านหลักสูตร) + เพิ่ม Safe JSON Guard |
| **LocalStorage Keys** | `index.html` (บรรทัด `1440–1452`) | `agy_v00_current_chapter`, `agy_chXX_audio_time`, `agy_chXX_completed`, `agy_chXX_quiz_answers`, `agy_chXX_quiz_submitted` | **Preserve 100%:** เก็บคีย์ชุดเดิมไว้ทั้งหมดเพื่อไม่ให้ความคืบหน้าของผู้เรียนปัจจุบันหาย |

### 1.2 การคงประสิทธิภาพเครื่องเล่นเสียงและการทดสอบข้ามอุปกรณ์ (Section E: Player Preservation)
- **สิ่งที่ยืนยันแล้วว่าทำงานได้ดีและจะไม่แตะต้อง:**
  - `<audio id="audioElement" preload="metadata" playsinline webkit-playsinline>` พร้อม Fallback `audio.load(); audio.play()` เมื่อ Mobile Browser บล็อกการเล่นครั้งแรก
  - การจำเวลาฟังค้างทุกๆ 3 วินาที (`Math.floor(audio.currentTime) % 3 === 0`) และการกู้คืนเวลาเมื่อกด Play ครั้งแรก (`isTimeRestored` flag ใน `togglePlay()`) ซึ่งป้องกันปัญหา iOS Safari รีเซ็ต `currentTime` ก่อน `play()`
  - การวาง Player แบบ In-flow Card (`.player-island`) ที่ **ไม่ใช่ Sticky Bottom Bar ทับเนื้อหา** จึงไม่บังฟอร์มข้อสอบหรือปุ่มกดบนจอมือถือ
- **ข้อจำกัดที่ยังไม่ได้ทดสอบจริง (Untested Scenarios — ต้องตรวจใน B1/B2):**
  - ยังไม่ได้ทดสอบบนเครื่อง iPhone Safari จริง (Physical Device) และ Android Chrome จริงครบทั้ง 10 ไฟล์เสียง (ปัจจุบันยืนยันผ่าน Chromium 390px emulation และ HTTP 200 เท่านั้น)
  - ยังไม่ได้เพิ่ม UI แจ้งเตือนกรณีโหลดไฟล์เสียงไม่สำเร็จเมื่อเน็ตหลุด (`audio.addEventListener('error', ...)` พร้อมปุ่ม `[ ลองโหลดเสียงใหม่ ]`) ซึ่งจะเพิ่มใน B1/B2

---

## 2. ต้องแก้ไขหรือเพิ่มไฟล์ใดบ้าง (Mapping to Handoff Section B & G)

### 2.1 การกำหนด Canonical Publish Path (แก้ปัญหาไฟล์ซ้ำ `root` vs `audio-course/`)
- **ข้อเท็จจริง:** GitHub Pages ของ `Gutumrod/business-audio-course` เสิร์ฟจาก **Root Directory (`/`)** โดยตรง ส่วนโฟลเดอร์ `audio-course/` เป็นเพียงโฟลเดอร์สคริปต์ทำงานเบื้องหลัง (`build_all_scripts.py`, `generate_all_chapters.py`, `scripts/`) ที่มีสำเนา `audio-course/index.html` และ `audio-course/audio/ch01_full.mp3` ค้างอยู่
- **แนวทางจัดการใน B1:**
  1. กำหนดให้ **Root (`/index.html`, `/data/*`, `/audio/*`) เป็น Canonical Web Root เพียงจุดเดียว**
  2. ลบสำเนาซ้ำ `audio-course/index.html`, `audio-course/test-player.html`, และ `audio-course/audio/ch01_full.mp3` ออกจาก Git (คงไว้เฉพาะ `audio-course/*.py` และ `audio-course/scripts/*.txt` สำหรับงานผลิตเสียงของ AGY) เพื่อตัดความเสี่ยงเรื่องการแก้ไฟล์ผิดจุด 100%

### 2.2 รายการไฟล์ที่ต้องแก้ไขและเพิ่มใหม่ (แยกตาม Batch B1–B3)

| ไฟล์ | สถานะ | Batch | หน้าที่และการเปลี่ยนแปลง |
| :--- | :---: | :---: | :--- |
| `index.html` | **Modify** | B1–B3 | ปรับเป็น Learning Hub Shell รองรับ Hash View Navigation (`#home`, `#pretest`, `#lesson/V00-L01`, `#progress`, `#help`), เพิ่ม Storage Guard, แยกสถานะการเรียนออกจากสถานะสอบผ่าน |
| `data/chapters.js` | **Keep (Read-only Content)** | B1 | คงข้อมูลบทเรียนและควิซ 10 บทเดิมไว้ทุกตัวอักษร อาจเพิ่มเฉพาะฟิลด์ Metadata (`lesson_id: "V00-L01"`, `volume_id: "V00"`) หรือแมปผ่าน Adapter |
| `data/v00-manifest.js` | **New** | B1–B2 | Adapter ผูก Canonical IDs (`program_id: "MBAI-SELF-01"`, `volume_id: "V00"`, `legacy_agy_alias: "vol-01"`, `lesson_id: "V00-L01".."V00-L10"`), คำศัพท์ (Glossary Tooltips), และโจทย์ฝึกคิด Track A / Track B เฉพาะที่ผ่านการอนุมัติจาก Academy |
| `data/v00-pretest-questions.js` | **New** | B3 | โครงคำถาม Pre-Test 24 ข้อ (16 ปรนัย + 8 อธิบายวิธีคิด) **เฉพาะตัวโจทย์และคำอธิบายศัพท์ที่เป็นกลาง (ไม่มีเฉลย `ANSWER-KEY.md` และไม่มีเกณฑ์ให้คะแนนลับฝังในไฟล์สาธารณะ)** |
| `js/storage-manager.js` | **New** | B1 | ระบบจัดการ LocalStorage แบบปลอดภัย (`safeReadJson`, Schema Validator, Non-destructive Migration/Adapter สำหรับ `agy_chXX_*`, และฟังก์ชัน Export/Import JSON สำหรับผู้เรียน) |
| `ARCHITECTURE-AND-ROADMAP.md` | **Modify** | B1 | อัปเดตเอกสารสถาปัตยกรรมให้ตรงกับ Canonical ID ของ Academy (`V00` = Foundation Bridge 10 บท, ส่วน `V01–V12` = หลักสูตรหลัก 8 หน่วย/เล่ม) และยกเลิกใบเซอร์จำลองจากการฟังครบ |

---

## 3. จะรวมหน้าเรียน อ่านหนังสือ ฟังเสียง และแบบทดสอบอย่างไร (Mapping to Handoff Section B & Wireframe Screens A–E)

### 3.1 สถาปัตยกรรม Navigation: Hash-based Single-Page Application (SPA) ใน `index.html` เดียว
เพื่อไม่ให้ URL เดิม (`https://gutumrod.github.io/business-audio-course/`) พัง และไม่ต้องพึ่งพา Server-side Routing บน GitHub Pages เสนอให้ใช้ **Hash-based View Router** ภายใน `index.html` เดียว:
- `#home` (หรือเปิดหน้าเว็บปกติ): **Screen A (First Visit)** หรือ **Screen C (Returning Learner)** ตามสถานะในเครื่อง
- `#pretest/V00`: **Screen B (Pre-Test 24 ข้อ — แบ่งชุดละ 4 ข้อ x 6 หน้า)**
- `#lesson/V00-L01` ถึง `#lesson/V00-L10`: **Screen D (Guided Lesson View)**
- `#progress`: **Screen E (สรุปความคืบหน้าแยกสถานะ: ฟังเสียง / อ่านเนื้อหา / แบบฝึกท้ายบท / แบบฝึก Track A-B / สถานะประเมินหลักสูตร)**
- `#help`: คู่มือการใช้งาน, คำศัพท์พื้นฐาน (Glossary), และการสำรองข้อมูล (Export/Import Local Data)

### 3.2 การรวมโหมดเรียนภายในหน้าบทเรียน (`#lesson/V00-LXX` — Screen D)
แทนที่จะแสดงเนื้อหายาวเหยียดรวดเดียวเหมือนเดิม จะจัดโครงสร้างในหน้าบทเรียนเป็น **4 โหมด (Sub-tabs ภายในบทเดียว)** ที่ใช้ข้อมูลจาก `data/chapters.js` ร่วมกับ `data/v00-manifest.js`:
1. **แท็บ `[ 📖 อ่านเนื้อหา ]` (Read):**
   - แสดง `ch.contentHtml` พร้อมปุ่มปรับขนาดตัวอักษร (`A- / A / A+`: `16px / 18px / 20px`)
   - รองรับ Glossary Tooltip แตะคำศัพท์ธุรกิจเพื่อดูคำอธิบายภาษาไทยเข้าใจง่าย
   - มีปุ่ม `[ ✓ อ่านจบบทนี้แล้ว ]` บันทึกสถานะ `reading_acknowledged` แยกจากเสียง
2. **แท็บ `[ 🎧 ฟังเสียง ]` (Listen):**
   - แสดง `.player-island` ตัวเดิมของ AGY (`play/pause`, `-10s/+10s`, `1.0x–2.0x`, `scrubber`, `resume`)
   - แสดงข้อความกำกับชัดเจน: *“การฟังจบเป็นการบันทึกกิจกรรมการเรียน ไม่ใช่การสอบผ่านบทเรียน”*
   - แสดงบทอ่านประกอบด้านล่างเครื่องเล่นเพื่อให้คนฟังอ่านตามได้ทันที
3. **แท็บ `[ 💡 ลองคิด & ฝึก (Track A / B) ]` (Practice):**
   - สวิตช์สลับบริบทการฝึก **Track A (เจ้าของธุรกิจ/หน้างานจริง)** และ **Track B (วิเคราะห์/อ้างอิงวิชาการ)** โดยเนื้อหาหลักและเกณฑ์ผ่านเหมือนกัน
   - ช่องพิมพ์คำตอบ (`<textarea>`) ที่บันทึกฉบับร่างอัตโนมัติลงเครื่อง (`practice_draft`) พร้อมปุ่มคัดลอกคำตอบไปส่งตรวจ (แสดงสถานะ `รอการตรวจประเมิน (Review Pending)` ไม่แอบอ้างว่า AI ตรวจให้ผ่านอัตโนมัติ)
4. **แท็บ `[ ✅ ทดสอบท้ายบท (3 ข้อ) ]` (Verify / Formative Quiz):**
   - ใช้ระบบควิซ 3 ข้อประจำบทที่ปรับเป็นโหมด **เลือกครบ 3 ข้อ → กดส่งคำตอบ → ค่อยเปิดดูคำอธิบาย**
   - ระบุชัดเจนว่าเป็น **แบบฝึกทบทวนความเข้าใจประจำบท (Formative Check)** ไม่ใช่การสอบผ่าน Gate ของเล่ม V00

---

## 4. จะเพิ่ม Pre-Test ก่อนเริ่มเรียน และบันทึกผลโดยไม่ทำลายข้อมูลเดิมอย่างไร (Mapping to Handoff Section C)

### 4.1 กลยุทธ์ Canonical ID และการรักษาข้อมูลเดิมใน `localStorage` (Zero Data Loss)
ปัจจุบันผู้เรียนที่มีข้อมูลอยู่ในเบราว์เซอร์ใช้คีย์ชุด `agy_v00_current_chapter` และ `agy_ch01_*` ถึง `agy_ch10_*` อยู่แล้ว ดังนั้นเราจะใช้ **Non-Destructive Dual-Read Adapter** ดังนี้:
- **ห้ามลบหรือเปลี่ยนชื่อคีย์เดิม (`agy_ch01_*` .. `agy_ch10_*`)**: ระบบเล่นเสียงและควิซท้ายบทจะอ่าน-เขียนคีย์เดิมต่อไปเพื่อให้ทำงานร่วมกับข้อมูลเดิมได้ทันทีและ Rollback กลับได้ทุกเมื่อ
- **เพิ่ม Namespace ใหม่สำหรับระบบ Academy (`wstera_v00_*`)** สำหรับข้อมูลส่วนขยายที่ยังไม่เคยมีในระบบเดิม:
  - `wstera_v00_learner_meta`: `{ schema_version: 1, selected_track: "A" | "B", baseline_status: "none" | "draft" | "submitted_local" | "verified_external_import", updated_at }`
  - `wstera_v00_pretest_attempt`: เก็บข้อมูล Pre-Test 24 ข้อ (เฉพาะกรณีทำใหม่บนเว็บ)
  - `wstera_v00_lesson_state`: เก็บสถานะ `reading_acknowledged` และ `practice_draft` ของ `V00-L01` ถึง `V00-L10`

### 4.2 การออกแบบระบบ Pre-Test 24 ข้อ (16 ปรนัย + 8 อธิบายวิธีคิด)
1. **การแบ่งหน้า (Chunked 4 Items / Batch):** แบ่ง 24 ข้อออกเป็น 6 ชุด ชุดละ 4 ข้อ (`ข้อ 1–4`, `5–8`, `9–12`, `13–16` เป็นปรนัย และ `17–20`, `21–24` เป็นอัตนัยแสดงวิธีคิดและเหตุผล)
2. **Autosave & Pause:** ทุกครั้งที่เลือกตัวเลือกหรือพิมพ์ข้อความ ระบบจะบันทึกลง `wstera_v00_pretest_attempt` (`state: "draft"`, `updated_at`) ทันที ผู้เรียนกด `[ บันทึกร่างและพัก ]` แล้วกลับมาทำต่อจากข้อเดิมได้ตลอดเวลา
3. **การส่งคำตอบและป้องกันการแอบให้คะแนนมั่ว:**
   - ก่อนส่งมีหน้าสรุปจำนวนข้อที่ตอบแล้วและข้อที่เว้นว่างให้ยืนยัน 1 ครั้ง
   - เมื่อกดส่ง สถานะจะเปลี่ยนเป็น `submitted` (ล็อกการแก้ไขทับ Attempt เดิม)
   - **ไม่ฝังเฉลย (`ANSWER-KEY.md`) หรือสูตรให้คะแนนข้อเขียนไว้ใน JavaScript สาธารณะเด็ดขาด** หน้าสรุปหลังส่งจะแสดงสถานะ `บันทึกคำตอบก่อนเรียนแล้ว — ข้อเขียนรอผู้ตรวจประเมิน (Review Pending)` และพาเข้าสู่บทเรียนที่ 1 ได้ทันที

### 4.3 การปกป้องผล Pre-Test เดิม `66/100` ของ Learner A
- ผล Pre-Test เดิม `66/100` ของ Learner A ใน `curriculum/learner-records/A/V00-G0-PRETEST-2026-10-10.md` เป็นความลับใน Private Repo ของ Academy **ห้ามนำไฟล์หรือตัวเลข `66/100` ไป Hardcode ในโค้ดเว็บสาธารณะเด็ดขาด**
- ในหน้า Home ของเว็บจะรองรับโหมด **"ยืนยันว่ามีผลประเมินก่อนเรียนแล้ว / นำเข้าหลักฐานเดิม (Import / Mark Existing Baseline)"**:
  - ทำให้ Learner A สามารถกดเข้าเรียนบทที่ 1–10 ต่อได้ทันทีโดย **ไม่ถูกบังคับให้ทำ Pre-Test ซ้ำ**
  - และหากกดทำข้อสอบในอนาคต ระบบจะเก็บเป็น `attempt_id` ใหม่แยกตามประเภท (`posttest` ชุดคำถามใหม่เมื่อพร้อม) โดยไม่เขียนทับประวัติ Baseline `G0` เดิม

---

## 5. จะแก้ปัญหาข้อมูล Quiz ใน `localStorage` เสียจนหน้าเว็บทำงานผิดปกติอย่างไร (Mapping to Handoff Section D)

### 5.1 สาเหตุของบั๊กที่ตรวจพบใน `02-B0-AGY-RECON-AUDIT.md`
ใน `index.html` ปัจจุบัน มีการเรียก `JSON.parse()` โดยตรงโดยไม่มี `try/catch` และไม่มีการตรวจชนิดข้อมูล (Schema Validation) 2 จุด:
1. บรรทัด `1462` ใน `getChapterQuizScore(ch)`:
   ```javascript
   const saved = JSON.parse(localStorage.getItem(keyQuizAnswers(ch.id)) || '{}');
   ```
2. บรรทัด `1594` ใน `renderQuiz(ch)`:
   ```javascript
   let userAnswers = JSON.parse(localStorage.getItem(keyQuizAnswers(ch.id)) || '{}');
   ```
เมื่อคีย์ใดคีย์หนึ่ง เช่น `agy_ch01_quiz_answers` มีค่าไม่ใช่ JSON ที่ถูกต้อง (เช่น `"BROKEN_NOT_JSON"`) หรือเป็น JSON ชนิดอื่นที่ไม่ใช่ Object (เช่น `null`, `"123"`, `[]`) ฟังก์ชัน `selectChapter()` และ `renderNavigationUI()` จะเกิด Uncaught `SyntaxError` / `TypeError` ทันที ส่งผลให้แถบเลือกบททั้ง 10 บทไม่ถูกสร้าง (`chapter_chips = 0`) และหน้าเว็บค้าง

### 5.2 วิธีแก้ไขระดับโค้ด (Guarded Parse + Per-Key Isolation + Self-Healing)
สร้างฟังก์ชัน `safeReadQuizAnswers(chId)` ใน `js/storage-manager.js` (หรือใน `index.html`) แทนการใช้ `JSON.parse` โดยตรงทุกจุด:

```javascript
function safeReadQuizAnswers(chId) {
  const key = keyQuizAnswers(chId);
  const raw = localStorage.getItem(key);
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    // Validate plain object shape and valid option letters ('A'|'B'|'C'|'D')
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('Invalid quiz answer payload shape');
    }
    const clean = {};
    for (const [k, v] of Object.entries(parsed)) {
      if (['A', 'B', 'C', 'D'].includes(v)) {
        clean[String(k)] = v;
      }
    }
    return clean;
  } catch (err) {
    console.warn(`[StorageGuard] Corrupted localStorage key "${key}" recovered safely:`, err.message);
    // Quarantine corrupted value for debugging without breaking the app, then reset only the broken key
    try {
      localStorage.setItem(`${key}_corrupted_backup`, String(raw).slice(0, 200));
      localStorage.removeItem(key);
      localStorage.removeItem(keyQuizSubmitted(chId));
    } catch (_) {}
    showNonBlockingStorageNotice(`พบข้อมูลแบบฝึกหัดของบทที่ ${chId} ในเบราว์เซอร์ผิดรูปแบบ ระบบได้รีเซ็ตเฉพาะบทที่ ${chId} ให้แล้ว (บทอื่นยังอยู่ครบ)`);
    return {};
  }
}
```
- **ผลลัพธ์:** ต่อให้ `agy_ch01_quiz_answers` พังเสียหาย หน้าเว็บก็จะยังคงโหลดครบทั้ง 10 บท (`chapter_chips === 10`), ข้อมูลบทที่ 2–10 และเวลาเสียงที่ฟังค้างไว้ (`agy_ch01_audio_time`) ไม่สูญหาย และแสดงแถบแจ้งเตือนเล็กๆ แบบไม่บล็อกหน้าจอ

### 5.3 การแก้ไขความขัดแย้งเชิงวิชาการของ Quiz 30 ข้อในหน้าเว็บปัจจุบัน
- ใน `index.html` บรรทัด `1498–1504` เดิมแสดงข้อความ `✓ ผ่านเกณฑ์` เมื่อฟังครบ 10 บทและได้คะแนนควิซรวม `>= 24/30`
- **แผนแก้ไขใน B1:**
  - เปลี่ยนป้ายสถานะจาก `✓ ผ่านเกณฑ์` เป็น **`ฟังครบ 10 บท · ทำแบบฝึกทบทวนครบ`**
  - เพิ่มป้ายสถานะแยกต่างหากสำหรับ **สถานะการผ่านมาตรฐานหลักสูตร (Academy Volume Gate): `รอการประเมินหลังเรียน (Post-Test & Rubric Review)`** เพื่อไม่ให้ผู้เรียนเข้าใจผิดว่าการทำควิซปรนัยท้ายบท 30 ข้อคือการจบหลักสูตร V00 อย่างเป็นทางการ

---

## 6. จะรองรับฐานข้อมูลและระบบผู้เรียนในอนาคตอย่างไร (Mapping to Handoff Section F)

### 6.1 การแยกชั้นข้อมูลด้วย `StorageAdapter` Pattern (Static Public vs. Authenticated Cloud)
เพื่อไม่ให้ต้องรื้อโค้ด UI เมื่อเปลี่ยนจาก LocalStorage (ระยะ P1–P2 / B1–B3) ไปเป็น Supabase (ระยะ P3 / B4 หลังได้รับอนุมัติ) เราจะออกแบบชั้นบันทึกข้อมูลเป็น Interface เดียว:
- `LearningStore.getProgress(volumeId)`
- `LearningStore.saveEvent(eventType, payload)` (รองรับ Event Schema ตาม Master Plan ข้อ 6: `lesson_viewed`, `audio_position`, `audio_completed`, `reading_acknowledged`, `quiz_draft_saved`, `quiz_submitted`, `practice_submitted` พร้อม `idempotency_key` และ `timestamp`)
- `LearningStore.exportSnapshot()` / `LearningStore.importSnapshot(json)`

### 6.2 กฎเหล็กด้านความปลอดภัยและความเป็นส่วนตัว (Strict Security & Privacy Boundary)
1. **ระยะ B1–B3 (Public GitHub Pages — Local Only):**
   - ข้อมูลทุกอย่างเก็บในเบราว์เซอร์ของผู้เรียนเท่านั้น และแสดงป้ายสถานะชัดเจนว่า **`สถานะบันทึก: เก็บในอุปกรณ์นี้เท่านั้น (ยังไม่ซิงก์ข้ามเครื่อง)`**
   - มีปุ่ม **ส่งออกไฟล์ความคืบหน้า (`.json`)** และ **นำเข้าไฟล์ความคืบหน้า** เพื่อให้ผู้เรียนสำรองข้อมูลด้วยตนเองได้โดยไม่ต้องส่งข้อมูลขึ้นที่สาธารณะ
2. **ระยะ B4 (เมื่อ Owner อนุมัติให้เชื่อม Supabase ในอนาคต):**
   - ใช้เฉพาะ `SUPABASE_URL` และ `SUPABASE_ANON_KEY` ร่วมกับ **Supabase Auth + Row-Level Security (`auth.uid() = learner_id`)** เท่านั้น
   - **ห้ามใส่ `service_role` key, เฉลยข้อสอบมาตรฐาน (`ANSWER-KEY.md`), หรือข้อมูลส่วนตัวของ Learner A/B ลงใน Frontend Bundle เด็ดขาด**
   - การตรวจให้คะแนนที่มีผลต่อการผ่าน Gate (`volume_assessment`, `posttest`, และการบันทึกผล Baseline `66/100` จากระบบกลาง) ต้องทำงานผ่าน **Supabase Edge Functions / Server-side Verification** เท่านั้น

---

## 7. ความเสี่ยง ข้อจำกัด จุดขัดแย้งกับสถาปัตยกรรมเดิม และทางเลือกที่เสนอ (Mapping to Handoff Section G)

### 7.1 จุดขัดแย้งที่พบกับสถาปัตยกรรมเดิม (`ARCHITECTURE-AND-ROADMAP.md`)

| ประเด็นขัดแย้ง | สิ่งที่เขียนไว้ใน `ARCHITECTURE-AND-ROADMAP.md` เดิมของ AGY | มาตรฐานของ WSTERA Academy (`COURSE-MANIFEST.json` & Master Plan) | แนวทางแก้ไขที่เสนอ |
| :--- | :--- | :--- | :--- |
| **1. รหัสเรียกชื่อเล่ม** | เรียกหนังสือปูพื้นฐาน 10 บทว่า `vol-01` (`agy_v01_*`) | กำหนดให้หนังสือปูพื้นฐาน 10 บทคือ **`V00` (Foundation Bridge)** ส่วน **`V01`** คือเล่ม "ธุรกิจ เศรษฐศาสตร์ และวิธีคิดของผู้บริหาร" (8 หน่วยเรียน, 45 ชม.) | ใช้ **`V00`** เป็น Canonical ID ทุกจุดใน UI และเอกสารใหม่ โดยคง Alias รองรับคีย์ `agy_v00_*` และ `agy_ch01_*` เดิมในโค้ด |
| **2. โครงสร้างบทเรียนของเล่มถัดไป** | สมมติว่าทุกเล่มจะมี 10 บทเหมือนกัน | `V00` มี **10 บท (Chapters)** แต่ `V01–V12` มีเล่มละ **8 หน่วย (Units `XX.1` – `XX.8`)** | ปรับ UI Component ให้ขับเคลื่อนด้วยจำนวนรายการจริงใน Manifest (`lessons.length`) ไม่ Hardcode เลข `10` หรือ `30` ในโค้ด |
| **3. เกณฑ์การผ่านและใบเซอร์** | เฟส 3 เดิมระบุว่าจะทำใบ Certificate จำลองเมื่อได้คะแนนควิซ `24/30` | **ห้ามออกใบเซอร์หรือให้ผ่านหลักสูตรจากควิซท้ายบทหรือการฟังเสียงจบ** ต้องผ่านเกณฑ์ `>= 80/100` + Core `>= 80%` + ไม่มี Critical Fail + Reviewer/Owner Sign-off | ตัดระบบออกใบเซอร์อัตโนมัติหน้าเว็บออก และแสดงแยกสถานะชัดเจนตามข้อ 5.3 |
| **4. ความยาวเสียงเทียบเวลาเรียนจริง** | ไฟล์เสียง 10 บทรวม `30:06` นาที | `COURSE-MANIFEST.json` กำหนดเวลาเรียน `V00` ไว้ `8–12 ชั่วโมง` | ระบุใน UI หน้าปกและหน้าบทเรียนให้ชัดเจนว่า **เสียงบรรยาย (`~3 นาที/บท`) เป็นบทสรุปนำทางเพื่อช่วยทำความเข้าใจ** ผู้เรียนต้องอ่านเนื้อหา ศึกษาตารางกรณีศึกษา และทำแบบฝึกหัดควบคู่ไปด้วย |

---

### 7.2 ทางเลือกเชิงสถาปัตยกรรมที่ต้องขอคำตัดสินใจ (Open Architectural Options for GPT & Owner)

#### ทางเลือกที่ 1: รูปแบบการจัดการหน้าจอ (Routing Architecture สำหรับ B1–B3)
- **Option 1A (แนะนำ): Single-Page Hash Router ใน `index.html` เดียว (`#home`, `#pretest`, `#lesson/V00-L01`, `#progress`)**
  - **ข้อดี:** เปลี่ยนหน้าเร็วทันที, เสียงไม่สะดุดหากสลับดูคำศัพท์/ความคืบหน้า, ใช้ร่วมกับ GitHub Pages ได้ 100% โดยไม่มีปัญหา 404 เวลา Refresh, รักษา URL เดิมได้สมบูรณ์
  - **ข้อเสีย:** ไฟล์ `index.html` (หรือไฟล์ JS แยกโมดูล) จะต้องดูแล State การสลับหน้าให้สะอาด
- **Option 1B: แยกไฟล์ HTML ตามหน้า (`index.html`, `pretest.html`, `lesson.html`, `progress.html`)**
  - **ข้อดี:** แยกไฟล์ตามหน้าจอชัดเจน
  - **ข้อเสีย:** เวลาเปลี่ยนหน้าเบราว์เซอร์ต้องโหลด CSS/JS ใหม่ทุกครั้ง และลิงก์เดิมที่ชี้มาที่ Root `index.html` ซึ่งเคยเปิดบทที่ 1 ทันทีจะต้องทำ Redirect เพิ่ม

#### ทางเลือกที่ 2: แหล่งคำถามสำหรับหน้า UI ของ Pre-Test ในระยะ B3 (ก่อนระบบ Backend พร้อม)
- เนื่องจาก `DIAGNOSTIC-PLAIN-TH-v1.1.md` อยู่ในสถานะ `STRUCTURAL QA PASS / ACADEMIC REVIEW PENDING` และห้ามนำเฉลยขึ้นเว็บสาธารณะ:
- **Option 2A (แนะนำตาม Implementation Brief ข้อ 9):** สร้างโครง UI Pre-Test 24 ข้อใน B3 ให้รองรับการโหลดชุดคำถามจากไฟล์ `data/v00-pretest-questions.js` โดยในระหว่างรอ Owner/GPT อนุมัติชุดคำถามจริง ให้ใส่ชุดคำถามตัวอย่าง (Synthetic/Preview Fixture) หรือใส่เฉพาะโจทย์ `v1.1` ที่ตัดเฉลยและตัดเกณฑ์ตรวจออกทั้งหมดหลัง GPT อนุมัติ
- **Option 2B:** ชะลอการเปิดปุ่มกดเข้าหน้าทำ Pre-Test จริงใน B1–B2 (แสดงป้ายสถานะ "เตรียมเปิดใช้งานหลังอนุมัติชุดคำถาม") แล้วเปิดให้กดทำใน B3 ทันทีที่ GPT อนุมัติไฟล์คำถาม

---

### 7.3 แผนแบ่งงานและประเมินความซับซ้อน (Implementation Batches & Effort Estimate)

| Batch | ขอบเขตงานที่จะลงมือทำ (หลังได้รับอนุมัติ) | ไฟล์ที่เกี่ยวข้อง | ระดับความซับซ้อน |
| :---: | :--- | :--- | :---: |
| **B1 — Learning Hub & Storage Guard** | 1. แก้บั๊ก `safeReadQuizAnswers()` ป้องกัน `localStorage` พัง<br>2. สร้างหน้า Home (`#home` — First Visit & Returning State) + แถบสถานะ `เก็บในอุปกรณ์นี้`<br>3. ปรับข้อความสถานะแยก "ฟังจบ/ทำควิซทบทวน" ออกจาก "ผ่านเกณฑ์หลักสูตร"<br>4. ลบสำเนาซ้ำใน `audio-course/index.html` | `index.html`, `js/storage-manager.js`, `data/v00-manifest.js`, `ARCHITECTURE-AND-ROADMAP.md` | **ต่ำ–ปานกลาง** (พร้อมทำทันทีหลังอนุมัติ) |
| **B2 — Guided Lesson Modes** | 1. แยกโหมดในหน้าบทเรียน (`อ่าน | ฟังเสียง | ลองคิด (Track A/B) | ทดสอบท้ายบท`)<br>2. เพิ่มปุ่มปรับขนาดตัวอักษร (`A-/A/A+`), Glossary Tooltip, และช่องบันทึกแบบฝึกหัด Track A/B ลงเครื่อง | `index.html`, `data/v00-manifest.js` | **ปานกลาง** |
| **B3 — Pre-Test 24-Item Shell** | 1. สร้างหน้า `#pretest/V00` แบ่ง 4 ข้อ/หน้า (16 ปรนัย + 8 อธิบายวิธีคิด)<br>2. ระบบ Autosave ร่างคำตอบ, พักแล้วทำต่อ, ยืนยันก่อนส่ง, สถานะ `รอตรวจประเมิน`, และปุ่ม Export/Import JSON | `index.html`, `data/v00-pretest-questions.js`, `js/storage-manager.js` | **ปานกลาง** |
| **B4 — Cloud Sync (Deferred)** | เชื่อมต่อ Supabase Auth + RLS + Edge Functions (ทำต่อเมื่อผ่าน Gate อนุมัติแยกต่างหากเท่านั้น) | Deferred | **สูง (รออนุมัติแยก)** |

---

## สรุปความพร้อมของ AGY (Readiness Declaration)
- **ตรวจสอบเอกสารต้นทางครบทั้ง 6 ไฟล์ + `COURSE-MANIFEST.json` แล้ว**
- **ยังไม่ได้แก้ไขไฟล์หน้าเว็บ ไฟล์เสียง หรือฐานข้อมูลใดๆ ในรอบ B0 นี้ตามคำสั่ง**
- **พร้อมเริ่มพัฒนา `B1 — Home Learning Hub & Storage Guard` บน Branch แยกทันทีที่ GPT ตรวจรับรายงานนี้และ Owner อนุมัติ**
