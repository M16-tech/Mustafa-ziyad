---
name: reel-editor
description: Edit vertical talking-head videos (Reels / TikTok / Shorts) end to end and hand back an editable CapCut project and/or Premiere layers — word-synced motion graphics and cards, captions (Arabic/RTL included), counters, icons, graphics behind the speaker, light leaks over jump cuts, b-roll treatment, generated sound effects and music mix, platform safe zones, end card, and a publish-ready MP4. Use it whenever someone gives a video file or a CapCut project and asks to edit/montage it, add animations/captions/motion graphics, make it ready to post, or export it to CapCut or Premiere — e.g. "منتجلي هذا الفيديو", "سويله انميشنات وترجمة", "مشروعي بكاب كت اسمه…", "edit this reel", "add motion graphics", "make a CapCut project from this video" — even if the skill isn't named.
---

# Reel editor

You turn a raw vertical video (or a rough cut in CapCut) into a finished reel: motion graphics timed to the words,
captions, transitions, sound design and music, safe for every platform's UI — and you hand it back as a **final MP4**
plus an **editable CapCut project** (every animation its own clips) and/or **Premiere layers** (ProRes + XML).

Talk to the user in their language and keep it simple — many users are editors, not programmers. Do the technical work
yourself; ask only for decisions that are theirs (style, brand, music, what to export).

`<skill>` below = this skill's base directory. Work files go in a work dir (the session scratchpad, or
`~/reel-editor-work/<video-name>`). Read `references/style-guide.md` before designing — it holds the rules that make
the result look professional instead of templated. `references/recipes.md` maps sentences to visuals;
`references/troubleshooting.md` covers fonts, Whisper, ffmpeg and CapCut quirks.

## 1. First run on this computer
```bash
python <skill>/scripts/setup_check.py
```
- Missing Python packages → ask, then `python <skill>/scripts/setup_check.py --install`. Missing ffmpeg → ask, then
  `winget install Gyan.FFmpeg` (Windows) / `brew install ffmpeg` (macOS).
- No style config yet → ask the user once (AskUserQuestion works well): their **name/brand** and **tagline** for the
  end card, the **style** (`news` = serious/trust, `creator` = bold/energetic, `minimal` = clean — see the table in the
  style guide), optional **brand colours**, the **captions language** (RTL for Arabic/Persian/Kurdish/Urdu/Hebrew),
  and optionally a **music folder** they own. Save it:
  `python <skill>/scripts/setup_check.py --config '{"name":"…","tagline":"…","theme":"news","rtl":true,"colors":{"accent":[214,170,60]},"music_dir":"…"}'`
- Run with `PYTHONIOENCODING=utf-8` on Windows so Arabic prints.

## 2. Get the footage
- **A video file**: `python <skill>/scripts/prep.py "<video>" "<work>" [--lang ar]` → `src.mov` (1080×1920, 30 fps working
  copy), `words.txt` (every word with its time), `cuts.txt`, `contact.png`. If the source is horizontal, tell the user it
  was centre-cropped to 9:16.
- **A CapCut project** ("مشروعي بكاب كت اسمه…"): `python <skill>/scripts/from_capcut.py --list`, confirm the name (and
  timeline, if the project has several), then
  `python <skill>/scripts/from_capcut.py "<project>" "<work>/src.mov" [--timeline "Timeline 02"]` and run `prep.py` on it.
  It only *reads* their project. Its printed `CUTS` are the real cuts; `BROLL` lists clips from other sources.
- If they pasted their script, use it for caption spelling (Whisper mangles dialects); timings still come from `words.txt`.

## 3. Look before you design
Open `contact.png`: where is the face, where are the hands, where is empty space (plain wall above the head? chest?),
what is the background. For behind-the-speaker effects and to know the head position per shot:
`python <skill>/scripts/matte.py "<work>/src.mov" "<work>/mattes" 3.0-3.1 12.0-12.1 …` (prints the head box; compute full
ranges only where something goes behind the person).

## 4. Plan, then write the timeline
Plan scene by scene (phrase → visual → time → sound) with `references/recipes.md`: one idea on screen at a time, a
change every 1.5–3 s, every visual on the word that carries it, numbers only as spoken. Then copy
`<skill>/examples/example_reel.py` to `<work>/edit_<name>.py` and replace scenes, captions, `CUTS`, names. Music:
pick from their music folder by measuring (`python <skill>/scripts/analyze_audio.py music <files>`) — you can't hear,
so say which track you chose and why; no music is better than a wrong one. Sound effects are generated automatically.

## 5. Check stills — always, before any render
```bash
python <work>/edit_<name>.py stills 2.0 5.5 9.0 …        # one time inside every scene
```
Look at `stills.png` (red = platform UI): fix every `SAFE-ZONE WARNING`, overlap, covered face, empty space inside a
card, off-centre text. Re-rendering stills takes seconds; a full render takes minutes.

## 6. Render and export
- `python <work>/edit_<name>.py render` → final MP4 (−14 LUFS, ready to post).
- `… capcut` → final MP4 + **new** CapCut project "<name> editable". **Before running, ask the user to close CapCut
  completely and wait for their confirmation** (CapCut rewrites its project list on exit). Result: natural video,
  vignette, light leaks and behind-the-speaker layers on their own tracks; every graphic as entrance/still/exit pieces;
  captions as native CapCut captions; voice, music and every sound effect as separate clips; `grade.cube` for colour.
- `… premiere` → final MP4 + ProRes 4444 layers + `<name>_premiere.xml` (File → Import → the sequence opens laid out).
Long renders: run in the background.

## 7. Hand over
Send/point to the MP4, name the CapCut project, and tell the user in a few lines: what each scene does, the music
chosen, what to check **by ear** (music level, effect timing), and how to tweak in CapCut — move/resize an element:
select its pieces → right-click → *Create compound clip*; change a duration: stretch the still (PNG) piece; captions:
edit them all at once; colour: Adjust → LUT → `grade.cube`, or their own grade.

When they give feedback, fix the cause (engine, layout rule, timing) — and if it's a taste rule that will apply to
their next videos, add it to `~/.reel-editor/config.json` notes or tell them to keep it in their Claude memory.
