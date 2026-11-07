"""Deepcell: generates the vector art in res/drawable.

Run from anywhere: python tools/art/gen_art.py
Overwrites the drawables it generates. Edit shapes here, then rerun and rebuild.
"""
import math, os, random, sys

R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main")
NS = 'xmlns:android="http://schemas.android.com/apk/res/android"'


def w(rel, text):
    p = os.path.join(R, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.strip() + "\n")


def vec(name, vw, vh, paths, dw=None, dh=None, note=""):
    dw = dw or vw
    dh = dh or vh
    lines = []
    for p in paths:
        color, d = p[0], p[1]
        extra = ' android:fillType="evenOdd"' if len(p) > 2 and p[2] == "eo" else ""
        lines.append(f'    <path android:fillColor="{color}"{extra} android:pathData="{d}" />')
    body = "\n".join(lines)
    w(f"res/drawable/{name}.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- {note} -->
<vector {NS}
    android:width="{dw}dp"
    android:height="{dh}dp"
    android:viewportWidth="{vw}"
    android:viewportHeight="{vh}">
{body}
</vector>''')


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def circle(cx, cy, r):
    return f"M{f(cx - r)},{f(cy)} a{f(r)},{f(r)} 0 1,0 {f(2 * r)},0 a{f(r)},{f(r)} 0 1,0 {f(-2 * r)},0 Z"


def ellipse(cx, cy, rx, ry):
    return f"M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0 Z"


def rect(x, y, w_, h):
    return f"M{f(x)},{f(y)} h{f(w_)} v{f(h)} h{f(-w_)} Z"


def rrect(x, y, w_, h, r):
    return (f"M{f(x + r)},{f(y)} h{f(w_ - 2 * r)} a{f(r)},{f(r)} 0 0,1 {f(r)},{f(r)} v{f(h - 2 * r)} "
            f"a{f(r)},{f(r)} 0 0,1 {f(-r)},{f(r)} h{f(-(w_ - 2 * r))} a{f(r)},{f(r)} 0 0,1 {f(-r)},{f(-r)} "
            f"v{f(-(h - 2 * r))} a{f(r)},{f(r)} 0 0,1 {f(r)},{f(-r)} Z")


def poly(pts):
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def gear(cx, cy, r_out, r_in, teeth, hole):
    pts = []
    n = teeth * 4
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        r = r_out if (i % 4) in (0, 1) else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(pts) + " " + circle(cx, cy, hole)


# ---------- palette ----------
SOOT = "#FF15130F"
STEEL = "#FF8C8A84"
STEEL_L = "#FFB8B4AA"
STEEL_D = "#FF5A5852"
CONCRETE = "#FF6E6A62"
CONCRETE_D = "#FF55524B"
RUST = "#FFB0552B"
AMBER = "#FFE3A23B"
AMBER_D = "#FF9A6A1E"
RED = "#FFD23C2F"
GREEN = "#FF8FB34A"
GREEN_D = "#FF5E7A2E"
BONE = "#FFEDE3D0"
WOOD = "#FF6B4A32"
WOOD_D = "#FF4A3324"
SKIN = "#FFE0B48A"

# ---------- resources ----------
hexo = [(12 + 10 * math.cos(math.radians(30 + 60 * i)), 12 + 10 * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
hexi = [(12 + 7.6 * math.cos(math.radians(30 + 60 * i)), 12 + 7.6 * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
vec("ic_scrap", 24, 24, [
    (STEEL_D, poly(hexo) + " " + circle(12, 12, 4), "eo"),
    (STEEL_L, poly(hexi) + " " + circle(12, 12, 4), "eo"),
    (STEEL_D, circle(12, 12, 4) + " " + circle(12, 12, 3), "eo"),
    ("#FFFFFFFF", poly([(7.5, 6.5), (11, 4.6), (11.6, 5.6), (8.2, 7.6)])),
], 24, 24, "Scrap resource icon (hex nut).")
vec("ic_food", 24, 24, [
    (GREEN_D, "M2,12.5 C2,6 7,2.5 12,2.5 C17,2.5 22,6 22,12.5 Z"),
    (GREEN, "M3,11.5 C3,6.5 7.5,3.5 12,3.5 C16.5,3.5 21,6.5 21,11.5 Z"),
    ("#FFC9E07A", circle(8, 7.5, 1.6) + " " + circle(14.5, 6, 1.2) + " " + circle(16.5, 9.5, 1)),
    (BONE, "M9,12 h6 l-0.8,8.5 h-4.4 Z"),
    ("#FFC9BFA8", "M9.6,18 h4.8 l-0.2,2.5 h-4.4 Z"),
], 24, 24, "Food resource icon (mushroom).")

# Survivors, the surface bunker, skyline, rooms, props and enemies are Blender renders now:
# see tools/blender/. They used to be generated here as vectors.

# ---------- UI icons ----------
# Tab, upgrade, settings and gear icons are Blender renders now (tools/blender/icons.py).
vec("ic_back", 24, 24, [(BONE, poly([(15, 3), (17.5, 5.5), (11, 12), (17.5, 18.5), (15, 21), (6, 12)]))], 24, 24, "Back arrow.")
vec("ic_close", 24, 24, [(BONE, poly([(5, 7), (7, 5), (12, 10), (17, 5), (19, 7), (14, 12), (19, 17), (17, 19), (12, 14), (7, 19), (5, 17), (10, 12)]))], 24, 24, "Close.")
vec("ic_skull", 24, 24, [
    (BONE, "M4,11 C4,5 8,2 12,2 C16,2 20,5 20,11 C20,14 18.5,15.5 17,16 V20 H7 V16 C5.5,15.5 4,14 4,11 Z"),
    (SOOT, circle(8.5, 11, 2.2) + " " + circle(15.5, 11, 2.2) + " " + poly([(12, 13), (13.4, 15.6), (10.6, 15.6)]) + " " + rect(9.4, 18, 1.2, 2) + " " + rect(13.4, 18, 1.2, 2)),
], 24, 24, "Boss wave marker.")

# ---------- upgrade icons (32x32) ----------

# ---------- logo / launcher / notification ----------
oct_pts = [(60 + 54 * math.cos(math.radians(22.5 + 45 * i)), 60 + 54 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
rv = " ".join(circle(60 + 46 * math.cos(math.radians(45 * i)), 60 + 46 * math.sin(math.radians(45 * i)), 2.4) for i in range(8))
hex_out = [(60 + 22 * math.cos(math.radians(90 + 60 * i)), 60 + 22 * math.sin(math.radians(90 + 60 * i))) for i in range(6)]
hex_in = [(60 + 16 * math.cos(math.radians(90 + 60 * i)), 60 + 16 * math.sin(math.radians(90 + 60 * i))) for i in range(6)]
CELL_RING = poly(hex_out) + " " + poly(hex_in)
CELL_ARROW = poly([(51, 52), (56, 52), (60, 57), (64, 52), (69, 52), (60, 67)]) + " " + rect(57.5, 44, 5, 9)
logo_paths = [
    (STEEL_D, poly(oct_pts)),
    (CONCRETE, poly([(60 + 50 * math.cos(math.radians(22.5 + 45 * i)), 60 + 50 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)])),
    (STEEL_L, rv),
    (AMBER, circle(60, 60, 38) + " " + circle(60, 60, 32), "eo"),
    ("#FF2A2722", circle(60, 60, 32)),
    (AMBER, CELL_RING, "eo"),
    (AMBER, CELL_ARROW),
]

# launcher: legacy full icon (soot square) and adaptive foreground (safe zone ~ centre 66/108)
w("res/drawable/ic_launcher_foreground.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Adaptive icon foreground: the rendered emblem (tools/blender/logo.py) inside the safe zone. -->
<inset {NS}
    android:drawable="@drawable/emblem"
    android:inset="19dp" />''')
