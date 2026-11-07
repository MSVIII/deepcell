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

# ---------- survivor figures (viewport 20x32) ----------
def figure(name, helmet, helmet_d, body, body_d, lamp=True, rifle=False, note=""):
    p = [
        ("#FF2A2520", rect(4.5, 28.5, 5, 3.5) + " " + rect(10.5, 28.5, 5, 3.5)),
        (body_d, rect(6, 20, 3.6, 9) + " " + rect(10.4, 20, 3.6, 9)),
        (body, rrect(5, 12, 10, 9.5, 2)),
        (body_d, rect(5, 17, 10, 1.4)),
        (SKIN, rrect(2.6, 13, 2.4, 7, 1.2) + " " + rrect(15, 13, 2.4, 7, 1.2)),
        (SKIN, circle(10, 8.3, 4)),
        ("#FF15130F", rect(6.6, 7.6, 6.8, 1.6)),
        ("#FF9FD3E0", rect(7.2, 7.9, 2.2, 1) + " " + rect(10.6, 7.9, 2.2, 1)),
        (helmet, "M5.6,7 C5.6,2.2 14.4,2.2 14.4,7 Z"),
        (helmet_d, rect(4.4, 6.4, 11.2, 1.4)),
    ]
    if lamp:
        p.append(("#FFFFF3B0", circle(10, 4.4, 1.3)))
    if rifle:
        p.append(("#FF2A2520", poly([(14.5, 18), (19.5, 4), (20, 4.3), (16, 18.6)])))
    vec(name, 20, 32, p, 20, 32, note)

figure("ic_survivor_digger", AMBER, AMBER_D, "#FF3E5A78", "#FF2E4560", note="Survivor working in Scrap Dig.")
figure("ic_survivor_farmer", GREEN_D, "#FF44591F", WOOD, WOOD_D, lamp=False, note="Survivor working in Mushroom Farm.")
figure("ic_survivor_guard", STEEL, STEEL_D, "#FF8A3B2A", "#FF6A2C20", lamp=False, rifle=True, note="Survivor on roof guard duty.")

# ---------- surface bunker (200x100) ----------
bags = []
for (x0, x1) in ((2, 46), (154, 198)):
    for row, y in enumerate((90, 82, 74)):
        inset = row * 5
        xs = x0 + inset
        while xs + 12 <= x1 - inset:
            bags.append(rrect(xs, y, 12, 8, 3.5))
            xs += 12
stripes = " ".join(poly([(72 + i * 8, 96), (76 + i * 8, 92), (80 + i * 8, 92), (76 + i * 8, 96)]) for i in range(7))
rivets = " ".join(circle(x, 50, 1) for x in range(52, 150, 12))
vec("ic_bunker", 200, 100, [
    ("#FF7A6A4E", " ".join(bags)),
    (CONCRETE_D, "M28,96 L40,46 Q100,30 160,46 L172,96 Z"),
    (CONCRETE, "M33,96 L44,48 Q100,34 156,48 L167,96 Z"),
    ("#FF7C776E", "M44,48 Q100,34 156,48 L154,54 Q100,41 46,54 Z"),
    (CONCRETE_D, "M38,96 L41,80 L159,80 L162,96 Z"),
    (STEEL_D, rivets),
    (SOOT, rect(52, 60, 20, 4) + " " + rect(128, 60, 20, 4)),
    (AMBER, circle(49, 70, 4.2) + " " + circle(49, 70, 1.8) + " " + rect(51.4, 70, 1.8, 8), "eo"),
    (RUST, "M76,96 L76,68 Q100,54 124,68 L124,96 Z"),
    ("#FF34322E", "M80,96 L80,70 Q100,59 120,70 L120,96 Z"),
    (STEEL_D, rect(80, 75, 40, 1.5) + " " + rect(80, 86, 40, 1.5)),
    (AMBER, circle(100, 80, 8.5) + " " + circle(100, 80, 6.5), "eo"),
    (AMBER, rect(99, 72, 2, 16) + " " + rect(92, 79, 16, 2)),
    (AMBER, stripes),
    (WOOD_D, rect(62, 40, 76, 6)),
    (WOOD, rect(62, 39, 76, 2)),
    (STEEL_D, " ".join(rect(x, 30, 1.6, 10) for x in (63, 82, 100, 118, 136)) + " " + rect(63, 30, 75, 1.4)),
    (STEEL_D, "M150,46 L152.5,10 L155,46 Z"),
    (STEEL, rect(147, 18, 11, 1.4) + " " + rect(148.5, 24, 8, 1.2)),
    (RED, circle(152.5, 9, 2.4)),
], 220, 110, "Bunker Nine on the surface. Roof survivors stand on the deck at y=40.")

