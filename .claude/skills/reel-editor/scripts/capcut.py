# capcut.py — turn a Reel timeline into an editable CapCut desktop project (tested with CapCut 9.5 on Windows).
# Every graphic becomes its own clips, cut by its motion (entrance / still / sweep / exit) and rendered by the engine, captions become
# native CapCut captions (edit words, font, colour, size for all of them at once), voice / music / every sound effect
# are separate audio clips. Built from known-good CapCut draft structures (assets/capcut_templates.json, personal data removed).
#
# CapCut must be CLOSED when register=True (it rewrites its project list on exit). A backup of the list is kept.
import os, sys, json, copy, uuid, time, shutil, math, subprocess
import numpy as np
from PIL import Image
import mclib
from mclib import W, H, CONFIG

US = 1_000_000
def drafts_dir():
    """CapCut's project folder (Windows / macOS), or CONFIG["capcut_drafts"] if set."""
    if CONFIG.get("capcut_drafts"): return CONFIG["capcut_drafts"]
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft"),
              os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")):
        if os.path.isdir(p): return p.replace("\\", "/")
    return None
DRAFTS = drafts_dir()

def capcut_running():
    """True if the CapCut app is open (it must be closed before a project is registered)."""
    try:
        if sys.platform.startswith("win"):
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe"], capture_output=True, text=True).stdout
            return "CapCut.exe" in out
        return subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0
    except Exception:
        return False
TPL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "capcut_templates.json"), encoding="utf-8"))

def uid(): return str(uuid.uuid4()).upper()
def us(t): return int(round(t * US))
def now_us(): return int(time.time() * US)


