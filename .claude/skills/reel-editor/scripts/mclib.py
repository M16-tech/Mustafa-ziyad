# mclib.py — motion-graphics engine for vertical reels (Pillow + numpy + ffmpeg).
# Themes, Arabic/RTL-safe text, cards, icons, animated elements, transitions, looks, audio helpers, platform safe zones.
import math, subprocess, os, glob, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import arabic_reshaper
from bidi.algorithm import get_display

W, H, FPS = 1080, 1920, 30
HOME = os.path.expanduser("~").replace("\\", "/")
DATA = HOME + "/.reel-editor"                 # user config, generated sound effects, models
os.makedirs(DATA, exist_ok=True)

def load_config():
    p = os.path.join(DATA, "config.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
CONFIG = load_config()

# ---------------------------------------------------------------- fonts
FONT_DIRS = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"), "C:/Windows/Fonts",
             HOME + "/Library/Fonts", "/Library/Fonts", "/System/Library/Fonts", "/System/Library/Fonts/Supplemental",
             "/usr/share/fonts", HOME + "/.fonts", HOME + "/.local/share/fonts"]
# preferred bold fonts, best first (any that exists AND has every glyph we need wins)
FONT_PREFS = ["Janna-LT-Bold", "JannaLT-Bold", "NotoKufiArabic-Bold", "Cairo-Bold", "Tajawal-Bold", "Almarai-ExtraBold",
              "IBMPlexSansArabic-Bold", "NotoSansArabic-Bold", "segoeuib", "arialbd", "tahomabd", "Arial Bold", "GeezaPro-Bold",
              "DejaVuSans-Bold"]
TEST_AR = "إسماعيل الوعي چگپژ ؟ 0123456789 لا"

def _has_glyphs(path, text):
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(path, fontNumber=0, lazy=True); cmap = f.getBestCmap() or {}
        return all(ord(ch) in cmap for ch in set(text) if not ch.isspace())
    except Exception:
        return False

def find_font(text=None):
    """first preferred font that renders `text` (default: Arabic incl. presentation forms + Persian/Iraqi letters)."""
    need = text or (TEST_AR + arabic_reshaper.reshape(TEST_AR))
    files = []
    for d in FONT_DIRS:
        if d and os.path.isdir(d):
            files += glob.glob(os.path.join(d, "**", "*.tt[fc]"), recursive=True) + glob.glob(os.path.join(d, "**", "*.otf"), recursive=True)
    norm = lambda p: os.path.splitext(os.path.basename(p))[0].lower().replace(" ", "").replace("_", "-")
    for pref in FONT_PREFS:
        key = pref.lower().replace(" ", "").replace("_", "-")
        for p in files:
            if norm(p).endswith(key) or norm(p) == key:
                if _has_glyphs(p, need): return p.replace("\\", "/")
    return None

FB = CONFIG.get("font") or find_font()
if not FB:
    sys.stderr.write("reel-editor: no installed font covers Arabic presentation forms — install Noto Kufi Arabic or Cairo, "
                     "or set \"font\" in ~/.reel-editor/config.json\n")
    FB = find_font("abc") or ""
def set_font(path):
    global FB; FB = path; _fc.clear(); _vb.clear()

# ---------------------------------------------------------------- themes
WHITE = (255, 255, 255); RED = (214, 40, 57); GREEN = (39, 174, 96); BLUE = (52, 120, 220); GRAY = (120, 130, 148)
THEMES = {
    # serious / news / political / educational: navy + muted gold, restrained motion
    "news":    dict(panel=(10, 28, 56), panel_a=232, accent=(214, 170, 60), accent_l=(250, 228, 165), accent_d=(196, 146, 40),
                    text=WHITE, on_accent=(10, 28, 56), cap_grad=True, cap_stroke=(6, 16, 34), enter="rise", dark=(6, 16, 34)),
    # creators / lifestyle / tech: black + bright yellow, punchier motion
    "creator": dict(panel=(18, 18, 20), panel_a=236, accent=(255, 204, 0), accent_l=(255, 232, 120), accent_d=(255, 170, 0),
                    text=WHITE, on_accent=(18, 18, 20), cap_grad=False, cap_stroke=(0, 0, 0), enter="pop", dark=(0, 0, 0)),
    # clean / business / medical: white cards, dark text, calm
    "minimal": dict(panel=(250, 250, 250), panel_a=242, accent=(30, 30, 34), accent_l=(80, 80, 88), accent_d=(10, 10, 12),
                    text=(24, 24, 28), on_accent=WHITE, cap_grad=False, cap_stroke=(0, 0, 0), enter="rise", dark=(0, 0, 0)),
}
THEME = {}
def set_theme(t="news", **override):
    """t: preset name or dict. override: any key (e.g. accent=(0,150,255)) — used for brand colours."""
    base = dict(THEMES[t]) if isinstance(t, str) else dict(t)
    base.update({k: tuple(v) if isinstance(v, list) else v for k, v in override.items()})
    THEME.clear(); THEME.update(base)
    g = globals()
    g.update(PANEL=THEME["panel"], ACCENT=THEME["accent"], ACCENT_L=THEME["accent_l"], ACCENT_D=THEME["accent_d"],
             TEXT=THEME["text"], ON_ACCENT=THEME["on_accent"], DARK=THEME["dark"])
_tc = CONFIG.get("theme", "news")
set_theme(_tc if isinstance(_tc, str) and _tc in THEMES else "news", **(CONFIG.get("colors") or {}))
RTL = CONFIG.get("rtl", True)                # Arabic / Persian / Kurdish / Urdu / Hebrew captions → True

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)  # text is pre-shaped by ar(); raqm would shape it twice
    return _fc[k]

