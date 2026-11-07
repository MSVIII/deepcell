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
vec("ic_settings", 24, 24, [(BONE, gear(12, 12, 10, 7.6, 8, 3.2), "eo")], 24, 24, "Settings gear.")
vec("ic_gear", 24, 24, [(AMBER, gear(12, 12, 10, 7.6, 8, 3.2), "eo")], 24, 24, "Automated room marker (spins).")
vec("ic_tab_defense", 32, 32, [
    (RUST, "M16,2 L28,7 V16 C28,23 22.5,27.5 16,30 C9.5,27.5 4,23 4,16 V7 Z"),
    ("#FF8A3F1E", "M16,2 L28,7 V16 C28,23 22.5,27.5 16,30 Z"),
    (BONE, circle(16, 16, 6) + " " + circle(16, 16, 4.4), "eo"),
    (BONE, rect(15.2, 7, 1.6, 6) + " " + rect(15.2, 19, 1.6, 6) + " " + rect(7, 15.2, 6, 1.6) + " " + rect(19, 15.2, 6, 1.6)),
], 32, 32, "Defense tab.")
vec("ic_tab_supplies", 32, 32, [
    (WOOD, rect(4, 9, 24, 19)),
    (WOOD_D, rect(4, 9, 24, 2) + " " + rect(4, 17.5, 24, 2) + " " + rect(4, 26, 24, 2)),
    ("#FF8A6444", poly([(4, 9), (8, 4), (24, 4), (28, 9)])),
    (AMBER, rrect(13, 12, 6, 4, 1)),
], 32, 32, "Supplies tab (crate).")
vec("ic_tab_automation", 32, 32, [
    (STEEL, gear(14, 18, 11, 8.4, 8, 3.6), "eo"),
    (AMBER, poly([(22, 1), (15, 13), (20, 13), (17, 22), (27, 9), (21.5, 9), (25, 1)])),
], 32, 32, "Automation tab.")
vec("ic_tab_survivors", 32, 32, [
    (GREEN_D, "M2,29 C2,21 14,21 14,29 Z"),
    (SKIN, circle(8, 15, 4.5)),
    (GREEN, "M3.5,14 C3.5,8.5 12.5,8.5 12.5,14 Z"),
    ("#FF3E5A78", "M14,29 C14,19 30,19 30,29 Z"),
    (SKIN, circle(22, 12.5, 5.5)),
    (AMBER, "M16.2,11.5 C16.2,4.5 27.8,4.5 27.8,11.5 Z"),
    ("#FFFFF3B0", circle(22, 7.6, 1.5)),
], 32, 32, "Survivors tab.")
vec("ic_back", 24, 24, [(BONE, poly([(15, 3), (17.5, 5.5), (11, 12), (17.5, 18.5), (15, 21), (6, 12)]))], 24, 24, "Back arrow.")
vec("ic_close", 24, 24, [(BONE, poly([(5, 7), (7, 5), (12, 10), (17, 5), (19, 7), (14, 12), (19, 17), (17, 19), (12, 14), (7, 19), (5, 17), (10, 12)]))], 24, 24, "Close.")
vec("ic_skull", 24, 24, [
    (BONE, "M4,11 C4,5 8,2 12,2 C16,2 20,5 20,11 C20,14 18.5,15.5 17,16 V20 H7 V16 C5.5,15.5 4,14 4,11 Z"),
    (SOOT, circle(8.5, 11, 2.2) + " " + circle(15.5, 11, 2.2) + " " + poly([(12, 13), (13.4, 15.6), (10.6, 15.6)]) + " " + rect(9.4, 18, 1.2, 2) + " " + rect(13.4, 18, 1.2, 2)),
], 24, 24, "Boss wave marker.")