# ---------- skyline (360x70) ----------
random.seed(9)
def skyline(seed, base, hmin, hmax, wmin, wmax):
    random.seed(seed)
    pts = [(0, 70), (0, base)]
    x = 0
    while x < 360:
        bw = random.randint(wmin, wmax)
        h = random.randint(hmin, hmax)
        top = base - h
        pts.append((x, top))
        if random.random() < 0.5:  # broken top
            pts.append((x + bw * 0.4, top - random.randint(2, 6)))
            pts.append((x + bw * 0.6, top + random.randint(3, 8)))
        pts.append((min(x + bw, 360), top))
        x += bw
        gap = random.randint(0, 6)
        if gap and x < 360:
            pts.append((x, base))
            pts.append((min(x + gap, 360), base))
            x += gap
    pts.append((360, base))
    pts.append((360, 70))
    return poly(pts)
vec("bg_skyline", 360, 70, [
    ("#FF4A3430", skyline(3, 62, 14, 40, 10, 24)),
    ("#FF2E2220", skyline(7, 70, 6, 24, 14, 30)),
], 360, 70, "Ruined city on the horizon.")

vec("bg_ground_edge", 360, 20, [
    ("#FF3A3024", "M0,6 Q30,1 60,5 T120,4 T180,6 T240,3 T300,5 T360,4 L360,20 L0,20 Z"),
    ("#FF4E4030", "M0,6 Q30,1 60,5 T120,4 T180,6 T240,3 T300,5 T360,4 L360,7 Q330,6 300,8 T240,6 T180,9 T120,7 T60,8 T0,9 Z"),
], 360, 20, "Dirt edge where the surface meets the bunker.")

# ---------- rooms ----------
vec("room_dig_wall", 300, 110, [
    ("#FF3B2F25", rect(0, 0, 300, 110)),
    ("#FF33281F", "M0,30 Q75,22 150,32 T300,28 L300,44 Q225,50 150,42 T0,46 Z"),
    ("#FF46382B", "M0,62 Q80,56 160,66 T300,60 L300,70 Q220,76 150,70 T0,74 Z"),
    ("#FF2E251D", " ".join(ellipse(x, y, rx, ry) for x, y, rx, ry in
                           ((40, 52, 6, 3), (120, 20, 5, 2.5), (210, 50, 7, 3), (262, 84, 5, 2.5), (90, 86, 6, 3)))),
    ("#FF2A221B", rect(0, 100, 300, 10)),
    (WOOD_D, rect(0, 0, 300, 7)),
    (WOOD, rect(6, 0, 7, 100) + " " + rect(287, 0, 7, 100)),
    (WOOD_D, rect(6, 0, 2, 100) + " " + rect(287, 0, 2, 100)),
    ("#FF2A2520", rect(149.5, 7, 1, 12)),
    ("#22E3A23B", circle(150, 24, 18)),
    (AMBER, circle(150, 22, 3.5)),
], 300, 110, "Scrap Dig room wall. Stretched to fit the row.")

vec("room_farm_wall", 300, 110, [
    ("#FF46423A", rect(0, 0, 300, 110)),
    ("#FF3A372F", " ".join(rect(x, 0, 1.5, 100) for x in (60, 120, 180, 240)) + " " + rect(0, 52, 300, 1.2)),
    (CONCRETE, rect(0, 6, 300, 5)),
    (STEEL_D, " ".join(rect(x, 4, 4, 9) for x in (30, 110, 190, 270))),
    ("#14FFF3B0", "M66,20 L124,20 L146,96 L44,96 Z M176,20 L234,20 L256,96 L154,96 Z"),
    ("#FFE3D07A", rect(66, 16, 58, 4) + " " + rect(176, 16, 58, 4)),
    ("#FF2A2620", rect(0, 100, 300, 10)),
], 300, 110, "Mushroom Farm room wall. Stretched to fit the row.")

# scrap heap prop 96x64
vec("prop_scrap_heap", 96, 64, [
    (CONCRETE_D, "M2,64 Q16,30 46,22 Q78,28 94,64 Z"),
    (STEEL, "M20,40 L44,30 L50,36 L26,46 Z"),
    (RUST, "M52,30 h18 v6 h-18 Z M60,44 L80,40 L82,48 L62,52 Z"),
    ("#FF2A2520", circle(32, 54, 8) + " " + circle(32, 54, 3.5), "eo"),
    (RUST, rrect(62, 14, 14, 20, 2)),
    ("#FF8A3F1E", rect(62, 19, 14, 2) + " " + rect(62, 27, 14, 2)),
    (AMBER, rect(40, 46, 10, 3)),
], 96, 64, "Pile of scrap in Scrap Dig.")

# mushroom beds 200x50
random.seed(4)
caps, stems = [], []
x = 8
while x < 192:
    r = random.uniform(5, 9)
    caps.append(f"M{f(x - r)},{f(31)} a{f(r)},{f(r * 0.85)} 0 0,1 {f(2 * r)},0 Z")
    stems.append(rect(x - r * 0.25, 31, r * 0.5, 4))
    x += r * 2 + random.uniform(4, 10)
vec("prop_mushroom_beds", 200, 50, [
    (BONE, " ".join(stems)),
    (GREEN, " ".join(caps)),
    ("#FF2E2318", rect(2, 34, 196, 5)),
    (WOOD, rect(0, 38, 200, 12)),
    (WOOD_D, rect(0, 38, 200, 2) + " " + " ".join(rect(x, 38, 2, 12) for x in (48, 98, 148))),
], 200, 50, "Mushroom trays in Mushroom Farm.")

