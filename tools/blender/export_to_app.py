"""Copy the Blender renders into the app as WebP files.

Run from the project folder after render_all.py:
    python tools/blender/export_to_app.py            # everything
    python tools/blender/export_to_app.py --frames   # only animation and effect frames
Needs Python 3 with Pillow. Writes app/src/main/res/drawable-{xxhdpi,xhdpi,hdpi}/*.webp.

Extra steps done here rather than in Blender:
- survivors get a soft contact shadow under their feet, so they stand on the floor;
- animation frames (anim_sprites.py, vfx.py) are exported and an AnimationDrawable list is
  written for each one to res/drawable/anim_*.xml / fx_*.xml; effects fade out on their last frames;
- the title shots (full screen size) get a blurred copy each (the title screen crossfades
  through the blurred copies between shots);
- icons get a sticker outline: a dark edge inside a thin warm-white rim, so they read on
  any background;
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "out")
DST = os.path.join(HERE, "..", "..", "app", "src", "main", "res", "drawable-nodpi")

# file -> (width, height) in the app. Sized for about 3.5x screens.
SIZES = {
    "room_dig": (1250, 500),
    "room_dig_auto": (1250, 500),
    "room_farm": (1250, 500),
    "shaft": (200, 500),
    "surface": (1260, 990),
    "bunker": (840, 420),
    "survivor_digger": (128, 192),
    "survivor_farmer": (128, 192),
    "survivor_guard": (128, 192),
    "icon_scrap": (96, 96),
    "icon_food": (96, 96),
    "icon_gear": (64, 64),
    "icon_settings": (112, 112),
    "icon_tab_defense": (128, 128),
    "icon_tab_supplies": (128, 128),
    "icon_tab_automation": (128, 128),
    "icon_tab_survivors": (128, 128),
    "icon_up_tap_power": (128, 128),
    "icon_up_hatch_plating": (128, 128),
    "icon_up_dig_tools": (128, 128),
    "icon_up_farm_tools": (128, 128),
    "icon_up_auto_turret": (128, 128),
    "icon_up_drill_rig": (128, 128),
    "icon_up_collector": (128, 128),
    "icon_up_storage": (128, 128),
    "logo": (900, 630),
    "emblem": (432, 432),
}
TITLE_SHOTS = ("surface", "dig", "farm")

# Frame sequences: render name -> (drawable name, frame size in the app, ms per frame,
# one-shot, alpha for the last frames). Frame counts come from the files in out/.
ANIMS = {
    "survivor_digger_work": ("anim_digger_work", (256, 192), [90, 90, 130, 80, 60, 150, 90, 100], False, ()),
    "survivor_farmer_work": ("anim_farmer_work", (256, 192), [140, 120, 130, 180, 120, 130, 140, 140], False, ()),
    "survivor_guard_idle": ("anim_guard_idle", (168, 168), [220] * 6, False, ()),
    "survivor_guard_fire": ("anim_guard_fire", (168, 168), [50, 70, 90], True, ()),
    "survivor_collector_walk": ("anim_collector_walk", (168, 168), [90] * 8, False, ()),
    "survivor_collector_grab": ("anim_collector_grab", (168, 168), [120] * 4, True, ()),
    "enemy_scout": ("anim_scout", (192, 192), [50] * 4, False, ()),
    "enemy_bomber": ("anim_bomber", (192, 192), [55] * 4, False, ()),
    "enemy_shrike": ("anim_shrike", (192, 192), [80] * 6, False, ()),
    "enemy_boss": ("anim_boss", (288, 288), [60] * 4, False, ()),
    "fx_explode": ("fx_explode", (224, 224), [55] * 8, True, (0.75, 0.4)),
    "fx_dust": ("fx_dust", (160, 160), [50] * 6, True, (0.7, 0.35)),
    "fx_spores": ("fx_spores", (160, 160), [70] * 6, True, (0.7, 0.35)),
    "fx_sparks": ("fx_sparks", (112, 112), [40] * 4, True, (0.5,)),
}
XML_DIR = os.path.join(HERE, "..", "..", "app", "src", "main", "res", "drawable")


def contact_shadow(im, half_w=0.36):
    """Soft dark ellipse under the feet (feet sit about 7% above the bottom of the frame).
    half_w is the ellipse half-width as a fraction of the frame width."""
    w, h = im.size
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    cy = h * 0.93
    d.ellipse((w * (0.5 - half_w), cy - h * 0.035, w * (0.5 + half_w), cy + h * 0.035), fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(w * 0.035))
    sh.alpha_composite(im)
    return sh


def sticker(im, dark=3, light=3):
    """Outline an icon: dark edge, then a thin warm-white rim outside it (sizes in source px)."""
    im = im.convert("RGBA")
    pad = dark + light + 2
    w, h = im.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(im, (pad, pad))
    a = canvas.split()[3].point(lambda v: 255 if v > 90 else 0)
    inner = a.filter(ImageFilter.MaxFilter(dark * 2 + 1))
    outer = inner.filter(ImageFilter.MaxFilter(light * 2 + 1))
    out = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    out.paste((236, 226, 206, 255), mask=outer.filter(ImageFilter.GaussianBlur(0.6)))
    out.paste((14, 12, 12, 255), mask=inner.filter(ImageFilter.GaussianBlur(0.6)))
    out.alpha_composite(canvas)
    return out.resize((w, h), Image.LANCZOS)


# Density buckets: the sizes above are for xxhdpi screens; smaller copies go to xhdpi and hdpi,
# so a low-resolution phone decodes (and keeps in memory) a quarter of the pixels instead of
# the full image. mdpi phones scale the hdpi copy.
BUCKETS = (("drawable-xxhdpi", 1.0), ("drawable-xhdpi", 2 / 3), ("drawable-hdpi", 0.5))
RES = os.path.join(HERE, "..", "..", "app", "src", "main", "res")


def save(im, name, size, quality=88):
    total = 0
    for folder, f in BUCKETS:
        w, h = max(1, round(size[0] * f)), max(1, round(size[1] * f))
        out_dir = os.path.join(RES, folder)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, name + ".webp")
        im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=quality, method=4)
        total += os.path.getsize(out)
    old = os.path.join(DST, name + ".webp")          # the old single copy in drawable-nodpi
    if os.path.exists(old):
        os.remove(old)
    print(f"{name}.webp {size[0]}x{size[1]} (+2 smaller) {total // 1024} KB")


FRAMES_ONLY = "--frames" in sys.argv
os.makedirs(DST, exist_ok=True)
for name, size in ({} if FRAMES_ONLY else SIZES).items():
    src = os.path.join(SRC, name + ".png")
    if not os.path.exists(src):
        print("missing", src)
        continue
    im = Image.open(src)
    if name.startswith("survivor_"):
        im = contact_shadow(im.convert("RGBA"))
    if name.startswith("icon_") and name != "icon_gear":
        im = sticker(im)
    save(im, name, size)

def fade(im, alpha):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * alpha))))


for src_name, (dname, size, durations, oneshot, tail) in ANIMS.items():
    n = len(durations)
    items = []
    for i in range(n):
        src = os.path.join(SRC, f"{src_name}_{i}.png")
        if not os.path.exists(src):
            print("missing", src)
            continue
        im = Image.open(src).convert("RGBA")
        if src_name.startswith("survivor_"):
            # Frames are wider than the figure: keep the shadow to the feet.
            im = contact_shadow(im, 0.13 if im.width > im.height else 0.17)
        k = i - (n - len(tail))
        if k >= 0:
            im = fade(im, tail[k])
        frame = f"{dname}_{i}"
        save(im, frame, size)
        items.append(f'    <item android:drawable="@drawable/{frame}" android:duration="{durations[i]}" />')
    xml = "\n".join([
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<!-- Generated by tools/blender/export_to_app.py from {src_name}_*.png. Do not edit. -->',
        '<animation-list xmlns:android="http://schemas.android.com/apk/res/android"',
        f'    android:oneshot="{str(oneshot).lower()}">',
        *items,
        '</animation-list>', ''])
    with open(os.path.join(XML_DIR, dname + ".xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print(f"{dname}.xml {n} frames {sum(durations)} ms")

TITLE_SIZE = (1080, 2340)        # the phone's own shape and width, so the shot is not upscaled
for shot in (() if FRAMES_ONLY else TITLE_SHOTS):
    src = os.path.join(SRC, f"title_{shot}.png")
    if not os.path.exists(src):
        print("missing", src)
        continue
    im = Image.open(src).convert("RGB")
    save(im, f"title_{shot}", TITLE_SIZE, quality=86)
    blur = im.resize((270, 585), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))
    save(blur, f"title_{shot}_blur", (270, 585), quality=70)
