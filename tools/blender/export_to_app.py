"""Copy the Blender renders into the app as WebP files.

Run from the project folder after render_all.py:
    python tools/blender/export_to_app.py
Needs Python 3 with Pillow. Writes app/src/main/res/drawable-nodpi/*.webp.
"""
import os
from PIL import Image

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
}

os.makedirs(DST, exist_ok=True)
for name, size in SIZES.items():
    src = os.path.join(SRC, name + ".png")
    if not os.path.exists(src):
        print("missing", src)
        continue
    im = Image.open(src)
    im = im.resize(size, Image.LANCZOS)
    out = os.path.join(DST, name + ".webp")
    im.save(out, "WEBP", quality=88, method=6)
    print(f"{name}.webp {size[0]}x{size[1]} {os.path.getsize(out) // 1024} KB")
