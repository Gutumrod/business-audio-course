// ============================================================================
// WSTERA Academy — V00 Foundation Bridge Canonical Manifest & Legacy Adapter
// Program: MBAI-SELF-01 | Volume: V00 (Legacy AGY Alias: vol-01)
// Note: Does not modify data/chapters.js or audio/* assets.
// ============================================================================
(function (global) {
  "use strict";

  var chapters = Array.isArray(global.COURSE_CHAPTERS) ? global.COURSE_CHAPTERS : [];

  function pad2(n) {
    var num = parseInt(n, 10);
    return (num < 10 ? "0" : "") + String(num);
  }

  function toCanonicalLessonId(chapterNumber) {
    var num = parseInt(chapterNumber, 10);
    if (isNaN(num) || num < 1) return null;
    return "V00-L" + pad2(num);
  }

  function parseLessonIdentifier(input) {
    if (typeof input === "number" && Number.isInteger(input)) {
      return input;
    }
    if (typeof input !== "string") return null;
    var trimmed = input.trim().toUpperCase();
    // Match canonical V00-L01 .. V00-L10
    var matchCanonical = /^V00-L(\d{1,2})$/.exec(trimmed);
    if (matchCanonical) {
      return parseInt(matchCanonical[1], 10);
    }
    // Match numeric "1" .. "10" or "01" .. "10"
    if (/^\d{1,2}$/.test(trimmed)) {
      return parseInt(trimmed, 10);
    }
    return null;
  }

  var lessons = chapters.map(function (ch) {
    var chNum = parseInt(ch.id, 10);
    var code = ch.code || pad2(chNum);
    var canonicalId = "V00-L" + code;
    var questionIds = Array.isArray(ch.quiz)
      ? ch.quiz.map(function (q) { return String(q.q); })
      : [];

    return {
      lesson_id: canonicalId,
      volume_id: "V00",
      chapter_number: chNum,
      code: code,
      title: ch.title,
      short_title: ch.shortTitle || ch.title,
      objective: ch.objective,
      audio_url: ch.audio,
      duration_formatted: ch.duration,
      duration_seconds_estimate: ch.durationSec,
      legacy_keys: {
        audio_time: "agy_ch" + code + "_audio_time",
        audio_completed: "agy_ch" + code + "_completed",
        quiz_answers: "agy_ch" + code + "_quiz_answers",
        quiz_submitted: "agy_ch" + code + "_quiz_submitted"
      },
      question_ids: questionIds,
      chapter_ref: ch
    };
  });

  var V00_MANIFEST = {
    schema_version: "1.0.0",
    program_id: "MBAI-SELF-01",
    volume_id: "V00",
    legacy_agy_alias: "vol-01",
    content_version: "bridge-v1",
    release_status: "READY_FOR_OWNER_STUDY",
    title: "บริหารธุรกิจจากศูนย์",
    subtitle: "เล่มปูพื้นฐาน (Foundation Bridge) · เข้าใจธุรกิจจากภาษาไทยธรรมดาก่อนเข้าสู่ศัพท์วิชาการ",
    guided_study_hours: {
      min: 8,
      max: 12,
      label: "8–12 ชั่วโมง (อ่านเนื้อหา ศึกษาตาราง และทำแบบฝึกหัด)"
    },
    audio_summary_meta: {
      total_seconds_estimate: 1706,
      total_formatted_estimate: "28:26",
      voice_name: "Sadaltager",
      disclaimer: "ไฟล์เสียงทั้ง 10 บท (รวมประมาณ 28 นาทีครึ่ง) เป็นสื่อเสียงสรุปนำทางเพื่อช่วยให้จับประเด็นหลักได้เร็วขึ้น ไม่ใช่เวลาเรียนทั้งหมดของหลักสูตร (8–12 ชั่วโมง) และการฟังจบไม่ใช่การสอบผ่านหลักสูตร"
    },
    legacy_current_chapter_key: "agy_v00_current_chapter",
    lessons: lessons,
    glossary: [
      {
        term: "รายได้ (Revenue / ยอดขายที่รับรู้)",
        plain: "มูลค่าจากการขายสินค้าหรือบริการตามเกณฑ์ที่กำหนด ยังไม่ได้หักต้นทุน และอาจยังไม่ได้รับเป็นเงินสดทันทีหากลูกค้าค้างจ่าย"
      },
      {
        term: "กำไร (Profit / เงินส่วนที่เหลือหลังหักต้นทุนและค่าใช้จ่าย)",
        plain: "ผลต่างที่เหลือจริงหลังจากนำรายได้มาหักต้นทุนสินค้าและค่าใช้จ่ายในการดำเนินงานทั้งหมดแล้ว"
      },
      {
        term: "กระแสเงินสด (Cash Flow / เงินสดรับเข้าและจ่ายออกจริง)",
        plain: "เงินสดที่ไหลเข้าและออกจากบัญชีจริงตามเวลาที่เกิดรายการ กิจการอาจมีกำไรทางบัญชีแต่ขาดเงินสดหมุนเวียนได้หากเก็บเงินลูกค้าช้า"
      },
      {
        term: "เงินที่เหลือหลังหักต้นทุนผันแปร (Contribution Margin / กำไรส่วนเกิน)",
        plain: "เงินที่เหลือจากการขายแต่ละหน่วยหลังหักต้นทุนที่เพิ่มตามจำนวนขาย เพื่อนำไปช่วยจ่ายค่าใช้จ่ายคงที่และสร้างกำไร"
      },
      {
        term: "จุดคุ้มทุน (Break-even Point / จุดที่รายได้เท่ากับต้นทุนรวม)",
        plain: "จำนวนสินค้าหรือยอดขายขั้นต่ำที่ทำให้กิจการไม่ขาดทุน (กำไรเท่ากับศูนย์พอดี)"
      },
      {
        term: "เงินทุนหมุนเวียน (Working Capital / สภาพคล่องระยะสั้น)",
        plain: "ทรัพยากรระยะสั้นที่ใช้หมุนเวียนในกิจการประจำวัน เช่น เงินสด ลูกหนี้การค้า และสินค้าคงเหลือ หักด้วยเจ้าหนี้ระยะสั้น"
      },
      {
        term: "ต้นทุนการได้ลูกค้าใหม่ (CAC / Customer Acquisition Cost)",
        plain: "ค่าการตลาดและค่าใช้จ่ายในการขายทั้งหมดที่ใช้ไป เฉลี่ยต่อจำนวนลูกค้าที่ซื้อจริง 1 ราย"
      },
      {
        term: "คอขวดของงาน (Bottleneck / จุดที่ทำงานช้าที่สุดในระบบ)",
        plain: "ขั้นตอนที่มีกำลังการผลิตหรือความเร็วจำกัดที่สุด ซึ่งทำให้งานทั้งระบบส่งมอบได้ช้าลงตามจุดนั้น"
      }
    ],
    getLessonByNumber: function (chNum) {
      var num = parseInt(chNum, 10);
      for (var i = 0; i < lessons.length; i++) {
        if (lessons[i].chapter_number === num) return lessons[i];
      }
      return null;
    },
    getLessonById: function (idOrNum) {
      var num = parseLessonIdentifier(idOrNum);
      if (num === null) return null;
      return this.getLessonByNumber(num);
    },
    toCanonicalLessonId: toCanonicalLessonId,
    parseLessonIdentifier: parseLessonIdentifier
  };

  global.WSTERA_V00_MANIFEST = V00_MANIFEST;
})(window);
