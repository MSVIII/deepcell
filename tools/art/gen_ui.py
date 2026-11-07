"""Deepcell: interface drawables, animations and dimens.

Run from the project folder: python tools/art/gen_ui.py
Needs Python 3 with Pillow (for the 9-patch PNGs).
Overwrites the files it generates in app/src/main/res.

Look: dark slate panels with cut corners and a thin cold border, chunky olive key-chip
buttons, round icon slots for the tabs. Matches the dark, lamp-lit Blender art.
"""
import os, sys
from PIL import Image, ImageDraw

R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main")
NS = 'xmlns:android="http://schemas.android.com/apk/res/android"'


def w(rel, text):
    p = os.path.join(R, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.strip() + "\n")


# ---------------------------------------------------------------- 9-patches
DENSITY = 3          # drawn for xxhdpi; Android scales for other screens
SS = 4               # supersampling for smooth diagonal edges


def rgba(h):
    h = h.lstrip("#")
    if len(h) == 6:
        h = "FF" + h
    a, r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    return (r, g, b, a)


def chamfer(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    return [(x0 + tl, y0), (x1 - tr, y0), (x1, y0 + tr), (x1, y1 - br), (x1 - br, y1),
            (x0 + bl, y1), (x0, y1 - bl), (x0, y0 + tl)]


def ninepatch(name, w_dp, h_dp, layers, stretch, pad):
    """layers: list of (polygon in dp, fill colour). stretch/pad: (left, top, right, bottom) in dp
    measured from each edge."""
    S = DENSITY * SS
    W, H = w_dp * DENSITY, h_dp * DENSITY
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    for poly, col in layers:
        d.polygon([(x * S, y * S) for x, y in poly], fill=rgba(col))
    img = big.resize((W, H), Image.LANCZOS)
    out = Image.new("RGBA", (W + 2, H + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    px = out.load()
    blk = (0, 0, 0, 255)
    sl, st, sr, sb = (int(v * DENSITY) for v in stretch)
    pl, pt, pr, pb = (int(v * DENSITY) for v in pad)
    for x in range(1 + sl, 1 + W - sr):
        px[x, 0] = blk
    for y in range(1 + st, 1 + H - sb):
        px[0, y] = blk
    for x in range(1 + pl, 1 + W - pr):
        px[x, H + 1] = blk
    for y in range(1 + pt, 1 + H - pb):
        px[W + 1, y] = blk
    p = os.path.join(R, "res", "drawable-xxhdpi", name + ".9.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    out.save(p)


def bordered(w_dp, h_dp, cut, border, edge, fill, inset_line=None):
    """Chamfered plate: outer edge colour, inner fill, optional thin inner highlight."""
    tl, tr, br, bl = cut
    outer = chamfer(0, 0, w_dp, h_dp, tl, tr, br, bl)
    b = border
    k = 0.41 * b  # keeps the border even along the 45 degree cuts
    inner = chamfer(b, b, w_dp - b, h_dp - b, max(0, tl - k), max(0, tr - k), max(0, br - k), max(0, bl - k))
    layers = [(outer, edge), (inner, fill)]
    if inset_line:
        layers.append((chamfer(b + tl * 0.6, b, w_dp - b - tr * 0.6, b + 1.2), inset_line))
    return layers


# Panels: cut top-left and bottom-right corners, cold thin border.
ninepatch("np_panel", 48, 48, bordered(48, 48, (10, 0, 10, 0), 1.5, "#B38FA3B0", "#F0161B21", "#228FA3B0"),
          (14, 14, 14, 14), (14, 12, 14, 12))
ninepatch("np_sheet", 48, 48, bordered(48, 48, (14, 14, 0, 0), 1.5, "#B38FA3B0", "#F5121619", "#228FA3B0"),
          (18, 18, 18, 8), (16, 10, 16, 6))
ninepatch("np_label", 24, 24, bordered(24, 24, (5, 0, 5, 0), 1, "#808FA3B0", "#D9101418"),
          (7, 7, 7, 7), (7, 3, 7, 3))
ninepatch("np_pill", 40, 32, bordered(40, 32, (8, 8, 8, 8), 1.5, "#B38FA3B0", "#E61A2026", "#228FA3B0"),
          (10, 10, 10, 10), (12, 4, 12, 4))
ninepatch("np_plaque", 24, 24, bordered(24, 24, (4, 4, 4, 4), 1.5, "#FF0B0C0D", "#FFC89238", "#55FFE0A0"),
          (7, 7, 7, 7), (5, 2, 5, 3))
ninepatch("np_field", 40, 40, bordered(40, 40, (8, 0, 8, 0), 1.5, "#998FA3B0", "#E60D1013"),
          (10, 10, 10, 10), (14, 10, 14, 10))


def frame_patch(name, size_dp=48, border=3.0, shadow=14.0):
    """Cell frame laid over each room and shaft segment: a solid black border and a soft inner
    shadow, so every cell reads as its own box. Transparent in the middle."""
    W = size_dp * DENSITY
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    px = img.load()
    b = border * DENSITY
    sh = shadow * DENSITY
    for y in range(W):
        for x in range(W):
            d = min(x, y, W - 1 - x, W - 1 - y)
            if d < b:
                a = 255
            elif d < b + sh:
                t = 1 - (d - b) / sh
                a = int(170 * t * t)
            else:
                a = 0
            px[x, y] = (0, 0, 0, a)
    out = Image.new("RGBA", (W + 2, W + 2), (0, 0, 0, 0))
    out.paste(img, (1, 1))
    o = out.load()
    edge = int((border + shadow + 2) * DENSITY)
    for i in range(1 + edge, 1 + W - edge):
        o[i, 0] = (0, 0, 0, 255)
        o[0, i] = (0, 0, 0, 255)
    for i in range(1, W + 1):          # content area: everything (no padding)
        o[i, W + 1] = (0, 0, 0, 255)
        o[W + 1, i] = (0, 0, 0, 255)
    p = os.path.join(R, "res", "drawable-xxhdpi", name + ".9.png")
    out.save(p)


frame_patch("np_cell_frame")


def chip(name, top, bottom, light, shade, pressed=False):
    """Key-chip button: dark outline, raised face with a light top lip and a shaded lower lip."""
    W, H = 48, 44
    o = 2.0
    lip = 1.5 if pressed else 4.0
    off = 2.5 if pressed else 0.0
    layers = [(chamfer(0, off, W, H, 6, 6, 6, 6), "#FF0C0D0B"),
              (chamfer(o, off + o, W - o, H - o, 5, 5, 5, 5), shade),
              (chamfer(o, off + o, W - o, H - o - lip, 5, 5, 5, 5), bottom),
              (chamfer(o, off + o, W - o, off + o + (H - off - 2 * o - lip) * 0.5, 5, 5, 0, 0), top),
              (chamfer(o + 4, off + o, W - o - 4, off + o + 1.3), light)]
    ninepatch(name, W, H, layers, (10, 12, 10, 12), (16, 9 + off, 16, 9 + lip))


chip("np_chip", "#FF66704F", "#FF555E42", "#FF8F9A6E", "#FF30352A")
chip("np_chip_pressed", "#FF4F5740", "#FF454C37", "#FF6B7556", "#FF30352A", pressed=True)
chip("np_chip_dark", "#FF39434C", "#FF2E363E", "#FF5A6875", "#FF1A1F24")
chip("np_chip_dark_pressed", "#FF2E363E", "#FF262D33", "#FF46525C", "#FF1A1F24", pressed=True)
chip("np_chip_danger", "#FF94402A", "#FF7E3522", "#FFC0644A", "#FF4A1E14")
chip("np_chip_danger_pressed", "#FF7E3522", "#FF6A2D1D", "#FF9A503A", "#FF4A1E14", pressed=True)
chip("np_chip_off", "#FF3A3C3A", "#FF333533", "#FF4A4C4A", "#FF222322")


def selector(name, normal, pressed, comment):
    w(f"res/drawable/{name}.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- {comment} -->
<selector {NS}>
    <item android:state_enabled="false" android:drawable="@drawable/np_chip_off" />
    <item android:state_pressed="true" android:drawable="@drawable/{pressed}" />
    <item android:drawable="@drawable/{normal}" />
</selector>''')


selector("bg_button", "np_chip", "np_chip_pressed", "Main button: olive key chip. Presses down when tapped.")
selector("bg_button_dark", "np_chip_dark", "np_chip_dark_pressed", "Secondary button: slate key chip.")
selector("bg_button_danger", "np_chip_danger", "np_chip_danger_pressed", "Destructive button: rust key chip.")

w("res/drawable/bg_hud.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Top bar: near-black with a faint cold line at the bottom. -->
<layer-list {NS}>
    <item><shape><solid android:color="#338FA3B0" /></shape></item>
    <item android:bottom="1dp">
        <shape><gradient android:angle="270" android:startColor="#FF0B0D10" android:endColor="#FF14181C" /></shape>
    </item>
</layer-list>''')

w("res/drawable/bg_tabbar.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list {NS}>
    <item><shape><solid android:color="#338FA3B0" /></shape></item>
    <item android:top="1dp">
        <shape><gradient android:angle="270" android:startColor="#FF14181C" android:endColor="#FF0B0D10" /></shape>
    </item>
</layer-list>''')

w("res/drawable/bg_tab.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Bottom tab: round dark slot; green ring when selected. -->
<selector {NS}>
    <item android:state_pressed="true">
        <shape android:shape="oval"><solid android:color="#FF232A31" /><stroke android:width="2dp" android:color="#FF8FA3B0" /></shape>
    </item>
    <item android:state_selected="true">
        <shape android:shape="oval"><solid android:color="#FF1C2A26" /><stroke android:width="3dp" android:color="@color/ring_on" /></shape>
    </item>
    <item>
        <shape android:shape="oval"><solid android:color="#FF161B20" /><stroke android:width="2dp" android:color="#FF3C4852" /></shape>
    </item>
</selector>''')

w("res/drawable/bg_icon_slot.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Round slot behind upgrade and survivor icons. -->
<shape {NS} android:shape="oval">
    <solid android:color="#FF0F1316" />
    <stroke android:width="2dp" android:color="#FF3C4852" />
</shape>''')

w("res/drawable/bg_bedrock.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Earth behind the room list (shows below the deepest room). -->
<shape {NS}><solid android:color="@color/earth" /></shape>''')

w("res/drawable/bg_vignette.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Darkens the edges of a scene so the centre reads as lit. -->
<shape {NS}>
    <gradient android:type="radial" android:gradientRadius="75%p" android:centerY="0.45"
        android:startColor="#00000000" android:centerColor="#00000000" android:endColor="#B3000000" />
</shape>''')

w("res/drawable/bg_room_shade.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Soft darkening at the top of each room so the labels read. -->
<shape {NS}>
    <gradient android:angle="270" android:startColor="#99000000" android:centerColor="#00000000" android:endColor="#00000000" />
</shape>''')


w("res/drawable/bg_title_shade.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Title screen: dark at the top behind the logo, fading out. -->
<shape {NS}>
    <gradient android:angle="270" android:startColor="#D9000000" android:centerColor="#80000000" android:endColor="#00000000" />
</shape>''')

w("res/drawable/bg_lamp_glow.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Warm lamp light over a room. Its alpha breathes (anim/lamp_flicker). -->
<shape {NS}>
    <gradient android:type="radial" android:centerX="0.5" android:centerY="0.1" android:gradientRadius="60%p"
        android:startColor="#30FFB060" android:endColor="#00FFB060" />
</shape>''')


def bar(name, color, back, radius="1dp"):
    w(f"res/drawable/{name}.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list {NS}>
    <item android:id="@android:id/background">
        <shape><corners android:radius="{radius}" /><solid android:color="{back}" /><stroke android:width="1dp" android:color="#998FA3B0" /></shape>
    </item>
    <item android:id="@android:id/progress" android:left="1dp" android:top="1dp" android:right="1dp" android:bottom="1dp">
        <clip><shape><corners android:radius="{radius}" /><solid android:color="{color}" /></shape></clip>
    </item>
</layer-list>''')


bar("progress_hatch", "@color/alarm_red", "#E60B0D10")
bar("progress_floor", "@color/amber", "#CC0B0D10")
bar("progress_level", "@color/ring_on", "#FF0B0D10")

# tween animations (survivors, enemies and effects use rendered frames instead)
w("res/anim/float_up.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!--
    "+5" payout text: pops in with a small overshoot, rises fast then slows (ease-out),
    and fades away faster and faster (ease-in).
-->
<set {NS} android:fillAfter="true">
    <scale android:duration="220" android:fromXScale="0.6" android:toXScale="1.0"
        android:fromYScale="0.6" android:toYScale="1.0" android:pivotX="50%" android:pivotY="50%"
        android:interpolator="@android:anim/overshoot_interpolator" />
    <translate android:duration="800" android:fromYDelta="0" android:toYDelta="-40dp"
        android:interpolator="@android:anim/decelerate_interpolator" />
    <alpha android:duration="450" android:startOffset="400" android:fromAlpha="1.0" android:toAlpha="0.0"
        android:interpolator="@android:anim/accelerate_interpolator" />
</set>''')
w("res/anim/sheet_in.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Upgrade sheet slides up: starts fast, settles gently (ease-out). -->
<translate {NS}
    android:duration="260"
    android:fromYDelta="100%"
    android:toYDelta="0"
    android:interpolator="@android:anim/decelerate_interpolator" />''')
w("res/anim/sheet_out.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Upgrade sheet drops away: starts slow, speeds up (ease-in). Shorter than coming in. -->
<translate {NS}
    android:duration="180"
    android:fromYDelta="0"
    android:toYDelta="100%"
    android:interpolator="@android:anim/accelerate_interpolator" />''')
w("res/anim/press_pop.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Button pressed: squashes a little and springs back past its size (overshoot). -->
<scale {NS}
    android:duration="260"
    android:fromXScale="0.85"
    android:toXScale="1.0"
    android:fromYScale="0.85"
    android:toYScale="1.0"
    android:pivotX="50%"
    android:pivotY="50%"
    android:interpolator="@android:anim/overshoot_interpolator" />''')
w("res/anim/hud_pop.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- HUD number changed: grows quickly and eases back (ease-out). -->
<scale {NS}
    android:duration="240"
    android:fromXScale="1.3"
    android:toXScale="1.0"
    android:fromYScale="1.3"
    android:toYScale="1.0"
    android:pivotX="0%"
    android:pivotY="50%"
    android:interpolator="@android:anim/decelerate_interpolator" />''')
w("res/drawable/fx_mote.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- A soft dust mote for the title screen: bright centre fading to nothing (tinted in code). -->
<shape {NS} android:shape="oval">
    <gradient
        android:type="radial"
        android:gradientRadius="50%"
        android:centerColor="#88FFFFFF"
        android:startColor="#FFFFFFFF"
        android:endColor="#00FFFFFF" />
</shape>''')
w("res/anim/stock_pulse.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Storage chip with something to collect: a slow breathing pulse (ease in and out). -->
<scale {NS}
    android:duration="700"
    android:fromXScale="1.0"
    android:toXScale="1.08"
    android:fromYScale="1.0"
    android:toYScale="1.08"
    android:pivotX="50%"
    android:pivotY="50%"
    android:repeatCount="infinite"
    android:repeatMode="reverse"
    android:interpolator="@android:anim/accelerate_decelerate_interpolator" />''')
w("res/anim/enemy_in.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Enemy appears: fades in and grows into place (ease-out). -->
<set {NS} android:interpolator="@android:anim/decelerate_interpolator">
    <alpha android:duration="300" android:fromAlpha="0.0" android:toAlpha="1.0" />
    <scale android:duration="300" android:fromXScale="0.6" android:toXScale="1.0"
        android:fromYScale="0.6" android:toYScale="1.0" android:pivotX="50%" android:pivotY="50%" />
</set>''')
w("res/anim/lamp_flicker.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Lamp glow over a room: a slow uneven breathe. -->
<alpha {NS}
    android:duration="2300"
    android:fromAlpha="1.0"
    android:toAlpha="0.55"
    android:interpolator="@android:anim/cycle_interpolator"
    android:repeatCount="infinite" />''')
w("res/values/dimens.xml", '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <dimen name="shaft_width">56dp</dimen>
    <dimen name="room_height">140dp</dimen>
    <dimen name="bunker_width">240dp</dimen>
    <dimen name="bunker_height">120dp</dimen>
</resources>''')
print("ui ok")