_RS = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True, "ARABIC LIGATURE ALLAH": False, "ARABIC LIGATURE ALLAH ISOLATED FORM": False})
def ar(s): return get_display(_RS.reshape(s))

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def e_out(p): return 1 - (1 - p) ** 3
def e_inout(p): return 3 * p * p - 2 * p * p * p
def e_back(p, s=1.7):
    p = p - 1; return p * p * ((s + 1) * p + s) + 1

# ---------------------------------------------------------------- text
_vb = {}
def vbox(f):
    """optical vertical box of a line relative to the baseline (alef top .. yaa bottom for Arabic; H..g otherwise)."""
    if id(f) not in _vb:
        top, bot = ("ا", "ي") if RTL else ("H", "g")
        _vb[id(f)] = (f.getbbox(ar(top), anchor="ls")[1], f.getbbox(ar(bot), anchor="ls")[3])
    return _vb[id(f)]

def text_sprite(s, size, fnt=None, fill=None, grad=None, stroke=0, sc=None, shadow=0):
    """sprite whose geometric centre is the optical centre of the line (so centring the sprite centres the text)."""
    f = font(fnt or FB, size); t = ar(s); fill = fill or TEXT; sc = sc or DARK
    l, tp, r, b = f.getbbox(t, anchor="ls", stroke_width=stroke)
    vt, vb_ = vbox(f); vc = (vt + vb_) / 2
    pad = stroke + shadow * 3 + 8
    half = int(max(vc - tp, b - vc)) + pad
    w, h = r - l + 2 * pad, 2 * half
    ox, oy = pad - l, half - vc
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text((ox, oy + shadow), t, font=f, fill=170, stroke_width=stroke, anchor="ls")
        img.paste((0, 0, 0, 255), (0, 0), m.filter(ImageFilter.GaussianBlur(shadow)))
    if stroke:
        st = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(st).text((ox, oy), t, font=f, fill=sc + (255,), stroke_width=stroke, stroke_fill=sc + (255,), anchor="ls")
        img = Image.alpha_composite(img, st)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((ox, oy), t, font=f, fill=255, anchor="ls")
    if grad:
        g = np.zeros((h, w, 4), np.uint8)
        ys = np.clip((np.arange(h) - (oy + vt)) / max(1, (vb_ - vt)), 0, 1)[:, None]
        for c in range(3): g[:, :, c] = (grad[0][c] * (1 - ys) + grad[1][c] * ys).astype(np.uint8)
        g[:, :, 3] = 255
        img.paste(Image.fromarray(g, "RGBA"), (0, 0), m)
    else:
        img.paste(fill + (255,), (0, 0), m)
    img.ink = (pad, w - pad)
    return img

def text_w(s, size, fnt=None):
    l, t, r, b = font(fnt or FB, size).getbbox(ar(s)); return r - l

def fit_size(s, size, maxw, fnt=None):
    while size > 20 and text_w(s, size, fnt) > maxw: size -= 2
    return size

def accent_text(s, size, stroke=8, shadow=6, maxw=820):
    """headline text in the theme's accent (gradient); shrinks to fit maxw."""
    return text_sprite(s, fit_size(s, size, maxw), grad=(ACCENT_L, ACCENT_D), stroke=stroke, shadow=shadow)

# ---------------------------------------------------------------- shapes
SS = 4
def shape(w, h, draw_fn, shadow=0, sh_alpha=150):
    p = int(shadow * 3.2) + 2 if shadow else 0          # room for the blur to reach zero (no clipped shadow edges)
    big = Image.new("RGBA", ((w + 2 * p) * SS, (h + 2 * p) * SS), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), SS, p * SS)
    img = big.resize((w + 2 * p, h + 2 * p), Image.LANCZOS)
    if shadow:
        a = img.split()[3].point(lambda v: v * sh_alpha // 255)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 255), (0, int(shadow * 0.5)), a)
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)), img)
    return img, p

_D = "theme"
def panel(w, h, r=30, fill=None, border=_D, bw=4, shadow=16):
    fill = fill or PANEL + (THEME["panel_a"],); border = ACCENT if border == _D else border
    def fn(d, k, o):
        d.rounded_rectangle((o, o, o + w * k - 1, o + h * k - 1), r * k, fill=fill,
                            outline=(border + (255,)) if border else None, width=bw * k)
    return shape(w, h, fn, shadow)

def circle(d_, fill, border=None, bw=0, shadow=12):
    def fn(d, k, o):
        d.ellipse((o, o, o + d_ * k - 1, o + d_ * k - 1), fill=fill, outline=(border + (255,)) if border else None, width=bw * k)
    return shape(d_, d_, fn, shadow)

# ---------------------------------------------------------------- icons (flat, single colour, 100-unit space)
ICONS = ("search chat chart columns doc house coin people person book bulb check cross eye info q news bill cart ship basket "
         "medicine device wallet shield up down scale play heart star clock phone camera mic globe car plane tool fire").split()