# drill rig prop 60x80
vec("prop_drill_rig", 60, 80, [
    (STEEL_D, poly([(10, 80), (22, 6), (26, 6), (16, 80)]) + " " + poly([(50, 80), (38, 6), (34, 6), (44, 80)])),
    (STEEL_D, rect(14, 30, 32, 2) + " " + rect(12, 52, 36, 2)),
    (AMBER, rrect(18, 10, 24, 18, 3)),
    (SOOT, " ".join(poly([(20 + i * 6, 28), (24 + i * 6, 22), (27 + i * 6, 22), (23 + i * 6, 28)]) for i in range(4))),
    (STEEL, rect(28, 28, 4, 30)),
    (STEEL_L, poly([(24, 58), (36, 58), (30, 74)])),
    ("#FF2A2520", rect(4, 76, 52, 4)),
], 60, 80, "Drill Rig machine, shown in Scrap Dig once bought.")

# ---------- enemies ----------
vec("ic_scout", 48, 48, [
    ("#55B8B4AA", ellipse(9, 13, 8, 3) + " " + ellipse(39, 13, 8, 3) + " " + ellipse(9, 35, 8, 3) + " " + ellipse(39, 35, 8, 3)),
    (STEEL_D, poly([(10, 14), (14, 12), (24, 22), (20, 26)]) + " " + poly([(38, 14), (34, 12), (24, 22), (28, 26)]) +
     " " + poly([(10, 34), (14, 36), (24, 26), (20, 22)]) + " " + poly([(38, 34), (34, 36), (24, 26), (28, 22)])),
    (STEEL, poly([(24, 13), (32, 18), (32, 30), (24, 35), (16, 30), (16, 18)])),
    (STEEL_L, poly([(24, 13), (32, 18), (24, 22), (16, 18)])),
    ("#55D23C2F", circle(24, 26, 5)),
    (RED, circle(24, 26, 2.6)),
    (STEEL_D, rect(23.4, 6, 1.2, 8)),
    (RED, circle(24, 6, 1.4)),
], 48, 48, "Scout drone.")
vec("ic_shrike", 48, 48, [
    ("#FF4A3328", "M24,26 C16,18 8,16 2,18 L8,21 L4,24 L11,24 L8,28 L17,27 Z M24,26 C32,18 40,16 46,18 L40,21 L44,24 L37,24 L40,28 L31,27 Z"),
    ("#FF5E4234", "M18,22 C18,15 30,15 30,22 L30,32 C30,38 18,38 18,32 Z"),
    ("#FF3A271E", "M20,36 L24,44 L28,36 Z"),
    (AMBER, poly([(22, 22), (26, 22), (24, 29)])),
    ("#FFB8F060", circle(21, 19, 1.5) + " " + circle(27, 19, 1.5) + " " + circle(24, 16.5, 1.1)),
], 48, 48, "Shrike, a mutated bird.")
vec("ic_bomber", 48, 48, [
    ("#55B8B4AA", ellipse(10, 9, 9, 2.5) + " " + ellipse(38, 9, 9, 2.5)),
    (STEEL_D, rect(9, 9, 2, 6) + " " + rect(37, 9, 2, 6)),
    (STEEL, rrect(4, 14, 40, 14, 5)),
    (STEEL_D, rect(4, 22, 40, 2)),
    (AMBER, " ".join(poly([(14 + i * 5, 28), (17 + i * 5, 24), (19.5 + i * 5, 24), (16.5 + i * 5, 28)]) for i in range(4))),
    (RED, circle(10, 18.5, 1.6) + " " + circle(38, 18.5, 1.6)),
    ("#FF2A2520", circle(24, 37, 6) + " " + poly([(20, 31), (28, 31), (26, 28), (22, 28)])),
    (RUST, rect(23, 41, 2, 2)),
], 48, 48, "Bomber drone carrying a bomb.")
vec("ic_boss", 80, 80, [
    (STEEL_D, poly([(14, 52), (6, 72), (12, 72), (22, 54)]) + " " + poly([(66, 52), (74, 72), (68, 72), (58, 54)]) + " " + rect(38, 56, 4, 20)),
    ("#FF3A3024", ellipse(40, 40, 36, 18)),
    (CONCRETE, ellipse(40, 37, 33, 14)),
    (STEEL, " ".join(poly(p) for p in (
        [(12, 34), (26, 26), (30, 32), (16, 40)], [(68, 34), (54, 26), (50, 32), (64, 40)]))),
    (SOOT, circle(40, 38, 10)),
    ("#66D23C2F", circle(40, 38, 8)),
    (RED, circle(40, 38, 4.5)),
    ("#FFFFB0A0", circle(38.5, 36.5, 1.4)),
    (AMBER, poly([(30, 22), (32, 12), (34, 22)]) + " " + poly([(38, 20), (40, 8), (42, 20)]) + " " + poly([(46, 22), (48, 12), (50, 22)])),
], 80, 80, "Boss: the command drone of the old air-defense network.")

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
