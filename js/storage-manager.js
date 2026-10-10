// ============================================================================
// WSTERA Academy — B1 Safe Storage Manager & Non-Destructive Legacy Adapter
// Implements C1, C2, C4, C7 from 05-B0-AGY-INDEPENDENT-REVIEW.md
// ============================================================================
(function (global) {
  "use strict";

  var VALID_OPTIONS = { A: true, B: true, C: true, D: true };
  var FORBIDDEN_KEYS = { __proto__: true, constructor: true, prototype: true };
  var B1_META_KEY = "wstera_v00_b1_meta";
  var MAX_RAW_BACKUP_BYTES = 65536; // 64 KiB guard against unbounded storage abuse

  // In-memory fallback when localStorage is blocked/unavailable or key is quarantined
  var memoryFallbackStore = Object.create(null);
  var warnedCorruptKeys = Object.create(null);
  var corruptedChapterRegistry = Object.create(null);
  var storageOperational = true;

  function pad2(n) {
    var num = parseInt(n, 10);
    return (num < 10 ? "0" : "") + String(num);
  }

  function keyAudioTime(chId) {
    return "agy_ch" + pad2(chId) + "_audio_time";
  }
  function keyCompleted(chId) {
    return "agy_ch" + pad2(chId) + "_completed";
  }
  function keyQuizAnswers(chId) {
    return "agy_ch" + pad2(chId) + "_quiz_answers";
  }
  function keyQuizSubmitted(chId) {
    return "agy_ch" + pad2(chId) + "_quiz_submitted";
  }
  function keyQuizCorruptBackup(chId) {
    return "agy_ch" + pad2(chId) + "_quiz_answers_corrupt_backup";
  }

  function safeGetItem(key) {
    try {
      var val = global.localStorage.getItem(key);
      if (val !== null) return val;
    } catch (e) {
      storageOperational = false;
    }
    return Object.prototype.hasOwnProperty.call(memoryFallbackStore, key)
      ? memoryFallbackStore[key]
      : null;
  }

  function safeSetItem(key, value) {
    var strVal = String(value);
    try {
      global.localStorage.setItem(key, strVal);
      return true;
    } catch (e) {
      storageOperational = false;
      memoryFallbackStore[key] = strVal;
      return false;
    }
  }

  function safeRemoveItem(key) {
    delete memoryFallbackStore[key];
    try {
      global.localStorage.removeItem(key);
      return true;
    } catch (e) {
      storageOperational = false;
      return false;
    }
  }

  function warnOnce(key, reason) {
    if (warnedCorruptKeys[key]) return;
    warnedCorruptKeys[key] = true;
    // Never log raw learner answers or sensitive content
    if (global.console && typeof global.console.warn === "function") {
      global.console.warn(
        "[StorageGuard] Non-conforming data detected in key '" +
          key +
          "' (" +
          reason +
          "). Preserving original raw value and using safe in-memory fallback."
      );
    }
  }

  function isPlainObject(obj) {
    if (!obj || typeof obj !== "object" || Array.isArray(obj)) return false;
    var proto = Object.getPrototypeOf(obj);
    return proto === null || proto === Object.prototype;
  }

  /**
   * Reads and strictly validates quiz answers for a chapter.
   * Does NOT destructively delete or truncate corrupted keys on read.
   */
  function readChapterQuizState(chId, allowedQuestionIds) {
    var key = keyQuizAnswers(chId);
    var raw = null;
    try {
      raw = global.localStorage.getItem(key);
    } catch (e) {
      storageOperational = false;
      raw = Object.prototype.hasOwnProperty.call(memoryFallbackStore, key)
        ? memoryFallbackStore[key]
        : null;
    }

    if (raw === null || raw === "") {
      delete corruptedChapterRegistry[chId];
      // Check if there is a clean in-memory draft when raw storage was quarantined
      if (Object.prototype.hasOwnProperty.call(memoryFallbackStore, key)) {
        try {
          var memParsed = JSON.parse(memoryFallbackStore[key]);
          if (isPlainObject(memParsed)) {
            return { answers: memParsed, corrupted: false, rawPreserved: false };
          }
        } catch (_) {}
      }
      return { answers: Object.create(null), corrupted: false, rawPreserved: false };
    }

    // Check raw string length bound
    if (typeof raw !== "string" || raw.length > MAX_RAW_BACKUP_BYTES) {
      warnOnce(key, "payload_exceeds_bounds");
      corruptedChapterRegistry[chId] = { key: key, reason: "payload_exceeds_bounds" };
      return { answers: Object.create(null), corrupted: true, rawPreserved: true };
    }

    // Inspect raw string for explicit "__proto__" token before JSON.parse
    // (since JSON.parse in JS silently drops or processes __proto__ differently)
    if (raw.indexOf('"__proto__"') !== -1 || raw.indexOf('"constructor"') !== -1 || raw.indexOf('"prototype"') !== -1) {
      warnOnce(key, "forbidden_prototype_key");
      corruptedChapterRegistry[chId] = { key: key, reason: "forbidden_prototype_key" };
      return { answers: Object.create(null), corrupted: true, rawPreserved: true };
    }

    var parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (err) {
      warnOnce(key, "malformed_json");
      corruptedChapterRegistry[chId] = { key: key, reason: "malformed_json" };
      return { answers: Object.create(null), corrupted: true, rawPreserved: true };
    }

    if (!isPlainObject(parsed)) {
      warnOnce(key, "non_object_json");
      corruptedChapterRegistry[chId] = { key: key, reason: "non_object_json" };
      return { answers: Object.create(null), corrupted: true, rawPreserved: true };
    }

    var allowedMap = null;
    if (Array.isArray(allowedQuestionIds) && allowedQuestionIds.length > 0) {
      allowedMap = Object.create(null);
      for (var i = 0; i < allowedQuestionIds.length; i++) {
        allowedMap[String(allowedQuestionIds[i])] = true;
      }
    }

    var clean = Object.create(null);
    var ownKeys = Object.keys(parsed);
    for (var kIdx = 0; kIdx < ownKeys.length; kIdx++) {
      var qKey = ownKeys[kIdx];
      if (FORBIDDEN_KEYS[qKey]) {
        warnOnce(key, "forbidden_key");
        corruptedChapterRegistry[chId] = { key: key, reason: "forbidden_key" };
        return { answers: Object.create(null), corrupted: true, rawPreserved: true };
      }
      if (allowedMap && !allowedMap[qKey]) {
        warnOnce(key, "unexpected_question_id");
        corruptedChapterRegistry[chId] = { key: key, reason: "unexpected_question_id" };
        return { answers: Object.create(null), corrupted: true, rawPreserved: true };
      }
      if (!allowedMap && !/^\d{1,3}$/.test(qKey)) {
        warnOnce(key, "non_numeric_question_id");
        corruptedChapterRegistry[chId] = { key: key, reason: "non_numeric_question_id" };
        return { answers: Object.create(null), corrupted: true, rawPreserved: true };
      }
      var optVal = parsed[qKey];
      if (typeof optVal !== "string" || !VALID_OPTIONS[optVal]) {
        warnOnce(key, "invalid_option_value");
        corruptedChapterRegistry[chId] = { key: key, reason: "invalid_option_value" };
        return { answers: Object.create(null), corrupted: true, rawPreserved: true };
      }
      clean[qKey] = optVal;
    }

    delete corruptedChapterRegistry[chId];
    return { answers: clean, corrupted: false, rawPreserved: false };
  }

  /**
   * Losslessly backs up full original corrupted raw string before resetting/writing.
   * Never truncates with slice(). If backup fails (e.g., quota error), preserves
   * original localStorage key untouched and operates in memoryFallbackStore only.
   */
  function backupAndRecoverCorruptedChapter(chId) {
    var key = keyQuizAnswers(chId);
    var backupKey = keyQuizCorruptBackup(chId);
    var raw = null;
    try {
      raw = global.localStorage.getItem(key);
    } catch (e) {
      storageOperational = false;
    }

    if (raw !== null) {
      try {
        global.localStorage.setItem(backupKey, raw);
        var verifyRead = global.localStorage.getItem(backupKey);
        if (verifyRead !== raw) {
          return { recovered: false, backupVerified: false, reason: "backup_verification_mismatch" };
        }
        // Full backup verified — safe to clear only the affected chapter quiz key and submitted flag
        global.localStorage.removeItem(key);
        global.localStorage.removeItem(keyQuizSubmitted(chId));
      } catch (e) {
        storageOperational = false;
        // Quota or security failure: DO NOT delete original key!
        return { recovered: false, backupVerified: false, reason: "storage_write_blocked" };
      }
    }

    delete memoryFallbackStore[key];
    delete memoryFallbackStore[keyQuizSubmitted(chId)];
    delete corruptedChapterRegistry[chId];
    return { recovered: true, backupVerified: true, backupKey: backupKey };
  }

  /**
   * Writes validated quiz answers for a chapter.
   * If the chapter currently has a corrupted raw value in localStorage, performs
   * a lossless verified backup first before overwriting; if backup fails, keeps
   * the original localStorage key untouched and writes to memoryFallbackStore.
   */
  function writeChapterQuizAnswers(chId, answersObj, allowedQuestionIds) {
    var key = keyQuizAnswers(chId);
    var state = readChapterQuizState(chId, allowedQuestionIds);
    if (state.corrupted) {
      var recovery = backupAndRecoverCorruptedChapter(chId);
      if (!recovery.recovered) {
        // Preserve raw localStorage untouched, write clean draft to memory only
        memoryFallbackStore[key] = JSON.stringify(answersObj);
        return { persistedToLocalStorage: false, usedMemoryFallback: true };
      }
    }

    var clean = Object.create(null);
    var keys = Object.keys(answersObj || {});
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (!FORBIDDEN_KEYS[k] && VALID_OPTIONS[answersObj[k]]) {
        clean[String(k)] = answersObj[k];
      }
    }
    var serialized = JSON.stringify(clean);
    var ok = safeSetItem(key, serialized);
    return { persistedToLocalStorage: ok, usedMemoryFallback: !ok };
  }

  function isChapterQuizSubmitted(chId, allowedQuestionIds) {
    var state = readChapterQuizState(chId, allowedQuestionIds);
    if (state.corrupted) {
      // Do not treat corrupted answer payload as a valid submitted quiz
      return false;
    }
    var subRaw = safeGetItem(keyQuizSubmitted(chId));
    return subRaw === "true";
  }

  function setChapterQuizSubmitted(chId, isSubmitted) {
    if (isSubmitted) {
      return safeSetItem(keyQuizSubmitted(chId), "true");
    } else {
      return safeRemoveItem(keyQuizSubmitted(chId));
    }
  }

  function resetChapterQuiz(chId, allowedQuestionIds) {
    var state = readChapterQuizState(chId, allowedQuestionIds);
    if (state.corrupted) {
      return backupAndRecoverCorruptedChapter(chId);
    }
    safeRemoveItem(keyQuizAnswers(chId));
    safeRemoveItem(keyQuizSubmitted(chId));
    return { recovered: true, backupVerified: true };
  }

  function getCurrentChapterNumber(totalLessons) {
    var maxCh = totalLessons || 10;
    var raw = safeGetItem("agy_v00_current_chapter");
    var parsed = parseInt(raw || "1", 10);
    if (isNaN(parsed) || parsed < 1 || parsed > maxCh) {
      return 1;
    }
    return parsed;
  }

  function hasExistingLearnerActivity(manifest) {
    if (safeGetItem("agy_v00_current_chapter") !== null) return true;
    var lessons = (manifest && manifest.lessons) || [];
    for (var i = 0; i < lessons.length; i++) {
      var chId = lessons[i].chapter_number;
      if (
        safeGetItem(keyCompleted(chId)) === "true" ||
        safeGetItem(keyAudioTime(chId)) !== null ||
        safeGetItem(keyQuizAnswers(chId)) !== null
      ) {
        return true;
      }
    }
    return false;
  }

  function setCurrentChapterNumber(chId) {
    return safeSetItem("agy_v00_current_chapter", String(chId));
  }

  function getAudioSavedTime(chId, maxDurationSec) {
    var raw = safeGetItem(keyAudioTime(chId));
    var val = parseFloat(raw || "0");
    if (isNaN(val) || !isFinite(val) || val < 0) return 0;
    if (maxDurationSec && val >= maxDurationSec - 5) return 0;
    return val;
  }

  function setAudioSavedTime(chId, seconds) {
    var num = parseFloat(seconds);
    if (isNaN(num) || !isFinite(num) || num < 0) num = 0;
    return safeSetItem(keyAudioTime(chId), String(num));
  }

  function isAudioCompleted(chId) {
    return safeGetItem(keyCompleted(chId)) === "true";
  }

  function setAudioCompleted(chId, completed) {
    if (completed) {
      return safeSetItem(keyCompleted(chId), "true");
    } else {
      return safeRemoveItem(keyCompleted(chId));
    }
  }

  /**
   * Reads B1 Hub metadata (strictly schema_version: 1, no fake verified baseline)
   */
  function readHubMeta() {
    var raw = safeGetItem(B1_META_KEY);
    var defaultMeta = {
      schema_version: 1,
      baseline_nav_mode: "none" // "none" | "prior_pretest_self_declared"
    };
    if (!raw) return defaultMeta;
    try {
      var parsed = JSON.parse(raw);
      if (!isPlainObject(parsed)) return defaultMeta;
      var mode =
        parsed.baseline_nav_mode === "prior_pretest_self_declared"
          ? "prior_pretest_self_declared"
          : "none";
      return {
        schema_version: 1,
        baseline_nav_mode: mode
      };
    } catch (e) {
      return defaultMeta;
    }
  }

  function setBaselineNavMode(mode) {
    var validMode =
      mode === "prior_pretest_self_declared" ? "prior_pretest_self_declared" : "none";
    var payload = {
      schema_version: 1,
      baseline_nav_mode: validMode,
      updated_at: new Date().toISOString()
    };
    return safeSetItem(B1_META_KEY, JSON.stringify(payload));
  }

  /**
   * Computes grounded progress metrics across all lessons in the manifest.
   * Enforces C4: separate audio_completed_count, practice_submitted_count,
   * practice_score, and academy_gate_status = "not_assessed".
   */
  function getChapterQuizSummary(chObj) {
    var qList = Array.isArray(chObj.quiz) ? chObj.quiz : [];
    var allowedIds = qList.map(function (q) { return String(q.q); });
    var state = readChapterQuizState(chObj.id, allowedIds);
    var isSubmitted = isChapterQuizSubmitted(chObj.id, allowedIds);

    var rawScore = 0;
    var answered = 0;
    for (var i = 0; i < qList.length; i++) {
      var q = qList[i];
      var chosen = state.answers[String(q.q)];
      if (chosen && VALID_OPTIONS[chosen]) {
        answered++;
        if (chosen === q.correct) {
          rawScore++;
        }
      }
    }

    var allAnswered = qList.length > 0 && answered === qList.length;
    var validSubmitted = isSubmitted && allAnswered && !state.corrupted;

    return {
      score: validSubmitted ? rawScore : 0,
      rawScore: rawScore,
      answered: answered,
      totalQuestions: qList.length,
      isSubmitted: validSubmitted,
      corrupted: state.corrupted,
      rawPreserved: state.rawPreserved,
      answers: state.answers
    };
  }

  function getCourseProgressSummary(manifest) {
    var lessons = (manifest && manifest.lessons) || [];
    var totalLessons = lessons.length;
    var audioCompletedCount = 0;
    var practiceSubmittedCount = 0;
    var practiceScore = 0;
    var practiceMaxScore = 0;
    var corruptedChapters = [];
    var lessonSummaries = [];

    for (var i = 0; i < totalLessons; i++) {
      var item = lessons[i];
      var ch = item.chapter_ref;
      var audioDone = isAudioCompleted(item.chapter_number);
      var audioTime = getAudioSavedTime(item.chapter_number, item.duration_seconds_estimate);
      var qSum = getChapterQuizSummary(ch);

      if (audioDone) audioCompletedCount++;
      if (qSum.isSubmitted) {
        practiceSubmittedCount++;
        practiceScore += qSum.score;
      }
      practiceMaxScore += qSum.totalQuestions;

      if (qSum.corrupted) {
        corruptedChapters.push(item.chapter_number);
      }

      lessonSummaries.push({
        lesson_id: item.lesson_id,
        chapter_number: item.chapter_number,
        code: item.code,
        title: item.title,
        short_title: item.short_title,
        duration_formatted: ch.duration || item.duration_formatted,
        audio_completed: audioDone,
        audio_saved_time: audioTime,
        quiz_submitted: qSum.isSubmitted,
        quiz_answered: qSum.answered,
        quiz_total: qSum.totalQuestions,
        quiz_score: qSum.score,
        quiz_corrupted: qSum.corrupted
      });
    }

    var hubMeta = readHubMeta();

    return {
      total_lessons: totalLessons,
      audio_completed_count: audioCompletedCount,
      practice_submitted_count: practiceSubmittedCount,
      practice_score: practiceScore,
      practice_max_score: practiceMaxScore,
      academy_gate_status: "not_assessed",
      academy_gate_label: "ยังไม่ได้ประเมิน (รอผลสอบหลังเรียนและผู้ตรวจ)",
      baseline_nav_mode: hubMeta.baseline_nav_mode,
      has_corrupted_storage: corruptedChapters.length > 0,
      corrupted_chapters: corruptedChapters,
      storage_operational: storageOperational,
      lessons: lessonSummaries
    };
  }

  global.LearningStore = {
    schema_version: 1,
    keyAudioTime: keyAudioTime,
    keyCompleted: keyCompleted,
    keyQuizAnswers: keyQuizAnswers,
    keyQuizSubmitted: keyQuizSubmitted,
    keyQuizCorruptBackup: keyQuizCorruptBackup,
    readChapterQuizState: readChapterQuizState,
    writeChapterQuizAnswers: writeChapterQuizAnswers,
    isChapterQuizSubmitted: isChapterQuizSubmitted,
    setChapterQuizSubmitted: setChapterQuizSubmitted,
    resetChapterQuiz: resetChapterQuiz,
    backupAndRecoverCorruptedChapter: backupAndRecoverCorruptedChapter,
    getChapterQuizSummary: getChapterQuizSummary,
    getCourseProgressSummary: getCourseProgressSummary,
    getCurrentChapterNumber: getCurrentChapterNumber,
    setCurrentChapterNumber: setCurrentChapterNumber,
    hasExistingLearnerActivity: hasExistingLearnerActivity,
    getAudioSavedTime: getAudioSavedTime,
    setAudioSavedTime: setAudioSavedTime,
    isAudioCompleted: isAudioCompleted,
    setAudioCompleted: setAudioCompleted,
    readHubMeta: readHubMeta,
    setBaselineNavMode: setBaselineNavMode,
    isStorageOperational: function () { return storageOperational; }
  };
})(window);
