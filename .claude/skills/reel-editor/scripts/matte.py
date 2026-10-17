# matte.py — person cut-out masks for the frames where graphics go BEHIND the speaker.
# usage: python matte.py <video> <out_dir> <start>-<end> [<start>-<end> ...]      (seconds)
# writes <out_dir>/<frame:05d>.png (frame index at 30 fps). Runs on CPU (~0.3 s/frame).
import sys, os, subprocess, urllib.request
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

MODEL = os.path.expanduser("~/.u2net/u2net_human_seg.onnx")
URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx"
W, H = 1080, 1920

def ensure_model():
    if not os.path.exists(MODEL) or os.path.getsize(MODEL) < 100_000_000:
        os.makedirs(os.path.dirname(MODEL), exist_ok=True)
        print("downloading", URL); urllib.request.urlretrieve(URL, MODEL)

def run(src, out, a, b, sess, inp):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-i", src, "-t", str(b - a), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    fs = W * H * 3; n = len(raw) // fs; i0 = round(a * 30)
    mean = np.array([0.485, 0.456, 0.406]); std = np.array([0.229, 0.224, 0.225])
    for k in range(n):
        im = Image.frombuffer("RGB", (W, H), raw[k * fs:(k + 1) * fs])
        x = np.asarray(im.resize((320, 320), Image.LANCZOS), np.float32); x = x / max(x.max(), 1e-6)
        x = ((x - mean) / std).transpose(2, 0, 1)[None].astype(np.float32)
        p = sess.run(None, {inp: x})[0][0, 0]
        p = (p - p.min()) / (p.max() - p.min() + 1e-8)
        Image.fromarray((p * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)).save(
            os.path.join(out, f"{i0 + k:05d}.png"))
    print(f"{a}-{b}s: {n} masks")

def head_box(out, idx):
    """(top_y, left_x, right_x) of the head in a saved mask — use it to place things above / behind the head."""
    m = np.asarray(Image.open(os.path.join(out, f"{idx:05d}.png"))) > 128
    ys = np.where(m.any(1))[0]; top = ys[0]; row = np.where(m[top + 40])[0]
    return int(top), int(row.min()), int(row.max())

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    ensure_model()
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"]); inp = sess.get_inputs()[0].name
    for r in sys.argv[3:]:
        a, b = map(float, r.split("-")); run(src, out, a, b, sess, inp)
        mid = round((a + b) / 2 * 30); print("head (top, left, right) at", mid / 30, "s:", head_box(out, mid))
