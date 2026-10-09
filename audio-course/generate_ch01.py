import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(r"D:\AI-Workspace\learning\AGY-Business-Self-Study\audio-course")
SCRIPTS_DIR = BASE_DIR / "scripts"
AUDIO_DIR = BASE_DIR / "audio"
TTS_SCRIPT = Path(r"D:\AI-Workspace\projects\tts_automation\gemini_tts.py")

DIRECTOR = "Style: Knowledgeable Business Mentor, calm, warm, authoritative, clear Thai articulation, steady and thoughtful pacing."
VOICE = "Sadaltager"

parts = ["ch01_part1", "ch01_part2", "ch01_part3", "ch01_part4"]
wav_files = []

for p in parts:
    txt_path = SCRIPTS_DIR / f"{p}.txt"
    wav_path = AUDIO_DIR / f"{p}.wav"
    wav_files.append(wav_path)
    
    print(f"\n--- Generating {p} ---")
    cmd = [
        sys.executable,
        str(TTS_SCRIPT),
        "--file", str(txt_path),
        "--output", str(wav_path),
        "--voice", VOICE,
        "--director", DIRECTOR
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to generate {p}")
        sys.exit(1)

# Concat using ffmpeg
print("\n--- Concatenating Audio Parts ---")
concat_list = AUDIO_DIR / "concat_list.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    for w in wav_files:
        # ffmpeg concat demuxer expects forward slashes or escaped backslashes
        escaped_p = str(w).replace("\\", "/")
        f.write(f"file '{escaped_p}'\n")

full_wav = AUDIO_DIR / "ch01_full.wav"
full_mp3 = AUDIO_DIR / "ch01_full.mp3"

concat_cmd = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy",
    str(full_wav)
]
subprocess.run(concat_cmd, check=True)

# Convert to MP3
print("\n--- Converting Full WAV to MP3 ---")
mp3_cmd = [
    "ffmpeg", "-y",
    "-i", str(full_wav),
    "-codec:a", "libmp3lame",
    "-b:a", "192k",
    str(full_mp3)
]
subprocess.run(mp3_cmd, check=True)

print(f"\n[SUCCESS] Generated complete audio:\n{full_wav}\n{full_mp3}")
