# sfxsynth.py — sound effects generated from scratch (no samples, no licences).
# ensure() writes a small palette into ~/.reel-editor/sfx/ once and returns {kind: [files]} for reelkit.
# Kinds: click (UI tick), swish (soft air for cards), whoosh (transitions), hit (low cinematic thump),
#        riser (build-up into a moment), flash (bright camera-flash whoosh), readout (digital counting blips), strike.
import os, wave
import numpy as np

SR = 48000
OUT = os.path.join(os.path.expanduser("~"), ".reel-editor", "sfx")

def _write(path, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())

def _noise(n, rng): return rng.standard_normal(n).astype(np.float32)

def _sweep_filter(x, f0, f1, q=1.2):
    """state-variable band-pass whose centre moves from f0 to f1 (Hz) over the sound."""
    n = len(x); fc = np.geomspace(max(f0, 20), max(f1, 20), n)
    lo = bp = 0.0; out = np.empty(n, np.float32); damp = 1.0 / q
    for i in range(n):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        hi = x[i] - lo - damp * bp; bp += f * hi; lo += f * bp; out[i] = bp
    return out

def _env(n, attack, release, curve=2.0):
    t = np.linspace(0, 1, n); a = max(1e-3, attack)
    e = np.where(t < a, (t / a) ** curve, ((1 - t) / max(1e-3, 1 - a)) ** release)
    return e.astype(np.float32)

def click(seed):
    rng = np.random.default_rng(seed); n = int(0.06 * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * (2400 + 500 * seed) * t) * np.exp(-t * 90)
    tick = _noise(n, rng) * np.exp(-t * 400)
    return 0.6 * tone + 0.5 * np.diff(np.concatenate([[0], tick]))

def swish(seed, dur=0.42):
    rng = np.random.default_rng(seed); n = int(dur * SR)
    x = _sweep_filter(_noise(n, rng), 400 + 120 * seed, 2200 + 250 * seed, q=1.4)
    return x * _env(n, 0.55, 2.2)

def whoosh(seed, dur=1.0):
    rng = np.random.default_rng(100 + seed); n = int(dur * SR)
    up = _sweep_filter(_noise(n, rng), 150 + 30 * seed, 1700 + 180 * seed, q=1.1)
    body = _sweep_filter(_noise(n, rng), 90, 600 + 60 * seed, q=0.8)
    return (0.7 * up + 0.5 * body) * _env(n, 0.5 + 0.04 * (seed % 3), 2.6)

def hit(seed):
    rng = np.random.default_rng(200 + seed); n = int(0.9 * SR); t = np.arange(n) / SR
    f = 62 * (1 + 1.2 * np.exp(-t * 18)) - 6 * seed
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    trans = _sweep_filter(_noise(n, rng), 900, 200, q=0.7) * np.exp(-t * 60)
    return body + 0.12 * trans

def riser(seed, dur=2.0):
    rng = np.random.default_rng(300 + seed); n = int(dur * SR); t = np.arange(n) / SR
    air = _sweep_filter(_noise(n, rng), 300, 6000, q=1.6)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 900, n)) / SR) * 0.25
    e = (t / dur) ** 2.4; e[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    return (air + tone) * e

def flash(seed, dur=0.9):
    rng = np.random.default_rng(400 + seed); n = int(dur * SR); t = np.arange(n) / SR
    w = _sweep_filter(_noise(n, rng), 900, 7000 if seed == 0 else 3000, q=1.3) * _env(n, 0.45, 3.0)
    shimmer = sum(np.sin(2 * np.pi * f * t + p) for f, p in ((5300, 0), (6100, 1), (7400, 2))) * np.exp(-np.abs(t - dur * 0.45) * 9) * 0.08
    return w + shimmer

def readout(seed, dur=1.4):
    rng = np.random.default_rng(500 + seed); out = np.zeros(int(dur * SR), np.float32); pos = 0
    while pos < len(out) - 2000:
        f = rng.choice([1600, 2000, 2400, 3000]); n = int(rng.uniform(0.025, 0.05) * SR); tt = np.arange(n) / SR
        out[pos:pos + n] += np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 * np.exp(-tt * 30); pos += n + int(rng.uniform(0.02, 0.06) * SR)
    return out

def strike(seed): return swish(seed + 7, dur=0.22)

PALETTE = {
    "click": [(click, s) for s in range(3)], "swish": [(swish, s) for s in range(4)], "trans": [(whoosh, s) for s in range(8)],
    "impact": [(hit, s) for s in range(2)], "riser": [(riser, 0)], "flashin": [(flash, 0)], "flashout": [(flash, 1)],
    "readout": [(readout, 0)], "strike": [(strike, 0)], "soft": [(whoosh, 20), (whoosh, 21)], "hit": [(hit, 2), (hit, 3)],
}

def ensure():
    os.makedirs(OUT, exist_ok=True); files = {}
    for kind, gens in PALETTE.items():
        files[kind] = []
        for fn, seed in gens:
            p = os.path.join(OUT, f"{kind}_{seed}.wav")
            if not os.path.exists(p): _write(p, fn(seed))
            files[kind].append(p.replace("\\", "/"))
    return files

# level vs the voice (dB), alignment and offset after the visual event — same contract as reelkit FXP
LEVELS = {"click": (-19, "onset", 0.0), "swish": (-18, "peak", 0.08), "strike": (-16, "peak", 0.06), "trans": (-18, "peak", 0.0),
          "impact": (-13, "peak", 0.12), "soft": (-19, "peak", 0.25), "readout": (-24, "onset", 0.0), "riser": (-22, "peak", 0.0),
          "flashin": (-15, "peak", 0.0), "flashout": (-17, "peak", 0.0), "hit": (-14, "onset", 0.0)}

def palette():
    f = ensure()
    return {k: (f[k],) + LEVELS[k] for k in f}

if __name__ == "__main__":
    for k, v in ensure().items(): print(k, len(v))
