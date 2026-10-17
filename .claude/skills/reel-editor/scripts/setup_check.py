# setup_check.py — check (and optionally install) everything reel-editor needs, and write the user's style config.
#   python setup_check.py                 → report what is missing
#   python setup_check.py --install       → pip-install missing Python packages (asks nothing; Claude asks the user first)
#   python setup_check.py --config '{"name": "...", "tagline": "...", "theme": "news", "colors": {"accent": [0,150,255]},
#                                    "rtl": true, "leaks": "warm", "music_dir": "..."}'   → save ~/.reel-editor/config.json
import sys, os, json, shutil, subprocess, importlib, importlib.util

PKGS = {"PIL": "pillow", "numpy": "numpy", "arabic_reshaper": "arabic-reshaper", "bidi": "python-bidi",
        "faster_whisper": "faster-whisper", "onnxruntime": "onnxruntime", "fontTools": "fonttools"}
DATA = os.path.join(os.path.expanduser("~"), ".reel-editor")

def main():
    os.makedirs(DATA, exist_ok=True)
    if "--config" in sys.argv:
        new = json.loads(sys.argv[sys.argv.index("--config") + 1])
        p = os.path.join(DATA, "config.json")
        cfg = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        cfg.update(new); json.dump(cfg, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("saved", p); print(json.dumps(cfg, ensure_ascii=False, indent=2)); return
    ok = True
    print(f"python {sys.version.split()[0]}", "OK" if sys.version_info >= (3, 9) else "— need 3.9+")
    missing = [pip for mod, pip in PKGS.items() if importlib.util.find_spec(mod) is None]
    if missing:
        ok = False; print("missing python packages:", " ".join(missing))
        if "--install" in sys.argv:
            subprocess.run([sys.executable, "-m", "pip", "install", *missing]); missing = []
    else: print("python packages OK")
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool): print(tool, "OK")
        else:
            ok = False
            print(tool, "MISSING →", "winget install Gyan.FFmpeg" if sys.platform.startswith("win") else
                  "brew install ffmpeg" if sys.platform == "darwin" else "sudo apt install ffmpeg")
    if shutil.which("ffmpeg"):
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        for e in ("libx264", "prores_ks"):
            print(f"  encoder {e}:", "OK" if e in enc else "MISSING (install a full ffmpeg build)")
    if not missing:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import mclib, capcut
        print("font:", mclib.FB or "NONE — install Noto Kufi Arabic / Cairo (free) or set \"font\" in config")
        print("CapCut projects folder:", capcut.DRAFTS or "not found (CapCut desktop not installed?) — the MP4 still works")
    cfg = os.path.join(DATA, "config.json")
    print("style config:", cfg if os.path.exists(cfg) else "none yet → ask the user (name, tagline, style, colours) and save it with --config")
    print("ALL GOOD" if ok else "fix the items above")

if __name__ == "__main__":
    main()