class CapCutDraft:
    def __init__(self, name, total):
        self.name, self.total = name, total
        self.draft_id = uid()
        d = copy.deepcopy(TPL["draft"])
        d.update(id=self.draft_id, name="", duration=us(total), fps=30.0, create_time=0, update_time=0)
        d["canvas_config"] = {"ratio": "original", "width": W, "height": H, "background": None}
        self.d = d

    # -- low level --
    def _segment(self, kind, start, dur, path, mat_fields, src_dur=None):
        t = TPL[kind]
        mat = copy.deepcopy(t["material"]); mat["id"] = uid(); mat["path"] = path.replace("\\", "/"); mat.update(mat_fields)
        va = mat.get("video_algorithm")
        if isinstance(va, dict):     # never inherit AI processing (e.g. "Enhance quality") from the template draft
            for k in ("algorithms", "ai_background_configs", "aigc_generate_list", "gameplay_configs", "ai_in_painting_config"): va[k] = []
            for k in ("time_range", "quality_enhance", "super_resolution", "noise_reduction", "deflicker", "motion_blur_config",
                      "complement_frame_config", "smart_complement_frame"): va[k] = None
            va["path"] = ""
        self.d["materials"][t["material_list"]].append(mat)
        refs = []
        for lst, obj in t["extras"]:
            o = copy.deepcopy(obj); o["id"] = uid()
            if lst == "material_animations": o["animations"] = []
            if lst == "speeds": o["speed"] = 1.0
            self.d["materials"].setdefault(lst, []).append(o); refs.append(o["id"])
        s = copy.deepcopy(t["segment"])
        s.update(id=uid(), material_id=mat["id"], extra_material_refs=refs, common_keyframes=[], keyframe_refs=[])
        s["target_timerange"] = {"start": us(start), "duration": us(dur)}
        if s.get("source_timerange") is not None or kind != "text":
            s["source_timerange"] = {"start": 0, "duration": us(src_dur if src_dur is not None else dur)}
        return s

    def _track(self, kind, segs, flag=None):
        tr = copy.deepcopy(TPL[kind]["track"]); tr["id"] = uid()
        if flag is not None: tr["flag"] = flag
        tr["segments"] = segs
        for s in segs: s["track_render_index"] = len(self.d["tracks"])
        self.d["tracks"].append(tr)
        return tr

    @staticmethod
    def _kf(prop, pts):
        return {"id": uid(), "material_id": "", "property_type": prop, "keyframe_list": [
            {"id": uid(), "curveType": "Line", "time_offset": int(o), "left_control": {"x": 0.0, "y": 0.0},
             "right_control": {"x": 0.0, "y": 0.0}, "values": [float(v)], "string_value": "", "graphID": ""} for o, v in pts]}

    # -- public --
    def video(self, path, start=0.0, dur=None, volume=0.0):
        dur = dur or self.total
        s = self._segment("video", start, dur, path, {"width": W, "height": H, "duration": us(dur), "material_name": os.path.basename(path), "has_audio": False})
        s["volume"] = volume
        s["clip"] = {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": 0.0, "y": 0.0}, "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}
        self._track("video", [s], flag=0)

    def audio_tracks(self, clips, own_track=()):
        """clips: [(start_s, dur_s, path)] → packed onto as few audio tracks as possible.
        paths in own_track (voice, music) get a track each, first, in that order."""
        for st, du, p in [c for c in clips if c[2] in own_track]:
            s = self._segment("audio", st, du, p, {"duration": us(du), "name": os.path.splitext(os.path.basename(p))[0]}); s["volume"] = 1.0
            self._track("audio", [s])
        lanes = []
        for st, du, p in sorted(c for c in clips if c[2] not in own_track):
            s = self._segment("audio", st, du, p, {"duration": us(du), "name": os.path.splitext(os.path.basename(p))[0]})
            s["volume"] = 1.0
            for ln in lanes:
                if ln[0] <= st + 1e-3: ln[0] = st + du; ln[1].append(s); break
            else: lanes.append([st + du, [s]])
        for ln in lanes: self._track("audio", ln[1])

    def _place(self, kind, start_f, n_f, path, box, extra=None):
        """one clip whose picture is `box` = (x0, y0, w, h) in canvas pixels; the file is padded to an exact 9:16 frame,
        so CapCut's fit-to-canvas makes scale = w_file / 1080 the real size (pivot = the element's own centre)."""
        x0, y0, w, h = box
        fields = {"width": w, "height": h, "material_name": os.path.basename(path)}
        if kind == "video": fields.update(duration=us(n_f / 30), has_audio=False)
        s = self._segment(kind, start_f / 30, n_f / 30, path, fields)
        if kind == "video": s["volume"] = 0.0
        cx, cy = x0 + w / 2, y0 + h / 2
        s["clip"] = {"scale": {"x": w / W, "y": w / W}, "rotation": 0.0, "transform": {"x": (cx - W / 2) / (W / 2), "y": (H / 2 - cy) / (H / 2)},
                     "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}
        s["uniform_scale"] = {"on": True, "value": 1.0}
        return s

    def graphics(self, els, out_dir, total, fps=30):
        """Every element is cut into pieces that follow its motion, rendered by the engine itself (identical to the final):
             moving parts (entrance, light sweep, exit) → ProRes 4444 clips with alpha  (CapCut 9.x on Windows reads them;
             WebM alpha shows black, per-frame keyframes written into the JSON jitter — both tested on CapCut 9.5),
             still parts → one PNG you can stretch to any length.
           The pieces of one element sit back-to-back on one track; z-order between elements is preserved."""
        os.makedirs(out_dir, exist_ok=True)
        lanes, placed, lane_segs = [], [], []
        for i, el in enumerate(els):
            f0 = max(0, round(el.t0 * fps)); f1 = min(round(total * fps), round(el.t1 * fps))
            if f1 - f0 < 2: continue
            def key(f):
                t = f / fps; sc, al, dx, dy, crop = el.state(t)
                sw = bool(el.sweep and el.sweep[0] <= t <= el.sweep[0] + el.sweep[1])
                ck = el.content_key(t) if hasattr(el, "content_key") else None     # DynEl: picture changes (counters…)
                return (round(sc, 4), round(al, 3), round(dx, 1), round(dy, 1), round(crop, 3), sw, ck)
            keys = [key(f) for f in range(f0, f1)]
            # any stretch where the picture doesn't change for ≥ 4 frames (and no light sweep) becomes a still PNG;
            # everything in between (entrance, counting numbers, sweep, exit) becomes an alpha video clip
            groups = []                                   # [key, start_f, end_f]
            for k, f in zip(keys, range(f0, f1)):
                if groups and groups[-1][0] == k: groups[-1][2] = f + 1
                else: groups.append([k, f, f + 1])
            runs = []                                     # [static?, start_f, end_f]
            for k, a_, b_ in groups:
                st = (b_ - a_ >= 4 and not k[5])
                if runs and not st and not runs[-1][0]: runs[-1][2] = b_
                else: runs.append([st, a_, b_])
            segs = []
            for j, (st, a, b) in enumerate(runs):
                frames = []
                for f in ([a] if st else range(a, b)):
                    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0)); el.draw(cv, f / fps); frames.append(cv)
                bb = None
                for fr in frames:
                    g = fr.getbbox()
                    if g: bb = g if bb is None else (min(bb[0], g[0]), min(bb[1], g[1]), max(bb[2], g[2]), max(bb[3], g[3]))
                if bb is None: continue                       # fully transparent run (e.g. first frame of a fade)
                bw = bb[2] - bb[0]; bh = bb[3] - bb[1]
                w = max(bw, math.ceil(bh * 9 / 16)); w += w % 2; h = round(w * 16 / 9); h += h % 2
                cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
                crop = lambda fr: fr.crop((x0, y0, x0 + w, y0 + h))
                tag = "ثبات" if st else ("دخول" if j == 0 else ("طلوع" if j == len(runs) - 1 and b >= f1 - 1 else "حركة"))
                base = os.path.join(out_dir, f"{i:03d}_{a / fps:05.2f}s_{tag}")
                if st:
                    crop(frames[0]).save(base + ".png")
                    segs.append(self._place("photo", a, b - a, base + ".png", (x0, y0, w, h)))
                else:
                    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                                          "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", base + ".mov"], stdin=subprocess.PIPE)
                    p.communicate(b"".join(crop(fr).tobytes() for fr in frames))
                    segs.append(self._place("video", a, b - a, base + ".mov", (x0, y0, w, h)))
            if not segs: continue
            t0, t1 = f0 / fps, f1 / fps
            floor = max([ln for ln, a, b in placed if a < t1 and b > t0], default=-1) + 1
            li = floor
            while li < len(lanes) and any(a < t1 and b > t0 for a, b in lanes[li]): li += 1
            while len(lanes) <= li: lanes.append([]); lane_segs.append([])
            lanes[li].append((t0, t1)); lane_segs[li] += segs; placed.append((li, t0, t1))
        for segs in lane_segs: self._track("photo", sorted(segs, key=lambda s: s["target_timerange"]["start"]), flag=2)

    def captions(self, caps, x=None, y=1375, size=7.0, color=None, stroke=None, font=None):
        """caps: [(t0, t1, text)] → native CapCut captions (one style for all, editable together)."""
        x = x or (500 if mclib.RTL else 580); font = font or mclib.FB
        color = color or (mclib.ACCENT if mclib.THEME.get("cap_grad") else (255, 255, 255)); stroke = stroke or mclib.THEME["cap_stroke"]
        segs = []
        hexc = "#%02X%02X%02X" % color
        for t0, t1, tx in caps:
            st = {"fill": {"content": {"render_type": "solid", "solid": {"color": [c / 255 for c in color]}}},
                  "font": {"path": font, "id": ""},
                  "strokes": [{"content": {"render_type": "solid", "solid": {"color": [c / 255 for c in stroke]}}, "width": 0.08, "mode": 0}],
                  "size": size, "useLetterColor": True,
                  "shadows": [{"diffuse": 0.15, "alpha": 0.6, "distance": 6.0, "content": {"render_type": "solid", "solid": {"color": [0, 0, 0]}}, "angle": -45}],
                  "range": [0, len(tx)]}
            content = json.dumps({"text": tx, "styles": [st]}, ensure_ascii=False)
            s = self._segment("text", t0, t1 - t0, "", {"content": content, "base_content": content, "recognize_text": tx,
                              "recognize_task_id": "", "words": {"start_time": [], "end_time": [], "text": []},
                              "text_color": hexc, "font_path": font, "font_size": size, "border_color": "#%02X%02X%02X" % stroke,
                              "border_width": 0.08, "alignment": 1})
            s["clip"] = {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": (x - W / 2) / (W / 2), "y": (H / 2 - y) / (H / 2)},
                         "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}
            segs.append(s)
        self._track("text", segs)

    # -- write the project folder (+ register it in CapCut's project list) --
    def save(self, cover=None, register=True):
        if not DRAFTS: raise RuntimeError("CapCut project folder not found — is CapCut desktop installed? (or set capcut_drafts in ~/.reel-editor/config.json)")
        if register and capcut_running(): raise RuntimeError("CapCut is open — ask the user to close it completely, then run again")
        fold = os.path.join(DRAFTS, self.name).replace("\\", "/")
        if os.path.exists(fold): shutil.rmtree(fold)
        os.makedirs(os.path.join(fold, "Timelines", self.draft_id))
        js = json.dumps(self.d, ensure_ascii=False)
        for p in (os.path.join(fold, "draft_content.json"), os.path.join(fold, "Timelines", self.draft_id, "draft_content.json")):
            open(p, "w", encoding="utf-8").write(js)
        n = now_us()
        json.dump({"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": False, "use_float_render": False},
                   "create_time": n, "id": uid(), "main_timeline_id": self.draft_id,
                   "timelines": [{"create_time": n, "id": self.draft_id, "is_marked_delete": False, "name": "Timeline 01", "update_time": n}],
                   "update_time": n, "version": 0}, open(os.path.join(fold, "Timelines", "project.json"), "w", encoding="utf-8"))
        json.dump({"dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [self.draft_id], "timelineNames": ["Timeline 01"]}], "layoutOrientation": 1},
                  open(os.path.join(fold, "timeline_layout.json"), "w", encoding="utf-8"))
        open(os.path.join(fold, "draft_settings"), "w").write(
            f"[General]\ndraft_create_time={n // US}\ndraft_last_edit_time={n // US}\nreal_edit_seconds=0\nreal_edit_keys=0\ncloud_last_modify_platform=windows\n")
        meta_id = uid()
        meta = copy.deepcopy(TPL["meta"])
        meta.update(draft_id=meta_id, draft_name=self.name, draft_fold_path=fold, draft_root_path=DRAFTS, draft_cover="draft_cover.jpg",
                    tm_draft_create=n, tm_draft_modified=n, tm_duration=us(self.total))
        meta["draft_timeline_materials_size_"] = 0
        json.dump(meta, open(os.path.join(fold, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)
        if cover: cover.convert("RGB").resize((540, 960)).save(os.path.join(fold, "draft_cover.jpg"), quality=88)
        if register:
            rp = os.path.join(DRAFTS, "root_meta_info.json")
            shutil.copy(rp, rp + f".bak_{n // US}")
            root = json.load(open(rp, encoding="utf-8"))
            root["all_draft_store"] = [e for e in root["all_draft_store"] if e.get("draft_fold_path") != fold]
            e = copy.deepcopy(TPL["root_entry"])
            e.update(draft_cover=fold + "\\draft_cover.jpg", draft_fold_path=fold, draft_id=meta_id, draft_json_file=fold + "\\draft_content.json",
                     draft_name=self.name, draft_root_path=DRAFTS, tm_draft_create=n, tm_draft_modified=n, tm_duration=us(self.total),
                     draft_timeline_materials_size=0)
            root["all_draft_store"].insert(0, e); root["draft_ids"] = root.get("draft_ids", 0) + 1
            json.dump(root, open(rp, "w", encoding="utf-8"), ensure_ascii=False)
        return fold


# ---------------- whole-reel export ----------------
def make_cube(path, grade):
    """3D LUT (.cube, 64³) of the colour part of the grade, so the raw footage can be graded inside CapCut / Premiere."""
    import subprocess
    colour = ",".join(f for f in grade.split(",") if not f.startswith("unsharp"))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "haldclutsrc=level=8", "-frames:v", "1", "-vf", colour + ",format=rgb48le",
                          "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint16).reshape(-1, 3).astype(np.float64) / 65535
    with open(path, "w") as f:
        f.write('TITLE "reel-editor grade"\nLUT_3D_SIZE 64\n')
        f.writelines(f"{r:.6f} {g:.6f} {b:.6f}\n" for r, g, b in a)

def encode_piece(frames, base_path, fps=30):
    """frames: full-canvas RGBA images → one ProRes 4444 clip cropped to their union box (padded to 9:16).
    Returns (path, box) or None if everything is transparent."""
    bb = None
    for fr in frames:
        g = fr.getbbox()
        if g: bb = g if bb is None else (min(bb[0], g[0]), min(bb[1], g[1]), max(bb[2], g[2]), max(bb[3], g[3]))
    if bb is None: return None
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    w = max(bw, math.ceil(bh * 9 / 16)); w += w % 2; h = round(w * 16 / 9); h += h % 2
    x0, y0 = int(round((bb[0] + bb[2]) / 2 - w / 2)), int(round((bb[1] + bb[3]) / 2 - h / 2))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                          "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", base_path + ".mov"], stdin=subprocess.PIPE)
    p.communicate(b"".join(fr.crop((x0, y0, x0 + w, y0 + h)).tobytes() for fr in frames))
    return base_path + ".mov", (x0, y0, w, h)

def export_reel(R, name, export_dir, register=True, caption_size=7.0):
    """R: a finalized reelkit.Reel whose render(export_dir) already ran (layers on disk).
    Tracks (bottom → top): natural video · vignette (delete it if you like) · light leaks · things behind the speaker ·
    graphics (entrance / still / exit pieces) · captions · voice · music · sfx.  No colour grade is baked in:
    grade.cube sits in the export folder for Adjust → LUT if he wants it."""
    from mclib import GRADE
    fps = 30
    make_cube(os.path.join(export_dir, "grade.cube"), GRADE)
    if not getattr(R, "sfx_files", None): R.build_audio(export_dir)
    cc = CapCutDraft(name, R.total)
    cc.video(os.path.join(export_dir, "01_video.mp4"))
    vg = os.path.join(export_dir, "01b_vignette.png")
    if os.path.exists(vg): cc._track("photo", [cc._place("photo", 0, round(R.total * fps), vg, (0, 0, W, H))], flag=2)
    ldir = os.path.join(export_dir, "capcut_layers"); 
    if os.path.exists(ldir): shutil.rmtree(ldir)
    os.makedirs(ldir)
    # light leaks → alpha clips (screen blend rewritten as straight alpha: a = max(rgb), colour = rgb / a)
    segs = []
    for k, L in enumerate(R.leaks):
        f0 = round(L.t0 * fps); frames = []
        for i in range(L.n):
            lk = L.frame((f0 + i) / fps)
            if lk is None: lk = np.zeros((H, W, 3), np.float32)
            a = lk.max(2, keepdims=True); rgb = np.where(a > 1e-4, lk / np.maximum(a, 1e-4), 0)
            frames.append(Image.fromarray((np.concatenate([rgb, a], 2) * 255).clip(0, 255).astype(np.uint8), "RGBA"))
        r = encode_piece(frames, os.path.join(ldir, f"leak_{k + 1}_{L.t0 + L.n / fps / 2:05.2f}s"))
        if r: segs.append(cc._place("video", f0, L.n, r[0], r[1]))
    if segs: cc._track("photo", segs, flag=2)
    # things behind the speaker (already cut to his shape) → one alpha clip per time range
    rngs = []
    for e in sorted(R.BEHIND, key=lambda e: e.t0):
        if rngs and e.t0 <= rngs[-1][1]: rngs[-1][1] = max(rngs[-1][1], e.t1)
        else: rngs.append([e.t0, e.t1])
    segs = []
    for k, (a, b) in enumerate(rngs):
        f0, f1 = round(a * fps), round(min(b, R.src_dur) * fps)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{f0 / fps:.4f}", "-i", R.src, "-frames:v", str(f1 - f0)] + R.vf +
                             ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        fs = W * H * 3; frames = []
        for i in range((len(raw) // fs)):
            fr = Image.frombuffer("RGB", (W, H), raw[i * fs:(i + 1) * fs])
            beh = R.layers(fr, (f0 + i) / fps, f0 + i)[2]
            frames.append(beh if beh is not None else Image.new("RGBA", (W, H), (0, 0, 0, 0)))
        r = encode_piece(frames, os.path.join(ldir, f"behind_{k + 1}_{a:05.2f}s"))
        if r: segs.append(cc._place("video", f0, len(frames), r[0], r[1]))
    if segs: cc._track("photo", segs, flag=2)
    el_dir = os.path.join(export_dir, "capcut_elements")
    if os.path.exists(el_dir): shutil.rmtree(el_dir)
    cc.graphics(R.GFX, el_dir, R.total)
    cc.captions([(e.t0, e.t1, e.text) for e in R.CAPS if getattr(e, "text", None)], size=caption_size)
    clips = [(0.0, R.total, os.path.join(export_dir, "audio", "voice.wav")), (0.0, R.total, os.path.join(export_dir, "audio", "music.wav"))]
    clips += [(st / fps, du / fps, p) for st, du, p in R.sfx_files]
    cc.audio_tracks(clips, own_track=(clips[0][2], clips[1][2]))
    cover = None
    try: cover = R.composite(*R.layers(R.grab(11.5), 11.5, round(11.5 * fps)))
    except Exception: pass
    return cc.save(cover=cover, register=register)