def icon(name, size, col=WHITE):
    k = size * 4 / 100.0
    img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img); c = col + (255,)
    P = lambda *pts: [(x * k, y * k) for x, y in pts]
    L = lambda pts, w: d.line(P(*pts), fill=c, width=int(w * k), joint="curve")
    E = lambda x0, y0, x1, y1, **kw: d.ellipse((x0 * k, y0 * k, x1 * k, y1 * k), **kw)
    R = lambda x0, y0, x1, y1, r=0, **kw: d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), r * k, **kw)
    def T(t, sz, y=52):
        f = font(FB, int(sz * k)); tt = ar(t); bb = d.textbbox((0, 0), tt, font=f)
        d.text((50 * k - (bb[0] + bb[2]) / 2, y * k - (bb[1] + bb[3]) / 2), tt, font=f, fill=c)
    if name == "search": E(14, 14, 66, 66, outline=c, width=int(10 * k)); L([(60, 60), (86, 86)], 13)
    elif name == "chat":
        R(8, 14, 92, 70, 16, outline=c, width=int(8 * k)); d.polygon(P((24, 66), (20, 90), (46, 68)), fill=c)
        for x in (32, 50, 68): E(x - 6, 36, x + 6, 48, fill=c)
    elif name == "chart":
        for x0, y0 in ((12, 58), (40, 40), (68, 22)): R(x0, y0, x0 + 20, 86, 3, fill=c)
        L([(8, 92), (92, 92)], 6)
    elif name == "columns":
        d.polygon(P((8, 34), (50, 8), (92, 34)), fill=c)
        for x in (18, 37, 56, 75): R(x, 40, x + 8, 78, 0, fill=c)
        R(10, 82, 90, 92, 2, fill=c)
    elif name == "doc":
        R(18, 6, 82, 94, 8, outline=c, width=int(8 * k))
        for y in (30, 48, 66): L([(32, y), (68, y)], 7)
    elif name == "house": L([(10, 50), (50, 14), (90, 50)], 9); R(22, 46, 78, 90, 4, outline=c, width=int(8 * k)); R(42, 64, 58, 90, 2, fill=c)
    elif name == "coin": E(10, 10, 90, 90, outline=c, width=int(8 * k)); T("$", 60, 50)
    elif name in ("people", "person"):
        def person(cx, s, cc):
            d.ellipse(((cx - 12 * s) * k, (38 - 26 * s) * k, (cx + 12 * s) * k, (38 - 2 * s) * k), fill=cc)
            d.pieslice(((cx - 24 * s) * k, 40 * k, (cx + 24 * s) * k, (40 + 48 * s) * k), 180, 360, fill=cc)
        if name == "people": person(24, 0.8, col + (170,)); person(76, 0.8, col + (170,)); person(50, 1.0, c)
        else: person(50, 1.25, c)
    elif name == "book":
        d.polygon(P((50, 24), (8, 16), (8, 80), (50, 88)), outline=c, width=int(7 * k))
        d.polygon(P((50, 24), (92, 16), (92, 80), (50, 88)), outline=c, width=int(7 * k)); L([(50, 24), (50, 88)], 7)
    elif name == "bulb": E(22, 6, 78, 62, fill=c); R(36, 58, 64, 78, 4, fill=c); R(40, 82, 60, 92, 4, fill=c)
    elif name == "check": L([(18, 52), (40, 74), (84, 26)], 13)
    elif name == "cross": L([(24, 24), (76, 76)], 13); L([(76, 24), (24, 76)], 13)
    elif name == "eye":
        d.chord((6 * k, 22 * k, 94 * k, 110 * k), 200, 340, outline=c, width=int(8 * k))
        d.chord((6 * k, -10 * k, 94 * k, 78 * k), 20, 160, outline=c, width=int(8 * k)); E(36, 36, 64, 64, fill=c)
    elif name == "info": E(8, 8, 92, 92, outline=c, width=int(8 * k)); E(44, 22, 56, 34, fill=c); R(44, 42, 56, 76, 3, fill=c)
    elif name == "q": T("؟" if RTL else "?", 92)
    elif name == "bill":
        R(6, 24, 94, 76, 8, outline=c, width=int(7 * k)); E(36, 36, 64, 64, outline=c, width=int(6 * k)); T("$", 26, 50)
        for x in (16, 84): E(x - 4, 46, x + 4, 54, fill=c)
    elif name == "cart": L([(6, 18), (20, 18), (30, 66), (80, 66), (90, 32), (24, 32)], 8); E(30, 74, 44, 88, fill=c); E(66, 74, 80, 88, fill=c)
    elif name == "ship":
        d.polygon(P((6, 60), (94, 60), (80, 86), (18, 86)), fill=c)
        for x0, y0 in ((22, 40), (42, 40), (62, 40), (32, 22), (52, 22)): R(x0, y0, x0 + 17, y0 + 16, 2, fill=c)
    elif name == "basket": d.polygon(P((8, 44), (92, 44), (80, 88), (20, 88)), fill=c); d.arc((26 * k, 14 * k, 74 * k, 62 * k), 180, 360, fill=c, width=int(7 * k))
    elif name == "medicine": R(12, 30, 88, 70, 20, outline=c, width=int(7 * k)); R(12, 30, 50, 70, 20, fill=c)
    elif name == "device": R(8, 14, 92, 70, 6, outline=c, width=int(8 * k)); R(44, 70, 56, 82, 0, fill=c); R(28, 82, 72, 90, 3, fill=c)
    elif name == "wallet": R(8, 22, 92, 84, 10, outline=c, width=int(8 * k)); R(58, 42, 92, 64, 6, fill=c); L([(14, 22), (70, 8), (76, 22)], 6)
    elif name == "shield": d.polygon(P((50, 6), (88, 20), (84, 56), (50, 94), (16, 56), (12, 20)), fill=c)
    elif name == "up": d.polygon(P((50, 10), (90, 62), (64, 62), (64, 90), (36, 90), (36, 62), (10, 62)), fill=c)
    elif name == "down": d.polygon(P((50, 90), (90, 38), (64, 38), (64, 10), (36, 10), (36, 38), (10, 38)), fill=c)
    elif name == "scale":
        L([(50, 12), (50, 86)], 7); L([(18, 26), (82, 26)], 7); R(30, 84, 70, 92, 3, fill=c)
        d.chord((6 * k, 34 * k, 34 * k, 62 * k), 0, 180, fill=c); d.chord((66 * k, 34 * k, 94 * k, 62 * k), 0, 180, fill=c)
        for a, b in (((20, 26), (8, 48)), ((20, 26), (32, 48)), ((80, 26), (68, 48)), ((80, 26), (92, 48))): L([a, b], 4)
    elif name == "news":
        R(8, 14, 92, 86, 8, outline=c, width=int(7 * k)); R(18, 26, 48, 50, 3, fill=c)
        for y in (30, 44): L([(56, y), (82, y)], 6)
        for y in (60, 72): L([(18, y), (82, y)], 6)
    elif name == "play": d.polygon(P((30, 16), (84, 50), (30, 84)), fill=c)
    elif name == "heart":
        E(10, 18, 52, 58, fill=c); E(48, 18, 90, 58, fill=c); d.polygon(P((12, 46), (88, 46), (50, 90)), fill=c)
    elif name == "star":
        pts = [(50 + (44 if i % 2 == 0 else 18) * math.sin(i * math.pi / 5), 54 - (44 if i % 2 == 0 else 18) * math.cos(i * math.pi / 5)) for i in range(10)]
        d.polygon(P(*pts), fill=c)
    elif name == "clock": E(8, 8, 92, 92, outline=c, width=int(8 * k)); L([(50, 24), (50, 52), (70, 64)], 8)
    elif name == "phone": R(28, 6, 72, 94, 10, outline=c, width=int(7 * k)); E(45, 80, 55, 90, fill=c)
    elif name == "camera": R(8, 28, 92, 84, 10, fill=c); R(32, 16, 68, 32, 4, fill=c); E(32, 38, 68, 74, fill=(0, 0, 0, 0)); E(38, 44, 62, 68, fill=c)
    elif name == "mic": R(36, 6, 64, 60, 14, fill=c); d.arc((24 * k, 30 * k, 76 * k, 74 * k), 0, 180, fill=c, width=int(7 * k)); L([(50, 74), (50, 92)], 7); L([(34, 92), (66, 92)], 7)
    elif name == "globe":
        E(8, 8, 92, 92, outline=c, width=int(7 * k)); d.ellipse((30 * k, 8 * k, 70 * k, 92 * k), outline=c, width=int(6 * k))
        L([(10, 50), (90, 50)], 6); L([(16, 30), (84, 30)], 5); L([(16, 70), (84, 70)], 5)
    elif name == "car":
        d.polygon(P((10, 56), (24, 30), (76, 30), (90, 56), (90, 74), (10, 74)), fill=c); E(18, 64, 38, 84, fill=c); E(62, 64, 82, 84, fill=c)
    elif name == "plane": d.polygon(P((48, 6), (56, 6), (58, 40), (94, 60), (94, 68), (58, 58), (56, 84), (68, 92), (36, 92), (48, 84), (46, 58), (8, 68), (8, 60), (46, 40)), fill=c)
    elif name == "tool": L([(22, 78), (66, 34)], 14); E(56, 10, 92, 46, outline=c, width=int(9 * k))
    elif name == "fire": d.polygon(P((50, 6), (78, 44), (84, 70), (66, 92), (34, 92), (16, 70), (26, 40), (40, 52)), fill=c)
    elif name.startswith("#"): T(name[1:], 64)                     # number badge: "#3" / "#٣"
    else: T(name[:2], 60)                                         # fallback: a short label
    return img.resize((size, size), Image.LANCZOS)

