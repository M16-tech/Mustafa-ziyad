# Troubleshooting & machine notes

- **Arabic letters show as boxes or come out disconnected**: the font lacks Arabic presentation forms. `find_font()`
  picks the first installed font that has them (Janna LT, Noto Kufi Arabic, Cairo, Tajawal, Almarai, IBM Plex Sans
  Arabic, Noto Sans Arabic, Segoe UI Bold, Arial Bold, Tahoma Bold, Geeza Pro). Set `"font"` in the config to force one.
  The «الله» ligature is turned off on purpose (several fonts draw it wrongly).
- **Pillow without libraqm** is expected: text is shaped with arabic-reshaper + python-bidi. Latin text passes through.
- **Whisper**: tries the GPU, falls back to CPU (`small` model: ~1–2 min per minute of video). Don't feed it the script
  as a prompt — that made it hallucinate. If the user pasted their script, use it for caption spelling only.
- **ffmpeg**: needs libx264 and prores_ks (any "full" build). No fontconfig needed — nothing uses `drawtext`.
  `showinfo` writes to stderr — don't pass `-v error` when detecting cuts.
- **Person masks** (`matte.py`): downloads `u2net_human_seg.onnx` (176 MB) to `~/.u2net` on first use; CPU ≈ 0.3 s per frame.
  Only compute the seconds that need something behind the speaker.
- **CapCut**
  - Project folder: Windows `%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft`, macOS
    `~/Movies/CapCut/User Data/Projects/com.lveditor.draft` (or `capcut_drafts` in the config).
  - CapCut must be **fully closed** when a project is registered — it rewrites its project list on exit
    (`root_meta_info.json`, a backup is written next to it each time).
  - Transparent clips: ProRes 4444 / QuickTime Animation / PNG-in-MOV work; **WebM alpha shows black**.
  - Keyframes written into the project JSON **jitter** — that's why every animation is exported as rendered pieces
    (entrance / still / exit) instead.
  - The templates come from CapCut 9.5 (Windows). If a much newer CapCut refuses the project, ask the user to make any
    small project with one image, one video, one audio and one caption, then rebuild `assets/capcut_templates.json`
    from it (same structure: material + segment + extra materials per kind) and strip personal paths / device ids.
  - Never inherit AI processing from templates (an "Enhance quality" job once ran on every clip) — `capcut.py` clears it.
- **Premiere**: File → Import the `*_premiere.xml`; if the light-leak layer shows black, set its Blend Mode to Screen.
- **Loudness**: the engine normalises the final mix to −14 LUFS; if a platform still plays it quiet, check the source isn't clipped.
- **Render times** (60 s reel, modern laptop): final only ≈ 3 min; + CapCut pieces ≈ 1 min; + Premiere ProRes layers ≈ 8 min.
  Run long renders in the background.
