# analyze_audio.py — "listen" to music / SFX by numbers (Claude can't hear).
# usage: python analyze_audio.py music <files...>   → tempo, key (major/minor), brightness, dynamics
#        python analyze_audio.py sfx   <files...>   → attack, active length, brightness, noisiness, peak
# Reading it: news beds = minor or neutral, steady (dyn < 12 dB), centroid 900–2000 Hz, 100–130 bpm.
#             formal ticks = active < 0.1 s; soft swishes = active 0.1–0.7 s, flat > 0.15; low hits = centroid < 450 Hz.
import sys, os, subprocess
import numpy as np

SR = 22050
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NAMES = "C C# D D# E F F# G G# A A# B".split()

def load(f, secs):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-t", str(secs), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def music(f):
    a = load(f, 75); n, h = 2048, 512
    fr = np.stack([a[i:i + n] for i in range(0, len(a) - n, h)]) * np.hanning(n)
    S = np.abs(np.fft.rfft(fr, axis=1)); fq = np.fft.rfftfreq(n, 1 / SR)
    cen = np.median((S * fq).sum(1) / (S.sum(1) + 1e-9))
    flux = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1); flux -= flux.mean()
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]; lags = np.arange(len(ac)) * h / SR
    rng = (lags > 0.33) & (lags < 1.0); bpm = 60 / lags[rng][ac[rng].argmax()]
    m = (fq > 60) & (fq < 2000); pc = np.round(12 * np.log2(fq[m] / 261.63)) % 12
    chroma = np.array([S[:, m][:, pc == k].sum() for k in range(12)])
    key = max(((np.corrcoef(np.roll(p, k), chroma)[0, 1], NAMES[k] + (" maj" if p is MAJ else " min")) for p in (MAJ, MIN) for k in range(12)))[1]
    rms = np.sqrt((fr ** 2).mean(1)); dyn = 20 * np.log10(np.percentile(rms, 95) / (np.percentile(rms, 10) + 1e-9))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    print(f"{dur:6.1f}s bpm~{bpm:4.0f} key {key:7s} centroid {cen:5.0f}Hz dyn {dyn:4.1f}dB  {os.path.basename(f)}")

def sfx(f):
    a = load(f, 8)
    if len(a) < 1000: return
    w = int(SR * 0.01); e = np.sqrt(np.convolve(a * a, np.ones(w) / w, "same"))
    pk = e.max(); on = np.argmax(e > pk * 0.1); pki = e.argmax(); act = (e > pk * 0.1).sum() / SR
    seg = a[max(0, pki - 512):pki + 512]; S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); fq = np.fft.rfftfreq(len(seg), 1 / SR)
    cen = (S * fq).sum() / (S.sum() + 1e-9); flat = np.exp(np.mean(np.log(S + 1e-9))) / (S.mean() + 1e-9)
    print(f"attack {(pki - on) / SR:5.2f}s active {act:5.2f}s centroid {cen:5.0f} flat {flat:.2f} peak {20 * np.log10(pk):5.1f}dB  {os.path.basename(f)}")

if __name__ == "__main__":
    fn = music if sys.argv[1] == "music" else sfx
    for f in sys.argv[2:]: fn(f)