def icon_badge(name, d_, bg=None, fg=None, shadow=10, ring=None):
    bg = bg or ACCENT; fg = fg or ON_ACCENT
    img, p = circle(d_, bg + (255,), border=ring, bw=4 if ring else 0, shadow=shadow)
    ic = icon(name, int(d_ * 0.56), fg)
    img.alpha_composite(ic, (p + (d_ - ic.width) // 2, p + (d_ - ic.height) // 2))
    return img

# ---------------------------------------------------------------- cards
def card(w, h, txt, size=50, ic=None, border=_D, ic_bg=None, ic_fg=None, fill=None, tcol=None, center=False, auto=True):
    """one-line card, icon on the reading side. auto=True (default) fits the width to the text — no dead space."""
    tcol = tcol or TEXT
    if auto: w = min(w, text_w(txt, size) + 2 * 30 + ((h - 34) + 22 if ic else 0))
    img, p = panel(w, h, r=h // 4 if h < 160 else 36, fill=fill, border=border)
    bd = h - 34
    if RTL:
        x_txt_end = p + w - 22
        if ic:
            img.alpha_composite(icon_badge(ic, bd, bg=ic_bg, fg=ic_fg, shadow=0), (x_txt_end - bd, p + (h - bd) // 2)); x_txt_end -= bd + 22
        size = fit_size(txt, size, x_txt_end - (p + 26)); ts = text_sprite(txt, size, fill=tcol)
        tx = p + (w - ts.width) // 2 if (center and not ic) else x_txt_end - ts.width + 8
        icon_x = (x_txt_end + 22 + bd // 2) if ic else None
    else:
        x_txt_start = p + 22
        if ic:
            img.alpha_composite(icon_badge(ic, bd, bg=ic_bg, fg=ic_fg, shadow=0), (x_txt_start, p + (h - bd) // 2)); x_txt_start += bd + 22
        size = fit_size(txt, size, (p + w - 26) - x_txt_start); ts = text_sprite(txt, size, fill=tcol)
        tx = p + (w - ts.width) // 2 if (center and not ic) else x_txt_start - 8
        icon_x = (p + 22 + bd // 2) if ic else None
    img.alpha_composite(ts, (tx, p + (h - ts.height) // 2))
    img.tb = (tx + ts.ink[0], tx + ts.ink[1], p + h // 2); img.icon_x = icon_x; img.pad = p
    return img

def card2(l1, l2, ic=None, size=48, h=168, ic_bg=None, ic_fg=None, border=_D, maxw=940):
    """two-line card (lead line + accent line), width fitted to the longer line."""
    bd = h - 48 if ic else 0
    while True:
        t1 = text_sprite(l1, size); t2 = text_sprite(l2, size, grad=(ACCENT_L, ACCENT_D))
        tw = max(t1.ink[1] - t1.ink[0], t2.ink[1] - t2.ink[0])
        if tw + 2 * 34 + (bd + 26 if ic else 0) <= maxw or size <= 28: break
        size -= 2
    w = min(maxw, tw + 2 * 34 + (bd + 26 if ic else 0))
    img, p = panel(w, h, r=40, border=border)
    if RTL:
        xr = p + w - 30
        if ic: img.alpha_composite(icon_badge(ic, bd, bg=ic_bg, fg=ic_fg, shadow=0), (xr - bd, p + (h - bd) // 2)); xr -= bd + 26
        for t, yc in ((t1, h * 0.31), (t2, h * 0.69)): img.alpha_composite(t, (xr - t.ink[1], int(p + yc - t.height / 2)))
    else:
        xl = p + 30
        if ic: img.alpha_composite(icon_badge(ic, bd, bg=ic_bg, fg=ic_fg, shadow=0), (xl, p + (h - bd) // 2)); xl += bd + 26
        for t, yc in ((t1, h * 0.31), (t2, h * 0.69)): img.alpha_composite(t, (xl - t.ink[0], int(p + yc - t.height / 2)))
    return img

def pill(txt, size=46, bg=None, fg=None, padx=34, pady=14):
    bg = bg or ACCENT; fg = fg or ON_ACCENT
    ts = text_sprite(txt, size, fill=fg)
    w, h = ts.width + 2 * padx - 16, ts.height + 2 * pady - 16
    img, p = panel(w, h, r=h // 2, fill=bg + (255,), border=None, shadow=10)
    img.alpha_composite(ts, (p + (w - ts.width) // 2, p + (h - ts.height) // 2))
    return img

def tile(label, ic, w=230, h=190):
    """square-ish tile: icon on top, label below (for rows of 3)."""
    img, p = panel(w, h, r=32)
    b = icon_badge(ic, 100, shadow=0); img.alpha_composite(b, (p + (w - b.width) // 2, p + 14))
    t = text_sprite(label, fit_size(label, 42, w - 30)); img.alpha_composite(t, (p + (w - t.width) // 2, p + int(h * 0.8) - t.height // 2))
    return img

def bar(w, h, col, r=None):
    return shape(w, h, lambda d, k, o: d.rounded_rectangle((o, o, o + w * k - 1, o + h * k - 1), (r or h // 2) * k, fill=col + (255,)), shadow=4)[0]

def arrow(length=120, th=12, col=None):
    col = col or ACCENT
    def fn(d, k, o):
        y = o + 20 * k
        d.line((o, y, o + (length - 26) * k, y), fill=col + (255,), width=th * k)
        d.polygon([(o + length * k, y), (o + (length - 34) * k, y - 20 * k), (o + (length - 34) * k, y + 20 * k)], fill=col + (255,))
    return shape(length, 40, fn, shadow=4)[0]

def glow(d_, col=None, a=150):
    img = Image.new("RGBA", (d_, d_), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse((d_ * 0.25, d_ * 0.25, d_ * 0.75, d_ * 0.75), fill=(col or ACCENT) + (a,))
    return img.filter(ImageFilter.GaussianBlur(d_ * 0.12))

def rays(d_, col=None, n=8):
    col = col or ACCENT
    def fn(dr, k, o):
        c = d_ * k / 2 + o
        for i in range(n):
            a = i * 2 * math.pi / n - math.pi / 2; r0, r1 = d_ * k * 0.36, d_ * k * 0.48
            dr.line((c + r0 * math.cos(a), c + r0 * math.sin(a), c + r1 * math.cos(a), c + r1 * math.sin(a)), fill=col + (255,), width=int(9 * k))
    return shape(d_, d_, fn)[0]

def news_card(w=760, h=128, tag=None):
    img, p = panel(w, h, r=22, fill=(250, 250, 252, 245), border=None, shadow=16)
    d = ImageDraw.Draw(img)
    tg = pill(tag or ("عاجل" if RTL else "BREAKING"), 40, bg=RED, fg=WHITE, padx=26, pady=10)
    tx = p + w - tg.width - 6 if RTL else p + 6
    img.alpha_composite(tg, (tx, p + (h - tg.height) // 2))
    x0, x1 = (p + 30, p + w - tg.width - 20) if RTL else (p + tg.width + 20, p + w - 30)
    for i, (y, ww) in enumerate(((p + 38, 0.95), (p + 76, 0.6))):
        L = int((x1 - x0) * ww)
        box = (x1 - L, y, x1, y + 16) if RTL else (x0, y, x0 + L, y + 16)
        d.rounded_rectangle(box, 8, fill=(190, 196, 206, 255) if i else (120, 128, 142, 255))
    return img

def end_card(name, tagline=""):
    """name + accent rule + tagline block for the outro (place at ~ (500, 800))."""
    img = Image.new("RGBA", (820, 400), (0, 0, 0, 0))
    n1 = text_sprite(name, fit_size(name, 112, 780), fill=WHITE, shadow=6); img.alpha_composite(n1, ((820 - n1.width) // 2, 100 - n1.height // 2))
    b = bar(360, 7, ACCENT); img.alpha_composite(b, ((820 - b.width) // 2, 190))
    if tagline:
        n2 = text_sprite(tagline, fit_size(tagline, 80, 780), grad=(ACCENT_L, ACCENT_D), shadow=6); img.alpha_composite(n2, ((820 - n2.width) // 2, 275 - n2.height // 2))
    return img

def full(col=(0, 0, 0), a=150): return Image.new("RGBA", (W, H), col + (a,))

def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H * 0.42) / (H * 0.62)) ** 2)
    a = np.clip((r - 0.55) / 0.6, 0, 1) ** 1.6 * 120 + np.clip((y - H * 0.70) / (H * 0.30), 0, 1) ** 1.3 * 95
    arr = np.zeros((H, W, 4), np.uint8); arr[:, :, 3] = np.clip(a, 0, 200).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def iraq_flag_behind(stripe=200, alpha=0.92):
    """example of a flag that sits BEHIND the speaker (z=-1): red+white solid, only the black stripe fades out downward."""
    w, h = W, stripe * 3
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for i, c in enumerate(((206, 17, 38), WHITE, (0, 0, 0))): d.rectangle((0, i * stripe, w, (i + 1) * stripe), fill=c + (255,))
    ts = text_sprite("الله أكبر", int(stripe * 0.58), fill=(0, 122, 61)); img.alpha_composite(ts, ((w - ts.width) // 2, int(stripe * 1.5) - ts.height // 2))
    arr = np.asarray(img).astype(np.float32)
    xs = np.linspace(0, 1, w)[None, :]; ys = np.linspace(0, 1, h)[:, None]
    arr[:, :, :3] = np.clip(arr[:, :, :3] * (1 + 0.09 * np.sin(xs * 8 + ys * 3) - 0.045)[:, :, None], 0, 255)
    yy = np.arange(h)[:, None]
    a = np.where(yy < 2 * stripe, 1.0, np.clip(1 - (yy - 2 * stripe) / stripe, 0, 1) ** 1.3) * alpha
    arr[:, :, 3] *= np.broadcast_to(a, (h, w))
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

# ---------------------------------------------------------------- animated element
class El:
    """sprite on screen from t0 to t1. enter: rise | pop | popsoft | slide | wipe | wipel | fade. exit: fade | drop | cut | None.
    z=-1 → drawn BEHIND the speaker (needs person masks for those frames)."""
    def __init__(self, sprite, cx, cy, t0, t1, enter=None, exit="fade", din=0.38, dout=0.22,
                 frm=(0, 0), bob=0, sweep=None, spin=0, z=0, cap=False, bg=False):
        self.s = sprite; self.cx, self.cy = cx, cy; self.t0, self.t1 = t0, t1
        self.enter = enter or THEME.get("enter", "rise"); self.exit, self.din, self.dout = exit, din, dout
        self.frm = frm; self.bob = bob; self.sweep = sweep; self.spin = spin; self.z = z
        self.cap = cap; self.bg = bg

    def state(self, t):
        """(scale, alpha, dx, dy, crop) at time t — shared by the renderer and the CapCut / Premiere exporters."""
        pi = clamp((t - self.t0) / self.din); po = clamp((self.t1 - t) / self.dout) if self.exit else 1.0
        sc, al, dx, dy, crop = 1.0, 1.0, 0.0, 0.0, 1.0
        if self.enter == "pop": sc = 0.6 + 0.4 * e_back(pi) if pi < 1 else 1.0; al = e_out(clamp(pi * 2.5))
        elif self.enter == "rise": q = e_out(pi); sc = 0.94 + 0.06 * q; dy = (1 - q) * 26; al = e_out(clamp(pi * 1.8))
        elif self.enter == "popsoft": sc = 0.85 + 0.15 * e_out(pi); al = e_out(clamp(pi * 2))
        elif self.enter == "slide": q = e_out(pi); dx, dy = self.frm[0] * (1 - q), self.frm[1] * (1 - q); al = e_out(clamp(pi * 2))
        elif self.enter in ("wipe", "wipel"): crop = e_inout(pi)
        elif self.enter == "fade": al = e_out(pi)
        if self.exit and po < 1:
            q = e_out(po)
            if self.exit == "fade": al *= q; sc *= 0.9 + 0.1 * q
            elif self.exit == "drop": al *= q; dy += (1 - q) * 40
            elif self.exit == "cut": al *= 1 if po > 0 else 0
        if self.bob: dy += math.sin((t - self.t0) * 2.4) * self.bob
        return sc, al, dx, dy, crop

    def draw(self, cv, t):
        if t < self.t0 or t > self.t1: return
        sc, al, dx, dy, crop = self.state(t)
        s = self.s
        if crop < 1:
            cw = max(1, int(s.width * crop)); c = Image.new("RGBA", s.size, (0, 0, 0, 0))
            from_right = (self.enter == "wipe") == RTL          # "wipe" follows the reading direction
            if from_right: c.paste(s.crop((s.width - cw, 0, s.width, s.height)), (s.width - cw, 0))
            else: c.paste(s.crop((0, 0, cw, s.height)), (0, 0))
            s = c
        if self.sweep and self.sweep[0] <= t <= self.sweep[0] + self.sweep[1]:
            q = (t - self.sweep[0]) / self.sweep[1]
            band = Image.new("L", s.size, 0); bd = ImageDraw.Draw(band); x = -s.width * 0.4 + q * s.width * 1.8
            bd.polygon([(x, 0), (x + 90, 0), (x + 30, s.height), (x - 60, s.height)], fill=120)
            band = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(14)), s.split()[3])
            a0 = s.split()[3]; s = s.copy(); s.paste((255, 255, 255, 255), (0, 0), band); s.putalpha(a0)
        if self.spin: s = s.rotate(self.spin * (1 - e_out(clamp((t - self.t0) / self.din))), resample=Image.BICUBIC)
        if abs(sc - 1) > 0.003:
            s = s.resize((max(1, int(s.width * sc)), max(1, int(s.height * sc))), Image.BICUBIC, reducing_gap=2.0)
        if al < 0.999:
            a = s.split()[3].point(lambda v: int(v * al)); s = s.copy(); s.putalpha(a)
        x = int(self.cx + dx - s.width / 2); y = int(self.cy + dy - s.height / 2)
        cv.alpha_composite(s, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

class DynEl(El):
    """element whose picture changes (counters, shrinking bars…). frame_fn(t) -> (key, make_sprite)."""
    def __init__(self, frame_fn, cx, cy, t0, t1, enter=None, **kw):
        self.fn = frame_fn; self._cache = {}
        super().__init__(self._get(t1)[1], cx, cy, t0, t1, enter, **kw)
    def _get(self, t):
        k, mk = self.fn(t)
        if k not in self._cache: self._cache[k] = mk()
        return k, self._cache[k]
    def content_key(self, t): return self._get(t)[0]
    def draw(self, cv, t):
        if self.t0 <= t <= self.t1: self.s = self._get(t)[1]
        super().draw(cv, t)

# ---------------------------------------------------------------- transitions (all screen-blended over the video)
class Leak:
    """light-leak clip from a file (user's own pack), centred on a cut."""
    def __init__(self, path, t_center, opacity=0.5, scale=(540, 960)):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={scale[0]}:{scale[1]},fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (scale[0] * scale[1] * 3)
        self.fr = np.frombuffer(raw, np.uint8)[: n * scale[0] * scale[1] * 3].reshape(n, scale[1], scale[0], 3)
        self.t0 = t_center - n / 30 / 2; self.n = n; self.op = opacity
    def frame(self, t):
        i = int((t - self.t0) * 30)
        if i < 0 or i >= self.n: return None
        env = math.sin(math.pi * (i + 0.5) / self.n) ** 0.7 * self.op
        return np.asarray(Image.fromarray(self.fr[i]).resize((W, H), Image.BILINEAR), np.float32) / 255 * env

class ProcLeak:
    """generated light leak (no files, no licence): warm soft blobs drifting across the frame, centred on a cut."""
    PALETTES = {"warm": [(1.0, 0.55, 0.15), (1.0, 0.8, 0.35), (0.95, 0.3, 0.15)], "cool": [(0.4, 0.7, 1.0), (0.7, 0.85, 1.0), (0.5, 0.5, 0.95)],
                "gold": [(1.0, 0.75, 0.3), (1.0, 0.9, 0.6), (0.9, 0.6, 0.2)]}
    def __init__(self, t_center, dur=1.0, opacity=0.55, seed=0, palette="warm"):
        self.n = int(round(dur * 30)); self.t0 = t_center - self.n / 30 / 2; self.op = opacity
        rng = np.random.default_rng(seed); cols = self.PALETTES.get(palette, self.PALETTES["warm"])
        self.blobs = [dict(x0=rng.uniform(-0.3, 0.3) + (0 if i else -0.4), y0=rng.uniform(0.1, 0.9), vx=rng.uniform(0.5, 1.1) * (1 if seed % 2 else -1),
                           vy=rng.uniform(-0.3, 0.3), r=rng.uniform(0.35, 0.7), col=np.array(cols[i % len(cols)], np.float32)) for i in range(3)]
        y, x = np.mgrid[0:240, 0:135].astype(np.float32); self.gx, self.gy = x / 135, y / 240
    def frame(self, t):
        i = int((t - self.t0) * 30)
        if i < 0 or i >= self.n: return None
        q = (i + 0.5) / self.n; env = math.sin(math.pi * q) ** 0.8 * self.op
        acc = np.zeros((240, 135, 3), np.float32)
        for b in self.blobs:
            cx = b["x0"] + 0.5 + b["vx"] * (q - 0.5); cy = b["y0"] + b["vy"] * (q - 0.5)
            d2 = ((self.gx - cx) * 1.0) ** 2 + ((self.gy - cy) * 0.56) ** 2
            acc += np.exp(-d2 / (b["r"] ** 2 * 0.18))[:, :, None] * b["col"]
        acc = np.clip(acc, 0, 1) * env
        return np.asarray(Image.fromarray((acc * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255

class Flash:
    """documentary white flash centred on a cut."""
    def __init__(self, t_center, dur=0.30, strength=0.95, col=(1.0, 1.0, 1.0)):
        self.n = max(3, int(round(dur * 30))); self.t0 = t_center - self.n / 30 / 2; self.k = strength; self.col = np.array(col, np.float32)
    def frame(self, t):
        i = int((t - self.t0) * 30)
        if i < 0 or i >= self.n: return None
        env = (1 - abs((i + 0.5) / self.n * 2 - 1)) ** 0.6 * self.k
        return np.broadcast_to(self.col * env, (H, W, 3)).astype(np.float32)

# ---------------------------------------------------------------- looks (per time range, applied to the video only)
_vig_docu = None
def docu_look(a, t, sat=0.10, contrast=1.18, grain=0.045, vig=0.45):
    """'almost black & white' documentary look for b-roll: 10 % colour, more contrast, film grain, dark edges."""
    global _vig_docu
    if _vig_docu is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.6)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
        _vig_docu = (1 - np.clip((r - 0.45) / 0.75, 0, 1) ** 1.5 * vig)[:, :, None]
    g = (a * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    o = np.clip(((g + (a - g) * sat) - 0.5) * contrast + 0.5, 0, 1)
    n = np.random.default_rng(int(t * 30)).standard_normal((H // 3, W // 3)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 0.25 + 0.5) * 255).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255 - 0.5
    return np.clip(o * _vig_docu + n[:, :, None] * grain * 2, 0, 1)

# optional colour grade — never baked by default; exported as a LUT (grade.cube) for the user to apply and tune
GRADE = ("curves=master='0/0 0.10/0.06 0.5/0.5 0.85/0.90 1/1',eq=contrast=1.06:saturation=1.12:gamma=0.98,"
         "colorbalance=rs=0.02:bs=0.03:rm=0.03:gm=0.01:bm=-0.03:rh=0.02:bh=-0.02,unsharp=5:5:0.7:5:5:0")

def apply_zoom(img, z, cx=540, cy=560):
    if abs(z - 1) < 0.002: return img
    w, h = W / z, H / z; x0 = clamp(cx - w / 2, 0, W - w); y0 = clamp(cy - h / 2, 0, H - h)
    return img.resize(img.size, Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))

def segment_zoom(t, cuts, z_end=1.0, last_end=None):
    """optional slow push-in per shot (off by default: z_end=1.0)."""
    if z_end == 1.0: return 1.0
    b = [0.0] + list(cuts) + [last_end or 1e9]
    for a, c in zip(b, b[1:]):
        if a <= t < c: return 1.0 + (z_end - 1.0) * e_inout(clamp((t - a) / max(0.1, c - a)))
    return 1.0

# ---------------------------------------------------------------- audio helpers
def env_peak(a, sr=48000):
    m = np.abs(a).max(1); win = int(sr * 0.01)
    e = np.convolve(m, np.ones(win) / win, "same"); pk = int(e.argmax())
    return int(np.argmax(e > e[pk] * 0.25)) / sr, pk / sr

def place(mix, a, t, gain, sr=48000, align="onset", maxlen=None, lead=1.2, fade=0.08, quant=None):
    """mix sound `a` into `mix` so its onset (or peak) lands at time t. Returns (pos, placed samples)."""
    on, pk = env_peak(a, sr); ref = on if align == "onset" else pk
    start_in = (ref - lead if (align == "peak" and ref > lead) else 0.0) if align == "peak" else max(0.0, on - 0.01)
    seg = a[int(start_in * sr):]
    if maxlen: seg = seg[:int(maxlen * sr)]
    seg = seg.copy()
    fi = min(len(seg), int(0.004 * sr if align == "onset" else 0.05 * sr)); seg[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = min(len(seg), int(fade * sr * 3)); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    pos = int((t - (ref - start_in)) * sr)
    if quant: pos = int(round(pos / quant)) * quant
    if pos < 0: seg = seg[-pos:]; pos = 0
    end = min(len(mix), pos + len(seg)); mix[pos:end] += seg[:end - pos] * gain
    return pos, seg[:end - pos] * gain

def st_rms(a, sr=48000, win=0.05):
    m = a.mean(1) if a.ndim == 2 else a; n = int(sr * win); k = len(m) // n
    return np.sqrt((m[:k * n].reshape(k, n) ** 2).mean(1) + 1e-12)

def norm_to(a, target_db, sr=48000):
    """scale a sound so its loudest 50 ms sits at target_db (dBFS RMS)."""
    return a * (10 ** (target_db / 20) / st_rms(a, sr).max())

# ---------------------------------------------------------------- platform safe zones (Reels / TikTok / Shorts, 1080x1920)
# measured on real TikTok / Instagram overlays: status bar + top tabs + IG camera icon reach ~y 250; TikTok's avatar /
# like column starts ~y 800 at x > 920; account name + caption + music start ~y 1600.
SAFE = dict(top=260, bottom=1440, left=60, right=910, right_from_y=700)

def safe_guides(a=90):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.rectangle((0, SAFE["bottom"], W, H), fill=(255, 0, 0, a))
    d.rectangle((SAFE["right"], SAFE["right_from_y"], W, SAFE["bottom"]), fill=(255, 0, 0, a))
    d.rectangle((0, 0, W, SAFE["top"]), fill=(255, 140, 0, a // 2))
    return g

def check_safe(els):
    bad = []
    for e in els:
        if e.bg or e.z < 0: continue
        bb = e.s.split()[3].point(lambda v: 255 if v > 60 else 0).getbbox()
        if not bb: continue
        ox, oy = e.cx - e.s.width / 2, e.cy - e.s.height / 2
        x0, y0, x1, y1 = ox + bb[0], oy + bb[1], ox + bb[2], oy + bb[3]
        why = [w for w, c in (("bottom", y1 > SAFE["bottom"]), ("left", x0 < SAFE["left"]), ("top", y0 < SAFE["top"]),
                              ("right", x1 > SAFE["right"] and y1 > SAFE["right_from_y"])) if c]
        if why: bad.append((round(e.t0, 2), (round(x0), round(y0), round(x1), round(y1)), why))
    return bad
