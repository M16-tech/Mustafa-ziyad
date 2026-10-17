# example_reel.py — a complete, working timeline to copy for a new reel. Every time below comes from words.txt.
# Topic of this example: "3 tips to save money" (Arabic captions, creator style). Replace scenes, captions, CUTS.
#   python edit_<name>.py stills 2.0 5.5 ...      → stills.png (red = platform UI zones) — check before rendering
#   python edit_<name>.py render                  → final mp4
#   python edit_<name>.py capcut                  → final mp4 + editable CapCut project   (CapCut must be closed)
#   python edit_<name>.py premiere                → final mp4 + Premiere layers + XML
import sys, os
SKILL = os.environ.get("REEL_EDITOR_SKILL") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL, "scripts"))
from reelkit import *                    # mclib (theme, cards, icons, El…) + Reel

WORK = os.path.dirname(os.path.abspath(__file__))           # the work dir: src.mov, words.txt, mattes/
NAME = "my_reel"                                            # output names
OUT_DIR = HOME + "/Desktop"
# set_theme("creator")                  # uncomment to override the user's saved style for this one video

CUTS = [6.10, 12.40]                    # from cuts.txt / from_capcut.py
R = Reel(os.path.join(WORK, "src.mov"), f"{OUT_DIR}/{NAME}_final.mp4", CUTS,
         music=None,                    # e.g. CONFIG.get("music_dir") + "/track.mp3" — always pick by measuring + tell the user
         mattes=os.path.join(WORK, "mattes"))
add, sfx = R.add, R.sfx
T = R.total
CX = 500 if RTL else 580                # content centre (keeps clear of the like/comment column on the right)
ZY = 1100                               # graphics zone centre for a standing / mid shot (use ~400 when the free space is ABOVE the head)

# ---- hook (0–6 s): question + big number --------------------------------------------------------------------------
add(El(accent_text("تصرف راتبك قبل نص الشهر؟", 70), CX, ZY - 150, 0.20, 5.95, din=0.4), "click")
def pct_card(v):                                            # a counter: the card keeps a fixed width while the number moves
    img, p = panel(620, 150, r=38)
    n = text_sprite(f"{v}%", 96, grad=(ACCENT_L, ACCENT_D)); l = text_sprite("من الناس", 46)
    img.alpha_composite(n, (p + 620 - 40 - n.ink[1], p + (150 - n.height) // 2))
    img.alpha_composite(l, (p + 620 - 80 - (n.ink[1] - n.ink[0]) - l.ink[1], p + (150 - l.height) // 2 + 6))
    return img
def pct_at(t):                                              # → (key, make_sprite); the key tells exporters when it changed
    v = int(70 * e_inout(clamp((t - 2.1) / 1.0)))
    return v, (lambda: pct_card(v))
add(DynEl(pct_at, CX, ZY + 40, 1.90, 5.95), "click")
sfx(2.1, "readout")

# ---- three tips (6–12 s): row of tiles, one per word ----------------------------------------------------------------
add(El(pill("٣ نصايح", 50), CX, ZY - 170, 6.30, 12.30), "click")
for (lab, ic, t0, x) in (("ميزانية", "chart", 7.0, CX + 250), ("ادخار", "wallet", 8.2, CX), ("بلا ديون", "shield", 9.4, CX - 250)):
    add(El(tile(lab, ic), x if RTL else 2 * CX - x, ZY, t0, 12.30), "click")

# ---- numbered card + strike-through (12– s) -------------------------------------------------------------------------
c = card(860, 120, "المشتريات العشوائية", 52, ic="cart", border=RED, ic_bg=RED, ic_fg=WHITE)
add(El(c, CX, ZY - 60, 12.60, 16.0), "swish")
x0, x1, yc = c.tb; ox = CX - c.width / 2
add(El(bar(int(x1 - x0) + 36, 9, RED), ox + (x0 + x1) / 2, ZY - 58, 13.40, 16.0, "wipe", din=0.28), "strike")
add(El(card2("القاعدة الذهبية", "ادخر ٢٠٪ أول ما يوصل الراتب", ic="#١", h=150, size=46), CX, ZY + 120, 14.0, 16.0, "wipe", din=0.5), "swish")

# ---- outro: name + tagline from config, the closing question, a call to action --------------------------------------
R.outro(16.4, question=("شنو أكثر شي يخلص راتبك؟", "اكتبلي بالتعليقات"), cta="تابعني للمزيد")

# ---- captions: the user's own spelling, 3–5 words each, timed from words.txt ------------------------------------
R.captions([(0.00, "تصرف راتبك قبل نص الشهر؟"), (2.10, "سبعين بالمية من الناس"), (4.00, "يعانون من نفس المشكلة"),
            (6.10, "عندي ثلاث نصايح"), (7.00, "سوي ميزانية"), (8.20, "ادخر من أول الشهر"), (9.40, "وابتعد عن الديون"),
            (12.40, "وانتبه للمشتريات العشوائية"), (14.00, "ادخر عشرين بالمية")], until=16.3)

R.finalize()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    exp = f"{OUT_DIR}/{NAME}_layers"
    if cmd == "stills": print(R.stills([float(x) for x in sys.argv[2:]], path=os.path.join(WORK, "stills.png")))
    elif cmd == "render": R.render()
    elif cmd in ("capcut", "premiere"):
        R.render(export_dir=exp, premiere=(cmd == "premiere"))
        if cmd == "capcut":
            from capcut import export_reel
            print("CapCut project:", export_reel(R, f"{NAME} editable", exp, register=True))
