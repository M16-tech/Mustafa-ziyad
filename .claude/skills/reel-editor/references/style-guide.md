# Style guide — taste rules that hold for every reel

These rules came from a real editor's corrections over several published reels (one of them reached 56K views).
Each one fixes something that looked amateur. When a new situation isn't covered, ask: *does this look like a
channel people trust, or like a template?*

## Pick the style with the user (saved in `~/.reel-editor/config.json`)
| preset | for | look | motion |
|---|---|---|---|
| `news` | politics, economy, education, analysis, anything that needs trust | navy cards, muted gold accent, gold captions | restrained `rise` / `slide` / `wipe`, no bounce |
| `creator` | lifestyle, tech, tips, personal brands | near-black cards, bright yellow accent, white captions with black stroke | snappier `pop` allowed |
| `minimal` | business, medical, clean brands | white cards, dark text | calm `rise` / `fade` |
Brand colours override any preset: `"colors": {"accent": [r,g,b], "panel": [r,g,b], "text": [r,g,b]}`.
Serious topics → `news` motion even with brand colours (no bouncy pops on a political reel).

## Layout
- **Platform safe zones (Reels / TikTok / Shorts)** — measured on the real apps:
  nothing above **y = 260** (status bar, "Following / For You" tabs, camera icon), nothing below **y = 1440**
  (account name, caption, music), nothing right of **x = 910** below **y = 700** (like/comment/share/follow column),
  60 px left margin. Background elements may pass under the UI; text and cards may not. Content centre `CX = 500`.
  `finalize()` prints `SAFE-ZONE WARNING`; `stills()` paints the forbidden zones red. Fix every warning.
- **Where graphics live depends on the shot** — look at `contact.png` first:
  standing / mid shot with plain background → over the chest, y ≈ 800–1300;
  seated wide shot with hands gesturing → on the wall **above the head**, between y 270 and (head top − 30)
  (`matte.py` prints the head top per shot); if that band is thin, use single-line cards and the space beside the head.
  Never cover the face; avoid covering hands while they gesture.
- One idea on screen at a time; clear the zone before the next scene; elements never overlap each other.
- Captions: ≈ y 1375, 3–5 words, the user's own spelling (Whisper mangles dialects), skip them during a big
  full-screen statement that already shows the same words.

## Cards and text
- Cards fit their text (`card(..., auto=True)` default, `card2()` for two lines) — no empty space beside the text.
  Fixed widths only for grids / pairs / counters.
- Text is optically centred (the engine centres on the letter body, not on dots).
- Strike-through lines cover only the text (`card(...).tb`); a ✗ badge goes on the card's icon (`.icon_x`).
- Numbers count up (`DynEl`), the card keeps a fixed width while counting. Only show figures the speaker says
  or the user provides — never invent statistics, sources or quotes.

## Depth (behind the speaker)
`El(..., z=-1)` draws behind the person (needs `matte.py` masks for those seconds). Use it for things that belong to
the world around them: a flag (only its lower edge fading behind the head), a chart line drawn across the wall, an
idea bulb rising out of the head. Text that must be read stays in front.

## Colour
**Never bake a grade by default.** Deliver natural footage; the vignette is its own layer; `grade.cube` (LUT) is
exported for the user to apply and tune (CapCut: Adjust → LUT; Premiere: Lumetri). A baked grade was rejected.

## Motion between shots
- Every real cut (from the user's rough cut) gets a light leak (generated, `leaks: warm|gold|cool|off`) and a soft
  whoosh — a *different* whoosh each time (repeated identical sounds were called "cheap").
- **No automatic zoom** (`zoom_end=1.0`): a per-shot push-in was "too much". The user adds zoom where they want it.
- Never freeze the last frame and never let size jump at the end: the end-card tail plays the last moments backwards.

## B-roll (clips from other sources)
`from_capcut.py` flags them. Brief that worked: almost black & white (`docu_look`), white `Flash` on its in/out cuts
(replaces the light leak there), a riser into it, flash sound + low hit, a tension music bed under it
(`R.beds`), quote captions in **white** placed where the clip's own banners/logo aren't. Don't cover, crop away or
fake the source's branding, and don't put cards over the b-roll.

## Sound
- Music bed **26 dB under the voice** (never louder than −24); swells under the end card. Pick tracks by measuring
  (`analyze_audio.py`) and say honestly you can't hear them — the user confirms by ear.
- Sound effects are normalised against the voice (their loudest 50 ms), aligned to the visual (one-shots: onset;
  whooshes: peak ~0.08 s after the move starts), rotated so none repeats back-to-back. Final mix −14 LUFS, limiter −1 dB.
- No cartoon pops / notification dings on serious content.

## Ending
End card = the creator's name + tagline + the reel's **closing question or key message** + a call to action
(e.g. «اكتبلي رأيك بالتعليقات»). Not a generic "follow" alone.

## Their projects are theirs
Read the user's CapCut project, never write to it. Everything you deliver is a new file / a new CapCut project.
To fix something underneath edits they already made in your project, re-render the media file it references with
the same name, length, fps and size (keep the old one as `_backup`) while CapCut is closed.