w("res/drawable/ic_launcher.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Launcher icon for Android 7.x (Android 8+ uses drawable-v26/ic_launcher.xml). -->
<vector {NS}
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="120"
    android:viewportHeight="120">
    <path android:fillColor="{SOOT}" android:pathData="{rrect(0, 0, 120, 120, 18)}" />
''' + "\n".join(
    f'    <path android:fillColor="{p[0]}"' + (' android:fillType="evenOdd"' if len(p) > 2 else "") + f' android:pathData="{p[1]}" />'
    for p in logo_paths) + '''
</vector>''')
vec("ic_notify", 120, 120, [
    ("#FFFFFFFF", circle(60, 60, 54) + " " + circle(60, 60, 42), "eo"),
    ("#FFFFFFFF", CELL_RING, "eo"),
    ("#FFFFFFFF", CELL_ARROW),
], 24, 24, "Monochrome notification icon.")

random.seed(11)
stones = " ".join(ellipse(random.uniform(10, 290), random.uniform(10, 390), random.uniform(5, 14), random.uniform(3, 7)) for _ in range(26))
vec("bg_bedrock_footer", 300, 400, [
    ("#FF2A2119", rect(0, 0, 300, 400)),
    ("#FF241C15", "M0,60 Q75,48 150,62 T300,56 L300,90 Q220,100 150,88 T0,96 Z M0,210 Q90,196 170,214 T300,204 L300,236 Q210,248 140,232 T0,240 Z"),
    ("#FF322820", stones),
    ("#FF1E1813", "M0,330 Q80,318 160,336 T300,326 L300,400 L0,400 Z"),
], 300, 400, "Earth below the deepest room.")
print("art ok")
