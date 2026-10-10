import json
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT_DIR = Path(r"D:\AI-Workspace\learning\AGY-Business-Self-Study")
ROOT_AUDIO_DIR = ROOT_DIR / "audio"
COURSE_DIR = ROOT_DIR / "audio-course"
SCRIPTS_DIR = COURSE_DIR / "scripts"
COURSE_AUDIO_DIR = COURSE_DIR / "audio"
TTS_SCRIPT = Path(r"D:\AI-Workspace\projects\tts_automation\gemini_tts.py")

ROOT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
COURSE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

DIRECTOR = "Style: Knowledgeable Business Mentor, calm, warm, authoritative, clear Thai articulation, steady and thoughtful pacing."
VOICE = "Sadaltager"

CHAPTERS = [f"ch{i:02d}" for i in range(2, 11)]


def get_wav_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)


def format_mmss(seconds: float) -> str:
    total = int(round(seconds))
    m = total // 60
    s = total % 60
    return f"{m}:{s:02d}"


for ch in CHAPTERS:
    final_root_mp3 = ROOT_AUDIO_DIR / f"{ch}_full.mp3"
    final_course_wav = COURSE_AUDIO_DIR / f"{ch}_full.wav"
    if final_root_mp3.exists() and final_root_mp3.stat().st_size > 500_000 and final_course_wav.exists():
        print(f"[SKIP CHAPTER] {ch} already generated ({final_root_mp3.stat().st_size} bytes)")
        continue

    parts = [f"{ch}_part1", f"{ch}_part2", f"{ch}_part3"]
    wav_files = []

    for p in parts:
        txt_path = SCRIPTS_DIR / f"{p}.txt"
        wav_path = COURSE_AUDIO_DIR / f"{p}.wav"
        wav_files.append(wav_path)

        if wav_path.exists() and wav_path.stat().st_size > 100_000:
            dur = get_wav_duration(wav_path)
            print(f"[SKIP PART] {p}.wav already exists ({dur:.1f}s)")
            continue

        print(f"\n=== Generating {p} ===")
        success = False
        for attempt in range(1, 4):
            cmd = [
                sys.executable,
                str(TTS_SCRIPT),
                "--file", str(txt_path),
                "--output", str(wav_path),
                "--voice", VOICE,
                "--director", DIRECTOR,
            ]
            res = subprocess.run(cmd)
            if res.returncode == 0 and wav_path.exists() and wav_path.stat().st_size > 50_000:
                dur = get_wav_duration(wav_path)
                print(f"[OK] {p}.wav generated ({dur:.1f}s)")
                success = True
                time.sleep(2)
                break
            else:
                print(f"[WARN] Attempt {attempt} failed for {p}, retrying in 6s...")
                time.sleep(6)

        if not success:
            print(f"[ERROR] Failed to generate {p} after 3 attempts.")
            sys.exit(1)

    # Concatenate parts into chXX_full.wav
    concat_list = COURSE_AUDIO_DIR / f"concat_{ch}.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for w in wav_files:
            escaped_p = str(w).replace("\\", "/")
            f.write(f"file '{escaped_p}'\n")

    full_wav = COURSE_AUDIO_DIR / f"{ch}_full.wav"
    full_mp3 = COURSE_AUDIO_DIR / f"{ch}_full.mp3"

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(full_wav)
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(full_wav),
        "-codec:a", "libmp3lame", "-b:a", "192k", str(full_mp3)
    ], check=True)

    shutil.copy2(full_mp3, final_root_mp3)
    dur_sec = get_wav_duration(full_wav)
    print(f"[CHAPTER DONE] {ch}_full.mp3 -> {format_mmss(dur_sec)} ({dur_sec:.1f}s)")

# Record all durations ch01..ch10
durations = {}
ch01_wav = ROOT_AUDIO_DIR / "ch01_full.wav"
if ch01_wav.exists():
    d1 = get_wav_duration(ch01_wav)
    durations["1"] = {"seconds": round(d1, 1), "formatted": format_mmss(d1)}
else:
    durations["1"] = {"seconds": 211.0, "formatted": "3:31"}

for i in range(2, 11):
    ch = f"ch{i:02d}"
    w_path = COURSE_AUDIO_DIR / f"{ch}_full.wav"
    if w_path.exists():
        d = get_wav_duration(w_path)
        durations[str(i)] = {"seconds": round(d, 1), "formatted": format_mmss(d)}

dur_json = ROOT_AUDIO_DIR / "durations.json"
dur_json.write_text(json.dumps(durations, indent=2, ensure_ascii=False), encoding="utf-8")
print("\n=== ALL CHAPTERS COMPLETED ===")
print(json.dumps(durations, indent=2, ensure_ascii=False))
