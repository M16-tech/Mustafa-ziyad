# from_capcut.py — rebuild a CapCut rough cut as one clean 1080x1920 / 30 fps source file (READ-ONLY on the draft).
# usage: python from_capcut.py --list                                   newest drafts (+ their timelines)
#        python from_capcut.py "<draft>" <out.mov> [--timeline "Timeline 02"]
# Handles several timelines per project and compound clips (one level). Prints, per piece, which file it comes from,
# then CUTS (all piece boundaries = real cuts) and BROLL (pieces from a different source than the main camera: other
# resolution / other folder) — b-roll gets its own treatment (B&W, documentary transitions, tension sound).
import json, os, sys, glob, re, subprocess

def _drafts():
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft"),
              os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")):
        if os.path.isdir(p): return p
    sys.exit("CapCut project folder not found")
D = _drafts()

def _res(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                       capture_output=True, text=True).stdout.strip().split(",")
    return tuple(sorted(int(x) for x in o if x.strip().isdigit()))

def timelines(folder):
    pj = os.path.join(folder, "Timelines", "project.json")
    if not os.path.exists(pj): return {"Timeline 01": os.path.join(folder, "draft_content.json")}
    P = json.load(open(pj, encoding="utf-8"))
    out = {}
    for t in P["timelines"]:
        if t.get("is_marked_delete"): continue
        p = os.path.join(folder, "Timelines", t["id"], "draft_content.json")
        out[t["name"]] = p if os.path.exists(p) else os.path.join(folder, "draft_content.json")
    return out

def pieces(d):
    """main-track pieces as (path, src_start, dur, tgt_start), expanding one level of compound clips."""
    A = {x["id"]: (k, x) for k, v in d["materials"].items() if isinstance(v, list) for x in v if isinstance(x, dict) and "id" in x}
    out = []
    for s in [s for t in d["tracks"] if t["type"] == "video" and t["flag"] == 0 for s in t["segments"]]:
        k, m = A[s["material_id"]]
        a, du, tg = s["source_timerange"]["start"] / 1e6, s["source_timerange"]["duration"] / 1e6, s["target_timerange"]["start"] / 1e6
        if abs(s.get("speed", 1.0) - 1.0) > 1e-3: print("NOTE: speed change at", round(tg, 2), "— not reproduced")
        comp = [A[r][1] for r in s["extra_material_refs"] if r in A and A[r][0] == "drafts"]
        if m.get("path"):
            out.append((m["path"], a, du, tg))
        elif comp:
            sub = comp[0]["draft"]; sub = json.loads(sub) if isinstance(sub, str) else sub
            for p, sa, sd, st in pieces(sub):           # keep the part of the inner timeline [a, a+du]
                lo, hi = max(st, a), min(st + sd, a + du)
                if hi - lo > 1e-3: out.append((p, sa + (lo - st), hi - lo, tg + (lo - a)))
        else:
            print("NOTE: unknown segment type at", round(tg, 2))
    return out

def main():
    if sys.argv[1] == "--list":
        for f in sorted(glob.glob(D + "/*/draft_content.json"), key=os.path.getmtime, reverse=True)[:10]:
            folder = os.path.dirname(f)
            tl = {n: round(json.load(open(p, encoding="utf-8"))["duration"] / 1e6, 1) for n, p in timelines(folder).items()}
            print(f"{os.path.basename(folder):30s} {tl}")
        return
    name, out = sys.argv[1], sys.argv[2]
    tname = sys.argv[sys.argv.index("--timeline") + 1] if "--timeline" in sys.argv else "Timeline 01"
    d = json.load(open(timelines(os.path.join(D, name))[tname], encoding="utf-8"))
    extra = [t["type"] for t in d["tracks"] if not (t["type"] == "video" and t["flag"] == 0)]
    if extra: print("NOTE: the timeline also has other tracks (ignored — tell the user):", extra)
    P = pieces(d)
    # main camera = the (resolution, folder) group with the most screen time; everything else is b-roll
    from collections import Counter
    key = {p: (_res(p), os.path.dirname(p)) for p in {x[0] for x in P}}
    tot = Counter(); [tot.__setitem__(key[p], tot[key[p]] + du) for p, a, du, tg in P]
    main = tot.most_common(1)[0][0]
    args, fc, cuts, broll = [], [], [], []
    for i, (p, a, du, tg) in enumerate(P):
        args += ["-ss", f"{a:.6f}", "-t", f"{du:.6f}", "-i", p]
        fc.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30,setsar=1[v{i}];"
                  f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        if i: cuts.append(round(tg, 3))
        cam = key[p] == main
        if not cam: broll.append((round(tg, 3), round(tg + du, 3), os.path.basename(p)))
        print(f"{tg:7.2f}s  {os.path.basename(p):40s} in {a:8.3f}s  dur {du:6.3f}s{'' if cam else '   <- b-roll?'}")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(P))) + f"concat=n={len(P)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", out], check=True)
    print("CUTS =", cuts); print("BROLL =", broll)

if __name__ == "__main__":
    main()