# ---------- upgrade icons (32x32) ----------
vec("ic_up_tap_power", 32, 32, [
    (AMBER, "M12,10 C12,4 16,1 16,1 C16,1 20,4 20,10 Z"),
    (AMBER_D, rect(12, 10, 8, 14)),
    ("#FFC48A2E", rect(12, 10, 3, 14)),
    (STEEL_D, rect(11, 24, 10, 4)),
    (RED, rect(11, 28, 10, 2)),
], 32, 32, "Sharpened Rounds.")
vec("ic_up_hatch_plating", 32, 32, [
    (STEEL_D, rrect(3, 5, 26, 22, 3)),
    (STEEL, rrect(5, 7, 22, 18, 2)),
    (STEEL_L, rect(5, 15.3, 22, 1.4)),
    (STEEL_D, " ".join(circle(x, y, 1.3) for x in (8, 24) for y in (10, 22))),
], 32, 32, "Hatch Plating.")
vec("ic_up_dig_tools", 32, 32, [
    (WOOD, poly([(22, 3), (25, 6), (14, 17), (11, 14)])),
    (STEEL, "M11,14 L14,17 L10,26 C8,28 4,28 3,27 C2,26 2,22 4,20 Z"),
    (STEEL_L, "M10,16 L12,18 L8.5,24 L6,22.5 Z"),
    (WOOD_D, rect(22, 1, 7, 3)),
], 32, 32, "Better Shovels.")
vec("ic_up_farm_tools", 32, 32, [
    (WOOD, rect(3, 22, 26, 7)),
    ("#FF2E2318", rect(4, 20, 24, 3)),
    (GREEN, "M9,20 C9,15 15,13 15,13 C15,13 15,19 9,20 Z M16,20 C16,13 24,11 24,11 C24,11 23,18 16,20 Z"),
    (GREEN_D, rect(15.4, 12, 1.2, 9)),
    (BONE, circle(8, 9, 1.5) + " " + circle(12, 5, 1.2) + " " + circle(20, 6, 1.4)),
], 32, 32, "Spore Trays.")
vec("ic_up_auto_turret", 32, 32, [
    (STEEL_D, poly([(6, 29), (10, 20), (22, 20), (26, 29)])),
    (STEEL, "M8,20 C8,13 24,13 24,20 Z"),
    (STEEL_L, poly([(18, 15), (29, 6), (30.5, 8), (20, 17.5)])),
    (RED, circle(16, 17.5, 1.6)),
    (AMBER, rect(6, 28, 20, 2)),
], 32, 32, "Auto-Turret.")
vec("ic_up_drill_rig", 32, 32, [
    (AMBER, rrect(8, 2, 16, 10, 2)),
    (SOOT, " ".join(poly([(9 + i * 4, 12), (12 + i * 4, 8), (14 + i * 4, 8), (11 + i * 4, 12)]) for i in range(3))),
    (STEEL, rect(14, 12, 4, 6)),
    (STEEL_L, poly([(10, 18), (22, 18), (16, 31)])),
    (STEEL_D, poly([(12, 21), (20, 21), (19, 23), (13, 23)]) + " " + poly([(13.5, 25), (18.5, 25), (17.7, 27), (14.3, 27)])),
], 32, 32, "Drill Rig.")

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
vec("ic_logo", 120, 120, logo_paths, 120, 120, "Deepcell emblem: a hatch wheel around a cell with a downward arrow.")

# launcher: legacy full icon (soot square) and adaptive foreground (safe zone ~ centre 66/108)
w("res/drawable/ic_launcher_foreground.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Adaptive icon foreground: the emblem scaled into the safe zone. -->
<vector {NS}
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <group android:scaleX="0.55" android:scaleY="0.55" android:translateX="21" android:translateY="21">
''' + "\n".join(
    f'        <path android:fillColor="{p[0]}"' + (' android:fillType="evenOdd"' if len(p) > 2 else "") + f' android:pathData="{p[1]}" />'
    for p in logo_paths) + '''
    </group>
</vector>''')
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
