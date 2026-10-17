# reelkit.py — timeline, audio mix, final render and layer export (Premiere XML / CapCut) for vertical reels.
import os, re, subprocess, urllib.parse
from collections import deque
import numpy as np
from PIL import Image
from mclib import *
import sfxsynth

SR = 48000
QUANT = SR // FPS          # audio samples per video frame

def probe_duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)

def load_mono(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vn"] + (["-af", af] if af else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 1).copy()

def write_wav(path, a):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", path], stdin=subprocess.PIPE)
    p.communicate(np.ascontiguousarray(a[:, 0], np.float32).tobytes())


class Reel:
    """One reel. Build it with add()/sfx()/captions(), call finalize(), then stills() to check and render() to output.
    src must be 1080x1920 (from_capcut.py / prep.py produce that)."""
    def __init__(self, src, out, cuts=(), music=None, fxp=None, tail=1.4, music_db=-26.0, music_swell=2.2,
                 voice_lufs=-13.2, zoom_end=1.0, leak_files=None, leaks=None, leak_opacity=0.5, mattes="mattes",
                 grade=False, vignette=True):
        self.src, self.out, self.cuts, self.music = src, out, list(cuts), music
        self.fxp = fxp or sfxsynth.palette()          # generated sound effects unless the user's own palette is given
        self.src_dur = probe_duration(src); self.total = round(self.src_dur + tail, 2)
        self.music_db, self.music_swell, self.voice_lufs = music_db, music_swell, voice_lufs
        self.zoom_end, self.mattes = zoom_end, mattes
        self.grade = GRADE if grade else None; self.use_vignette = vignette      # colour stays natural by default
        self.vf = ["-vf", self.grade] if self.grade else []
        self.E, self.S, self._rot = [], [], {}
        self.leak_files, self.leak_opacity = leak_files or [], leak_opacity
        self.leak_style = leaks if leaks is not None else CONFIG.get("leaks", "warm")   # warm | gold | cool | off
        self.end_swell_at = None
        self.looks = []          # [(t0, t1, fn(array, t))] e.g. docu_look on b-roll
        self.flashes = []        # mclib.Flash on chosen cuts (replaces the light leak there)
        self.beds = None         # [(path, t0, t1, db_vs_voice, src_offset)] — several music beds
        self.tmp = os.path.join(DATA, "mix.f32")

    # ---- building the timeline ----
    def sfx(self, t, kind, db=0.0):
        if kind not in self.fxp: return
        files, lvl, align, off = self.fxp[kind]
        i = self._rot.get(kind, 0); self._rot[kind] = i + 1            # rotate: never the same sound twice in a row
        self.S.append((t + off, files[i % len(files)], lvl + db, align, kind))

    def add(self, el, kind=None, db=0.0, at=None):
        self.E.append(el)
        if kind: self.sfx(el.t0 if at is None else at, kind, db)
        return el

    def captions(self, caps, cx=None, cy=1375, size=64, maxw=800, until=None, quote=False):
        """caps: [(t0, text), ...]; each caption lasts until the next one (or `until`). quote=True → someone else speaking."""
        cx = cx or (500 if RTL else 580)
        nxt = [c[0] for c in caps[1:]] + [until or self.src_dur]
        for (t0, tx), t1 in zip(caps, nxt):
            if not tx: continue
            sz = fit_size(tx, size, maxw)
            if quote: sp = text_sprite(tx, sz, fill=WHITE, stroke=8, sc=(20, 20, 20), shadow=5)
            elif THEME.get("cap_grad"): sp = text_sprite(tx, sz, grad=(ACCENT_L, ACCENT_D), stroke=8, sc=THEME["cap_stroke"], shadow=5)
            else: sp = text_sprite(tx, sz, fill=WHITE, stroke=9, sc=THEME["cap_stroke"], shadow=5)
            el = El(sp, cx, cy, t0, t1 - 0.02, "popsoft", din=0.14, dout=0.06, exit="cut", cap=True)
            el.text = tx; self.E.append(el)

    def outro(self, t0, question=None, cta=None, name=None, tagline=None):
        """end card: dim the video, show the name/tagline (from config), the closing question (2 lines) and a call to action."""
        name = name or CONFIG.get("name", ""); tagline = tagline if tagline is not None else CONFIG.get("tagline", "")
        cx = 500 if RTL else 580; T = self.total
        self.add(El(full((4, 10, 22), 175), 540, 960, t0, T + 1, "fade", din=0.5, exit=None, bg=True))
        if name: self.add(El(end_card(name, tagline), cx, 800, t0 + 0.1, T + 1, "rise", din=0.7, exit=None, sweep=(t0 + 0.9, 0.8)), "impact")
        y = 1095
        if question:
            l1, l2 = question if isinstance(question, (tuple, list)) else (question, "")
            q = card2(l1, l2, ic="q", h=150, size=44) if l2 else card(900, 120, l1, 48, ic="q")
            self.add(El(q, cx, y, t0 + 0.45, T + 1, "rise", exit=None, din=0.5), "click"); y += 170
        if cta: self.add(El(card(700, 100, cta, 44, ic="chat"), cx, y, t0 + 0.8, T + 1, "rise", exit=None), "click")
        self.end_swell_at = t0 - 0.3

    def finalize(self, trans_kind="trans"):
        """light leak + a different soft whoosh on every real cut (a Flash replaces the leak where one is set)."""
        fl = {round(f.t0 + f.n / 60, 2) for f in self.flashes}
        cuts_leak = [c for c in self.cuts if not any(abs(c - x) < 0.3 for x in fl)]
        if self.leak_files: self.leaks = [Leak(f, c, self.leak_opacity) for c, f in zip(cuts_leak, self.leak_files)]
        elif self.leak_style != "off": self.leaks = [ProcLeak(c, 1.0, self.leak_opacity, seed=i, palette=self.leak_style) for i, c in enumerate(cuts_leak)]
        else: self.leaks = []
        self.leaks += list(self.flashes)
        for c in self.cuts:
            if not any(abs(t - c) < 0.3 for t, *_ in self.S): self.sfx(c, trans_kind)
        self.BEHIND = [e for e in self.E if e.z < 0]
        self.GFX = [e for e in self.E if e.z >= 0 and not e.cap]
        self.CAPS = [e for e in self.E if e.cap]
        self.vigmul = (1 - np.asarray(vignette())[:, :, 3:4].astype(np.float32) / 255)
        bad = check_safe(self.E)
        for b in bad: print("SAFE-ZONE WARNING", b)
        return bad

    # ---- pictures ----
    def matte(self, idx):
        p = os.path.join(self.mattes, f"{idx:05d}.png")
        return Image.open(p).convert("L") if os.path.exists(p) else None

    def layers(self, frame, t, idx):
        z = segment_zoom(t, self.cuts, self.zoom_end, self.total)
        base = np.asarray(apply_zoom(frame, z), np.float32) / 255
        for a, b, fn in self.looks:
            if a <= t < b: base = fn(base, t)
        lk = None
        for L in self.leaks:
            f = L.frame(t)
            if f is not None: lk = f if lk is None else 1 - (1 - lk) * (1 - f)
        beh = None
        act = [e for e in self.BEHIND if e.t0 <= t <= e.t1]
        m = self.matte(idx) if act else None
        if m is not None:
            beh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for el in act: el.draw(beh, t)
            a = np.asarray(beh, np.float32); a[:, :, 3] *= 1 - np.asarray(apply_zoom(m, z), np.float32) / 255
            beh = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        gfx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for el in self.GFX: el.draw(gfx, t)
        cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for el in self.CAPS: el.draw(cap, t)
        return base, lk, beh, gfx, cap

    def composite(self, base, lk, beh, gfx, cap):
        """layer order (same in Premiere / CapCut): video → vignette → light leak (screen) → behind-the-speaker → graphics → captions"""
        if self.use_vignette: base = base * self.vigmul
        rgb = base if lk is None else 1 - (1 - base) * (1 - lk)
        img = Image.fromarray((rgb * 255 + 0.5).clip(0, 255).astype(np.uint8)).convert("RGBA")
        for L in (beh, gfx, cap):
            if L is not None: img.alpha_composite(L)
        return img.convert("RGB")

    def grab(self, t):
        if t > self.src_dur - 0.05: t = max(0.0, 2 * self.src_dur - t - 0.1)          # tail = last moments played backwards
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(min(t, self.src_dur - 0.05)), "-i", self.src, "-frames:v", "1"] + self.vf +
                             ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        return Image.frombuffer("RGB", (W, H), raw)

    def stills(self, times, path="stills.png", guides=True):
        """contact sheet of the finished look at chosen times; guides=True paints the platform UI zones red."""
        out = []
        for t in times:
            im = self.composite(*self.layers(self.grab(t), t, round(t * FPS))).convert("RGBA")
            if guides: im.alpha_composite(safe_guides())
            out.append(im.convert("RGB").resize((360, 640)))
        cols = 6; rows = (len(out) + cols - 1) // cols
        sheet = Image.new("RGB", (360 * cols, 640 * rows), "black")
        for i, im in enumerate(out): sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
        sheet.save(path); return path

    # ---- sound ----
    def build_audio(self, export_dir=None):
        n = int(self.total * SR)
        voice = np.zeros((n, 1), np.float32)
        v = load_mono(self.src, f"loudnorm=I={self.voice_lufs}:TP=-2:LRA=11")[:n]; voice[:len(v)] = v
        r = st_rms(v); speech = r[r > r.max() * 0.1]
        v90 = 20 * np.log10(np.percentile(speech, 90)); vmean = 20 * np.log10(np.sqrt((speech ** 2).mean()))
        music = np.zeros((n, 1), np.float32)
        beds = self.beds or ([(self.music, 0.0, self.total, self.music_db, 0.0)] if self.music else [])
        sw = self.end_swell_at or self.src_dur - 1.4
        for path, b0, b1, db, off in beds:
            m = load_mono(path)[int(off * SR):]
            if not len(m): continue
            m = m * (10 ** ((vmean + db) / 20) / np.sqrt((m[: int(min(len(m), 55 * SR))] ** 2).mean() + 1e-12))
            i0, i1 = int(b0 * SR), min(n, int(b1 * SR)); m = m[: i1 - i0]
            tt = b0 + np.arange(len(m)) / SR; fd = 0.6
            g = np.interp(tt, [b0, b0 + fd, max(b0 + fd, b1 - fd), b1], [0, 1, 1, 0]) if b0 > 0 or b1 < self.total else np.ones(len(m))
            if b1 >= self.total - 0.01: g = g * np.interp(tt, [0, sw, sw + 1.0, self.total - 1.0, self.total], [1, 1, self.music_swell, self.music_swell, 0])
            elif b0 == 0: g = g * np.interp(tt, [0, 0.4], [0, 1])
            music[i0:i0 + len(m)] += m * g[:, None]
        sfx = np.zeros((n, 1), np.float32); clips = []; cache = {}
        for t, f, lvl, align, kind in sorted(self.S):
            if f not in cache: cache[f] = load_mono(f)
            pos, seg = place(sfx, norm_to(cache[f], v90 + lvl), t, 1.0, align=align, maxlen=0.6 if align == "onset" else 1.6, lead=0.8, quant=QUANT)
            clips.append((pos, seg, kind, os.path.splitext(os.path.basename(f))[0]))
        mix = voice + music + sfx
        mix.astype(np.float32).tofile(self.tmp)                    # measure, then hit -14 LUFS (platform target)
        er = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", self.tmp, "-af", "ebur128", "-f", "null", "-"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        Is = re.findall(r"I:\s+(-?[\d.]+) LUFS", er)
        if Is:
            # -13.5 on the mono mix lands at about -14 LUFS after the stereo AAC encode
            k = 10 ** ((-13.5 - float(Is[-1])) / 20); voice *= k; music *= k; sfx *= k; mix *= k
            clips = [(p, s * k, kd, nm) for p, s, kd, nm in clips]
        # keep the mix at -14 LUFS (the final encode's limiter catches peaks); only the exported stems get headroom
        mix.astype(np.float32).tofile(self.tmp)
        pk = np.abs(mix).max()
        if pk > 0.98:
            k = 0.98 / pk; voice *= k; music *= k; sfx *= k; clips = [(p, s * k, kd, nm) for p, s, kd, nm in clips]
        print(f"voice p90 {v90:.1f} dBFS | music {'none' if not beds else str(self.music_db) + ' dB under voice'} | {len(clips)} sfx")
        if export_dir:
            ad = os.path.join(export_dir, "audio"); sd = os.path.join(ad, "sfx"); os.makedirs(sd, exist_ok=True)
            write_wav(os.path.join(ad, "voice.wav"), voice); write_wav(os.path.join(ad, "music.wav"), music); write_wav(os.path.join(ad, "sfx_all.wav"), sfx)
            self.sfx_files = []
            for i, (pos, seg, kind, nm) in enumerate(clips):
                fn = os.path.join(sd, f"{i + 1:02d}_{pos / SR:05.2f}s_{kind}.wav"); write_wav(fn, seg)
                self.sfx_files.append((pos // QUANT, int(np.ceil(len(seg) / QUANT)), fn))

    # ---- render: final mp4 (+ layers for CapCut / Premiere) ----
    def render(self, export_dir=None, premiere=False):
        """final mp4 always. export_dir → also the pieces the CapCut exporter needs (natural video, vignette, audio stems);
        premiere=True → also ProRes 4444 layers + an FCP7 XML that Premiere imports laid out."""
        self.build_audio(export_dir)
        nfr = int(self.total * FPS)
        def enc(args, path, pix):
            return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", pix, "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + args + [path], stdin=subprocess.PIPE)
        H264 = ["-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-profile:v", "high"]
        PRORES = ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"]
        final = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                  "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", self.tmp, "-af", "alimiter=limit=0.89:level=false", "-ac", "2"]
                                 + H264 + ["-crf", "17", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", self.out], stdin=subprocess.PIPE)
        lay = {}
        if export_dir:
            os.makedirs(export_dir, exist_ok=True); P = lambda n: os.path.join(export_dir, n)
            vg = Image.new("RGBA", (W, H), (0, 0, 0, 255)); vg.putalpha(Image.fromarray(((1 - self.vigmul[:, :, 0]) * 255).astype(np.uint8)))
            vg.save(P("01b_vignette.png"))
            lay["video"] = enc(H264 + ["-crf", "14"], P("01_video.mp4"), "rgb24")
            if premiere:
                lay.update(leak=enc(H264 + ["-crf", "16"], P("02_light_leaks_SCREEN.mp4"), "rgb24"), beh=enc(PRORES, P("03_behind_person.mov"), "rgba"),
                           gfx=enc(PRORES, P("04_graphics.mov"), "rgba"), cap=enc(PRORES, P("05_captions.mov"), "rgba"))
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", self.src] + self.vf + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        fsz = W * H * 3; last = None; n_src = 0
        buf = deque(maxlen=nfr - int(self.src_dur * FPS) + 3)       # tail: the last frames play backwards (never a frozen frame)
        blank_rgb = bytes(W * H * 3); blank_rgba = bytes(W * H * 4)
        for i in range(nfr):
            raw = dec.stdout.read(fsz)
            if len(raw) == fsz: last = Image.frombuffer("RGB", (W, H), raw); buf.append(last); n_src = i + 1
            elif buf: last = buf[max(0, len(buf) - 1 - (i - n_src + 1))]
            L = self.layers(last, i / FPS, i)
            final.stdin.write(self.composite(*L).tobytes())
            if lay:
                base, lk, beh, gfx, cap = L
                lay["video"].stdin.write((base * 255 + 0.5).clip(0, 255).astype(np.uint8).tobytes())
                if premiere:
                    lay["leak"].stdin.write(blank_rgb if lk is None else (lk * 255 + 0.5).clip(0, 255).astype(np.uint8).tobytes())
                    lay["beh"].stdin.write(blank_rgba if beh is None else beh.tobytes())
                    lay["gfx"].stdin.write(gfx.tobytes()); lay["cap"].stdin.write(cap.tobytes())
            if i % 300 == 0: print(f"{i}/{nfr}", flush=True)
        for p in [final] + list(lay.values()): p.stdin.close()
        for p in [final] + list(lay.values()): p.wait()
        dec.kill()
        if export_dir and premiere: self.write_xml(export_dir, nfr)
        print("done", self.out)

    # ---- Premiere / FCP7 XML: the whole edit opens already laid out ----
    def write_xml(self, d, nfr, name=None):
        name = name or os.path.splitext(os.path.basename(self.out))[0]
        url = lambda p: "file://localhost/" + urllib.parse.quote(os.path.abspath(p).replace("\\", "/"), safe="/:")
        rate = "<rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate>"; fid = [0]
        def vclip(path, alpha=False, blend=None):
            fid[0] += 1; n = os.path.basename(path)
            return (f'<clipitem id="clip-{fid[0]}"><name>{n}</name><enabled>TRUE</enabled><duration>{nfr}</duration>{rate}'
                    f'<start>0</start><end>{nfr}</end><in>0</in><out>{nfr}</out>' + (f"<compositemode>{blend}</compositemode>" if blend else "")
                    + ("<alphatype>straight</alphatype>" if alpha else "<alphatype>none</alphatype>")
                    + f'<file id="file-{fid[0]}"><name>{n}</name><pathurl>{url(path)}</pathurl>{rate}<duration>{nfr}</duration>'
                    f'<media><video><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height></samplecharacteristics></video></media></file></clipitem>')
        def aclip(path, start, dur):
            fid[0] += 1; n = os.path.basename(path)
            return (f'<clipitem id="clip-{fid[0]}"><name>{n}</name><enabled>TRUE</enabled><duration>{dur}</duration>{rate}'
                    f'<start>{start}</start><end>{start + dur}</end><in>0</in><out>{dur}</out>'
                    f'<file id="file-{fid[0]}"><name>{n}</name><pathurl>{url(path)}</pathurl>{rate}<duration>{dur}</duration>'
                    f'<media><audio><samplecharacteristics><depth>24</depth><samplerate>{SR}</samplerate></samplecharacteristics><channelcount>1</channelcount></audio></media></file>'
                    f'<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>')
        P = lambda n: os.path.join(d, n)
        vtracks = [vclip(P("01_video.mp4")), vclip(P("01b_vignette.png"), True), vclip(P("02_light_leaks_SCREEN.mp4"), blend="screen"),
                   vclip(P("03_behind_person.mov"), True), vclip(P("04_graphics.mov"), True), vclip(P("05_captions.mov"), True)]
        atracks = [[aclip(P("audio/voice.wav"), 0, nfr)], [aclip(P("audio/music.wav"), 0, nfr)]]
        lanes = []
        for st, du, fn in self.sfx_files:
            for ln in lanes:
                if ln[0] <= st: ln[0] = st + du; ln[1].append(aclip(fn, st, du)); break
            else: lanes.append([st + du, [aclip(fn, st, du)]])
        atracks += [ln[1] for ln in lanes]
        fmt = (f"<format><samplecharacteristics>{rate}<width>{W}</width><height>{H}</height><anamorphic>FALSE</anamorphic>"
               f"<pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>")
        xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="sequence-1">'
               f"<name>{name}</name><duration>{nfr}</duration>{rate}<media><video>{fmt}" + "".join(f"<track>{c}</track>" for c in vtracks)
               + f"</video><audio><numOutputChannels>2</numOutputChannels><format><samplecharacteristics><depth>24</depth><samplerate>{SR}</samplerate></samplecharacteristics></format>"
               + "".join("<track>" + "".join(cs) + "</track>" for cs in atracks) + "</audio></media></sequence></xmeml>\n")
        open(P(f"{name}_premiere.xml"), "w", encoding="utf-8").write(xml)
