"""Copy the Blender renders into the app as WebP files.

Run from the project folder after render_all.py:
    python tools/blender/export_to_app.py
Needs Python 3 with Pillow. Writes app/src/main/res/drawable-nodpi/*.webp.

Extra steps done here rather than in Blender:
- survivors get a soft contact shadow under their feet, so they stand on the floor;
- the title shots get the bunker laid over the surface shot, and a blurred copy each
  (the title screen crossfades through the blurred copies between shots).
"""
import os
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
    "enemy_scout": (192, 192),
    "enemy_shrike": (192, 192),
    "enemy_bomber": (192, 192),
    "enemy_boss": (288, 288),
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
    "logo": (900, 630),
    "emblem": (432, 432),
}
TITLE_SHOTS = ("surface", "dig", "farm")


def contact_shadow(im):
    """Soft dark ellipse under the feet (feet sit about 7% above the bottom of the frame)."""
    w, h = im.size
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    cy = h * 0.93
    d.ellipse((w * 0.14, cy - h * 0.035, w * 0.86, cy + h * 0.035), fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(w * 0.035))
    sh.alpha_composite(im)
    return sh


def save(im, name, size, quality=88):
    im = im.resize(size, Image.LANCZOS)
    out = os.path.join(DST, name + ".webp")
    im.save(out, "WEBP", quality=quality, method=6)
    print(f"{name}.webp {size[0]}x{size[1]} {os.path.getsize(out) // 1024} KB")


os.makedirs(DST, exist_ok=True)
for name, size in SIZES.items():
    src = os.path.join(SRC, name + ".png")
    if not os.path.exists(src):
        print("missing", src)
        continue
    im = Image.open(src)
    if name.startswith("survivor_"):
        im = contact_shadow(im.convert("RGBA"))
    save(im, name, size)

bunker = Image.open(os.path.join(SRC, "bunker.png")).convert("RGBA")
for shot in TITLE_SHOTS:
    src = os.path.join(SRC, f"title_{shot}.png")
    if not os.path.exists(src):
        print("missing", src)
        continue
    im = Image.open(src).convert("RGBA")
    if shot == "surface":
        bw = int(im.width * 0.95)
        b = bunker.resize((bw, bw // 2), Image.LANCZOS)
        im.alpha_composite(b, ((im.width - bw) // 2, im.height - bw // 2 - 20))
    im = im.convert("RGB")
    save(im, f"title_{shot}", (720, 1280), quality=82)
    blur = im.resize((360, 640), Image.LANCZOS).filter(ImageFilter.GaussianBlur(12))
    save(blur, f"title_{shot}_blur", (360, 640), quality=75)
