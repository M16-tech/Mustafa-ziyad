# prep.py — everything you need to know about a raw reel before designing the edit.
# usage: python prep.py <video> <work_dir> [script.txt] [--model small] [--lang ar]   (--lang auto-detects if omitted)
# Also converts any input (horizontal, 4K, 25/50/60 fps…) to a 1080x1920 / 30 fps working copy: <work_dir>/src.mov
# outputs in work_dir: transcript.json (segments + word timings), words.txt (one line per segment, word@time),
#                      cuts.txt (real jump-cut times), contact.png (frame every ~6 s), info.txt
import sys, os, re, json, subprocess
from PIL import Image

def sh(cmd): return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small"
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else None
    for v in (model if "--model" in sys.argv else None, lang):
        if v in args: args.remove(v)
    src, wd = args[0], args[1]; script = open(args[2], encoding="utf-8").read() if len(args) > 2 else ""
    os.makedirs(wd, exist_ok=True)
    # working copy: vertical 1080x1920, 30 fps (crops the centre of a horizontal video — tell the user if that happens)
    work = os.path.join(wd, "src.mov")
    if not os.path.exists(work):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30,setsar=1",
                        "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", work], check=True)
    src = work

    info = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,channels", "-of", "compact", src]).stdout
    dur = float(re.search(r"duration=([\d.]+)", info).group(1))
    open(os.path.join(wd, "info.txt"), "w", encoding="utf-8").write(info); print(info)

    # real jump cuts (showinfo prints on stderr, so do NOT pass -v error here)
    err = sh(["ffmpeg", "-i", src, "-vf", "select='gt(scene,0.06)',showinfo", "-f", "null", "-"]).stderr
    cuts = [round(float(x), 3) for x in re.findall(r"pts_time:([\d.]+)", err)]
    open(os.path.join(wd, "cuts.txt"), "w").write("\n".join(map(str, cuts))); print("cuts:", cuts)

    # contact sheet
    n = 10; tiles = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == 270 * 480 * 3: tiles.append(Image.frombuffer("RGB", (270, 480), raw))
    sheet = Image.new("RGB", (270 * 5, 480 * 2))
    for i, im in enumerate(tiles): sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
    sheet.save(os.path.join(wd, "contact.png"))

    # transcription with word timings — GPU if it works, otherwise CPU
    wav = os.path.join(wd, "audio16.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav])
    from faster_whisper import WhisperModel
    def run(device, ctype):
        m = WhisperModel(model, device=device, compute_type=ctype)
        # no initial_prompt (the script made Whisper hallucinate in tests); VAD + no conditioning is reliable
        segs, info = m.transcribe(wav, language=lang, word_timestamps=True, beam_size=5, vad_filter=True, condition_on_previous_text=False)
        return list(segs), info
    try: segs, info = run("cuda", "float16")
    except Exception: segs, info = run("cpu", "int8")
    print("language:", info.language)
    out, lines = [], []
    for s in segs:
        out.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
        lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] " + " ".join(f"{w.word.strip()}@{w.start:.2f}" for w in s.words))
    json.dump(out, open(os.path.join(wd, "transcript.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(wd, "words.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
