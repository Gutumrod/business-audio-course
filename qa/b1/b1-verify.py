import json
import subprocess
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(r"d:\AI-Workspace\learning\AGY-Business-Self-Study")
QA_DIR = REPO_ROOT / "qa" / "b1"
SCREENSHOT_DIR = QA_DIR / "screenshots"
EVIDENCE_PATH = QA_DIR / "B1-QA-EVIDENCE.json"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass


def start_server(port: int):
    handler = partial(QuietHandler, directory=str(REPO_ROOT))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def run_static_checks():
    results = {}
    js_files = ["data/chapters.js", "data/v00-manifest.js", "js/storage-manager.js"]
    syntax_ok = True
    syntax_details = {}
    for rel in js_files:
        proc = subprocess.run(
            ["node", "--check", str(REPO_ROOT / rel)],
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0
        syntax_ok = syntax_ok and ok
        syntax_details[rel] = {"ok": ok, "stderr": proc.stderr.strip()}
    results["js_syntax_check"] = {"passed": syntax_ok, "files": syntax_details}

    diff_proc = subprocess.run(
        ["git", "diff", "main", "--", "audio/", "audio-course/", "data/chapters.js"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    results["untouched_protected_paths"] = {
        "passed": diff_proc.returncode == 0 and len(diff_proc.stdout.strip()) == 0,
        "diff_bytes": len(diff_proc.stdout),
    }

    b1_files = [
        "index.html",
        "js/storage-manager.js",
        "data/v00-manifest.js",
        "ARCHITECTURE-AND-ROADMAP.md",
    ]
    leaked_tokens = []
    for rel in b1_files:
        content = (REPO_ROOT / rel).read_text(encoding="utf-8")
        for forbidden in ["66/100", "verified_external_import", "ANSWER-KEY"]:
            if forbidden in content:
                leaked_tokens.append({"file": rel, "token": forbidden})
    results["no_private_data_or_forbidden_tokens"] = {
        "passed": len(leaked_tokens) == 0,
        "leaked_tokens": leaked_tokens,
    }
    return results


def main():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    port = 8765
    httpd = start_server(port)
    base_url = f"http://127.0.0.1:{port}"

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "base_url": base_url,
        "static_checks": run_static_checks(),
        "routes_and_ux": {},
        "corrupt_storage_matrix": [],
        "lossless_recovery_check": {},
        "quota_blocked_safety_check": {},
        "audio_retention_check": {},
        "separated_progress_check": {},
        "responsive_viewports": [],
        "b0_backward_compat_smoke": {},
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # -----------------------------------------------------------------
            # TEST 1: First-visit UX, Routes, Pre-Test Placeholder, Unknown Hash
            # -----------------------------------------------------------------
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page_errors = []
            page.on("pageerror", lambda e: page_errors.append(str(e)))

            page.goto(f"{base_url}/", wait_until="networkidle")
            root_hub_visible = page.locator("#hubSection").is_visible()
            root_lesson_visible = page.locator("#lessonSection").is_visible()
            first_visit_badge = page.locator("#hubStateBadge").inner_text()
            pretest_cta_text = page.locator("#hubPretestInfoBtn").inner_text()
            start_cta_text = page.locator("#hubStartLessonBtn").inner_text()
            storage_badge_text = page.locator("#syncStatusText").inner_text()

            page.screenshot(path=str(SCREENSHOT_DIR / "b1-desktop-1280-home.png"), full_page=False)

            # Load /?v=2
            page.goto(f"{base_url}/?v=2", wait_until="networkidle")
            v2_ok = page.locator(".ch-chip").count() == 10

            # Test self-declared prior baseline toggle on #home
            page.locator("#hubPriorBaselineToggleBtn").click()
            page.wait_for_timeout(120)
            meta_raw = page.evaluate("localStorage.getItem('wstera_v00_b1_meta')")
            meta_obj = json.loads(meta_raw) if meta_raw else {}
            baseline_after_self_declare = page.locator("#hubStatBaseline").inner_text()

            # Toggle back to default
            page.locator("#hubPriorBaselineToggleBtn").click()
            page.wait_for_timeout(100)

            # Navigate to #pretest/V00 via CTA
            page.locator("#hubPretestInfoBtn").click()
            page.wait_for_timeout(150)
            pretest_hash = page.evaluate("window.location.hash")
            pretest_section_visible = page.locator("#pretestSection").is_visible()
            pretest_heading = page.locator("#pretestSection h1").inner_text()

            # Navigate to #lesson/V00-L10
            page.goto(f"{base_url}/#lesson/V00-L10", wait_until="networkidle")
            l10_title = page.locator("#chapterTitle").inner_text()
            l10_hub_hidden = not page.locator("#hubSection").is_visible()

            # Navigate to #progress
            page.goto(f"{base_url}/#progress", wait_until="networkidle")
            progress_visible = page.locator("#progressSection").is_visible()
            progress_rows = page.locator("#progressTableBody tr").count()

            # Navigate to #help
            page.goto(f"{base_url}/#help", wait_until="networkidle")
            help_visible = page.locator("#helpSection").is_visible()

            # Test browser Back / Forward
            page.go_back()
            page.wait_for_timeout(100)
            back_hash = page.evaluate("window.location.hash")
            page.go_forward()
            page.wait_for_timeout(100)
            forward_hash = page.evaluate("window.location.hash")

            # Test unknown hash & invalid lesson ID fallback
            page.goto(f"{base_url}/#unknown-route-xyz", wait_until="networkidle")
            unknown_fallback_notice = page.locator("#systemNoticeBanner").is_visible()
            unknown_hub_visible = page.locator("#hubSection").is_visible()

            page.goto(f"{base_url}/#lesson/V00-L99", wait_until="networkidle")
            invalid_lesson_notice = page.locator("#systemNoticeBanner").is_visible()

            report["routes_and_ux"] = {
                "passed": (
                    root_hub_visible
                    and root_lesson_visible
                    and v2_ok
                    and "ยังไม่มีผลประเมินก่อนเรียนในเว็บนี้" in first_visit_badge
                    and "สอบตก" not in first_visit_badge
                    and "ทำแบบประเมินก่อนเรียน — เตรียมเปิดใช้งาน" in pretest_cta_text
                    and "ดูบทเรียนตัวอย่าง / เริ่มเรียนบทที่ 1" in start_cta_text
                    and "บันทึกในอุปกรณ์นี้ · ยังไม่ซิงก์ข้ามเครื่อง" in storage_badge_text
                    and pretest_hash == "#pretest/V00"
                    and pretest_section_visible
                    and meta_obj.get("baseline_nav_mode") == "prior_pretest_self_declared"
                    and "แจ้งว่ามีผลจากช่องทางเดิมแล้ว" in baseline_after_self_declare
                    and l10_hub_hidden
                    and progress_visible
                    and progress_rows == 10
                    and help_visible
                    and back_hash == "#progress"
                    and forward_hash == "#help"
                    and unknown_fallback_notice
                    and unknown_hub_visible
                    and invalid_lesson_notice
                    and len(page_errors) == 0
                ),
                "first_visit_badge": first_visit_badge,
                "pretest_cta_text": pretest_cta_text,
                "start_cta_text": start_cta_text,
                "storage_badge_text": storage_badge_text,
                "pretest_heading": pretest_heading,
                "self_declared_meta": meta_obj,
                "baseline_after_self_declare": baseline_after_self_declare,
                "l10_title": l10_title,
                "progress_rows": progress_rows,
                "back_hash": back_hash,
                "forward_hash": forward_hash,
                "unknown_fallback_notice": unknown_fallback_notice,
                "invalid_lesson_notice": invalid_lesson_notice,
                "page_errors": page_errors,
            }
            ctx.close()

            # -----------------------------------------------------------------
            # TEST 2: Corrupt localStorage Matrix & Lossless Recovery
            # -----------------------------------------------------------------
            corrupt_cases = [
                ("invalid_json", "BROKEN_NOT_JSON_{{"),
                ("null_value", "null"),
                ("array_value", '["A","B","C"]'),
                ("primitive_number", "12345"),
                ("primitive_string", '"just_a_string"'),
                ("proto_pollution", '{"__proto__":{"polluted":"A"},"1":"A"}'),
                ("invalid_question_or_option", '{"999":"A","1":"Z"}'),
            ]

            for case_name, raw_payload in corrupt_cases:
                c_ctx = browser.new_context(viewport={"width": 390, "height": 844})
                c_page = c_ctx.new_page()
                c_errors = []
                c_console_warnings = []
                c_page.on("pageerror", lambda e: c_errors.append(str(e)))
                c_page.on(
                    "console",
                    lambda m: c_console_warnings.append(m.text)
                    if m.type == "warning"
                    else None,
                )

                c_page.goto(f"{base_url}/#home", wait_until="networkidle")
                c_page.evaluate(
                    """([payload]) => {
                        localStorage.clear();
                        localStorage.setItem('agy_ch01_quiz_answers', payload);
                        localStorage.setItem('agy_ch01_quiz_submitted', 'true');
                        localStorage.setItem('agy_ch02_completed', 'true');
                        localStorage.setItem('agy_ch02_quiz_answers', JSON.stringify({"1":"B","2":"B","3":"B"}));
                        localStorage.setItem('agy_ch02_quiz_submitted', 'true');
                    }""",
                    [raw_payload],
                )
                c_page.reload(wait_until="networkidle")

                chips = c_page.locator(".ch-chip").count()
                banner_visible = c_page.locator("#systemNoticeBanner").is_visible()
                raw_still_intact = c_page.evaluate(
                    "localStorage.getItem('agy_ch01_quiz_answers')"
                )
                ch02_intact = c_page.evaluate(
                    "localStorage.getItem('agy_ch02_completed') === 'true' && localStorage.getItem('agy_ch02_quiz_submitted') === 'true'"
                )
                leaked_in_console = any(
                    raw_payload in w for w in c_console_warnings if len(raw_payload) > 6
                )

                report["corrupt_storage_matrix"].append(
                    {
                        "case": case_name,
                        "ch_chip_count": chips,
                        "banner_visible": banner_visible,
                        "raw_preserved_on_read": raw_still_intact == raw_payload,
                        "ch02_progress_intact": ch02_intact,
                        "no_raw_console_leak": not leaked_in_console,
                        "page_errors": c_errors,
                        "passed": (
                            chips == 10
                            and banner_visible
                            and raw_still_intact == raw_payload
                            and ch02_intact
                            and not leaked_in_console
                            and len(c_errors) == 0
                        ),
                    }
                )
                c_ctx.close()

            # Test lossless full-string backup on manual recovery (with >300 chars payload to prove no slice(0,200))
            r_ctx = browser.new_context(viewport={"width": 390, "height": 844})
            r_page = r_ctx.new_page()
            r_errors = []
            r_page.on("pageerror", lambda e: r_errors.append(str(e)))
            long_corrupt_payload = "CORRUPT_PAYLOAD_" + ("X" * 350) + "_END_MARKER"

            r_page.goto(f"{base_url}/#home", wait_until="networkidle")
            r_page.evaluate(
                """([payload]) => {
                    localStorage.clear();
                    localStorage.setItem('agy_ch01_quiz_answers', payload);
                    localStorage.setItem('agy_ch02_completed', 'true');
                }""",
                [long_corrupt_payload],
            )
            r_page.reload(wait_until="networkidle")
            r_page.screenshot(
                path=str(SCREENSHOT_DIR / "b1-corrupt-storage-recovery.png"),
                full_page=False,
            )

            r_page.locator("#systemRecoverBtn").click()
            r_page.wait_for_timeout(150)

            backup_val = r_page.evaluate(
                "localStorage.getItem('agy_ch01_quiz_answers_corrupt_backup')"
            )
            ch01_after = r_page.evaluate("localStorage.getItem('agy_ch01_quiz_answers')")
            ch02_after = r_page.evaluate("localStorage.getItem('agy_ch02_completed')")
            banner_after = r_page.locator("#systemNoticeBanner").is_visible()

            report["lossless_recovery_check"] = {
                "passed": (
                    backup_val == long_corrupt_payload
                    and len(backup_val) == len(long_corrupt_payload)
                    and ch01_after is None
                    and ch02_after == "true"
                    and not banner_after
                    and len(r_errors) == 0
                ),
                "original_length": len(long_corrupt_payload),
                "backup_length": len(backup_val) if backup_val else 0,
                "exact_match": backup_val == long_corrupt_payload,
                "ch01_cleared_after_verified_backup": ch01_after is None,
                "ch02_untouched": ch02_after == "true",
                "page_errors": r_errors,
            }
            r_ctx.close()

            # -----------------------------------------------------------------
            # TEST 3: Simulated localStorage Quota/Access Denial Safety Check
            # -----------------------------------------------------------------
            q_ctx = browser.new_context(viewport={"width": 390, "height": 844})
            q_page = q_ctx.new_page()
            q_errors = []
            q_page.on("pageerror", lambda e: q_errors.append(str(e)))
            q_page.goto(f"{base_url}/#lesson/V00-L01", wait_until="networkidle")

            quota_res = q_page.evaluate(
                """() => {
                    localStorage.setItem('agy_ch01_quiz_answers', 'CORRUPT_UNDER_QUOTA_BLOCK');
                    const origSetItem = Storage.prototype.setItem;
                    Storage.prototype.setItem = function() {
                        throw new DOMException('QuotaExceededError', 'QuotaExceededError');
                    };
                    try {
                        const rec = window.LearningStore.backupAndRecoverCorruptedChapter(1);
                        const writeRes = window.LearningStore.writeChapterQuizAnswers(1, {"1":"B"}, ["1","2","3"]);
                        const rawStillThere = localStorage.getItem('agy_ch01_quiz_answers');
                        return {
                            recoveryAttempt: rec,
                            writeAttempt: writeRes,
                            rawPreservedWhenBackupBlocked: rawStillThere === 'CORRUPT_UNDER_QUOTA_BLOCK'
                        };
                    } finally {
                        Storage.prototype.setItem = origSetItem;
                    }
                }"""
            )
            report["quota_blocked_safety_check"] = {
                "passed": (
                    quota_res["recoveryAttempt"]["recovered"] is False
                    and quota_res["rawPreservedWhenBackupBlocked"] is True
                    and quota_res["writeAttempt"]["usedMemoryFallback"] is True
                    and len(q_errors) == 0
                ),
                "details": quota_res,
                "page_errors": q_errors,
            }
            q_ctx.close()

            # -----------------------------------------------------------------
            # TEST 4: Audio Player Retention & Controls Across Route Changes
            # -----------------------------------------------------------------
            a_ctx = browser.new_context(viewport={"width": 390, "height": 844})
            a_page = a_ctx.new_page()
            a_errors = []
            a_page.on("pageerror", lambda e: a_errors.append(str(e)))
            a_page.goto(f"{base_url}/#lesson/V00-L01", wait_until="networkidle")

            a_page.evaluate(
                """() => {
                    const audio = document.getElementById('audioElement');
                    audio.dataset.instanceTag = 'same-audio-element-1';
                }"""
            )
            a_page.locator("#speedBtn").click()
            speed_after_click = a_page.locator("#speedBtn").inner_text()
            src_before = a_page.evaluate("document.getElementById('audioElement').getAttribute('src')")

            a_page.goto(f"{base_url}/#progress", wait_until="networkidle")
            a_page.goto(f"{base_url}/#home", wait_until="networkidle")
            a_page.goto(f"{base_url}/#lesson/V00-L01", wait_until="networkidle")

            same_instance = a_page.evaluate(
                "document.getElementById('audioElement').dataset.instanceTag === 'same-audio-element-1'"
            )
            src_after = a_page.evaluate("document.getElementById('audioElement').getAttribute('src')")

            report["audio_retention_check"] = {
                "passed": (
                    same_instance
                    and src_before == "audio/ch01_full.mp3"
                    and src_after == "audio/ch01_full.mp3"
                    and speed_after_click == "1.25x"
                    and len(a_errors) == 0
                ),
                "same_dom_instance": same_instance,
                "src_before": src_before,
                "src_after": src_after,
                "speed_after_click": speed_after_click,
                "page_errors": a_errors,
            }
            a_ctx.close()

            # -----------------------------------------------------------------
            # TEST 5: Separated Progress & Anti-Premature Pass Gate
            # -----------------------------------------------------------------
            p_ctx = browser.new_context(viewport={"width": 390, "height": 844})
            p_page = p_ctx.new_page()
            p_errors = []
            p_page.on("pageerror", lambda e: p_errors.append(str(e)))
            p_page.goto(f"{base_url}/#home", wait_until="networkidle")

            # Case A: 1 chapter submitted with 0/3 score -> practice_submitted_count must be 1/10 (not 0/10)
            p_page.evaluate(
                """() => {
                    localStorage.clear();
                    localStorage.setItem('agy_ch01_quiz_answers', JSON.stringify({"1":"A","2":"A","3":"A"}));
                    localStorage.setItem('agy_ch01_quiz_submitted', 'true');
                }"""
            )
            p_page.reload(wait_until="networkidle")
            zero_score_submitted_text = p_page.locator("#statSubmittedQuizzes").inner_text()
            zero_score_total_text = p_page.locator("#statTotalScore").inner_text()

            # Case B: 10/10 audio completed + 10/10 quiz submitted with 30/30 perfect score
            p_page.evaluate(
                """() => {
                    localStorage.clear();
                    const chapters = window.COURSE_CHAPTERS;
                    chapters.forEach(ch => {
                        const pad = ch.id < 10 ? '0' + ch.id : '' + ch.id;
                        localStorage.setItem('agy_ch' + pad + '_completed', 'true');
                        const ans = {};
                        ch.quiz.forEach(qObj => { ans[String(qObj.q)] = qObj.correct; });
                        localStorage.setItem('agy_ch' + pad + '_quiz_answers', JSON.stringify(ans));
                        localStorage.setItem('agy_ch' + pad + '_quiz_submitted', 'true');
                    });
                }"""
            )
            p_page.reload(wait_until="networkidle")
            perfect_audio = p_page.locator("#statCompletedChapters").inner_text()
            perfect_submitted = p_page.locator("#statSubmittedQuizzes").inner_text()
            perfect_score = p_page.locator("#statTotalScore").inner_text()
            perfect_gate = p_page.locator("#statPassStatus").inner_text()
            body_text = p_page.locator("body").inner_text()

            report["separated_progress_check"] = {
                "passed": (
                    zero_score_submitted_text == "1 / 10"
                    and zero_score_total_text == "0 / 30"
                    and perfect_audio == "10 / 10"
                    and perfect_submitted == "10 / 10"
                    and perfect_score == "30 / 30"
                    and perfect_gate == "ยังไม่ได้ประเมิน"
                    and "✓ ผ่านเกณฑ์" not in body_text
                    and len(p_errors) == 0
                ),
                "zero_score_submitted_count": zero_score_submitted_text,
                "zero_score_total": zero_score_total_text,
                "perfect_audio": perfect_audio,
                "perfect_submitted": perfect_submitted,
                "perfect_score": perfect_score,
                "perfect_gate_status": perfect_gate,
                "page_errors": p_errors,
            }
            p_ctx.close()

            # -----------------------------------------------------------------
            # TEST 6: Responsive Viewports (375, 390, 430, 768, 1280px)
            # -----------------------------------------------------------------
            viewports = [
                (375, 812),
                (390, 844),
                (430, 932),
                (768, 1024),
                (1280, 900),
            ]
            routes_to_check = ["#home", "#lesson/V00-L01", "#progress", "#pretest/V00", "#help"]

            for vw, vh in viewports:
                v_ctx = browser.new_context(viewport={"width": vw, "height": vh})
                v_page = v_ctx.new_page()
                v_errors = []
                v_page.on("pageerror", lambda e: v_errors.append(str(e)))

                route_metrics = {}
                all_no_overflow = True
                for r in routes_to_check:
                    v_page.goto(f"{base_url}/{r}", wait_until="networkidle")
                    v_page.wait_for_timeout(80)
                    dims = v_page.evaluate(
                        """() => ({
                            innerWidth: window.innerWidth,
                            scrollWidth: document.documentElement.scrollWidth
                        })"""
                    )
                    no_overflow = dims["scrollWidth"] <= dims["innerWidth"]
                    all_no_overflow = all_no_overflow and no_overflow
                    route_metrics[r] = {
                        "innerWidth": dims["innerWidth"],
                        "scrollWidth": dims["scrollWidth"],
                        "no_horizontal_overflow": no_overflow,
                    }

                    if vw == 390 and r in ("#home", "#lesson/V00-L01", "#progress"):
                        slug = r.replace("#", "").replace("/", "-")
                        v_page.screenshot(
                            path=str(SCREENSHOT_DIR / f"b1-mobile-390-{slug}.png"),
                            full_page=False,
                        )

                report["responsive_viewports"].append(
                    {
                        "viewport": f"{vw}x{vh}",
                        "passed": all_no_overflow and len(v_errors) == 0,
                        "routes": route_metrics,
                        "page_errors": v_errors,
                    }
                )
                v_ctx.close()

            # -----------------------------------------------------------------
            # TEST 7: B0 Backward-Compatibility Smoke (Root load + .option-btn click)
            # -----------------------------------------------------------------
            s_ctx = browser.new_context(viewport={"width": 390, "height": 844})
            s_page = s_ctx.new_page()
            s_errors = []
            s_page.on("pageerror", lambda e: s_errors.append(str(e)))
            s_page.goto(f"{base_url}/", wait_until="networkidle")
            s_page.locator(".option-btn").first.click()
            saved_ans = s_page.evaluate("localStorage.getItem('agy_ch01_quiz_answers')")
            report["b0_backward_compat_smoke"] = {
                "passed": saved_ans == '{"1":"A"}' and len(s_errors) == 0,
                "saved_ans": saved_ans,
                "page_errors": s_errors,
            }
            s_ctx.close()

            browser.close()
    finally:
        httpd.shutdown()

    EVIDENCE_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Verification completed. Summary:")
    print("Static checks:", {k: v["passed"] for k, v in report["static_checks"].items()})
    print("Routes & UX:", report["routes_and_ux"]["passed"])
    print(
        "Corrupt storage matrix:",
        all(item["passed"] for item in report["corrupt_storage_matrix"]),
    )
    print("Lossless recovery:", report["lossless_recovery_check"]["passed"])
    print("Quota blocked safety:", report["quota_blocked_safety_check"]["passed"])
    print("Audio retention:", report["audio_retention_check"]["passed"])
    print("Separated progress:", report["separated_progress_check"]["passed"])
    print(
        "Responsive viewports:",
        all(item["passed"] for item in report["responsive_viewports"]),
    )
    print("B0 backward compat smoke:", report["b0_backward_compat_smoke"]["passed"])


if __name__ == "__main__":
    main()
