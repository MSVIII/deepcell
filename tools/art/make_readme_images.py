"""Build the README images in docs/images/ from the Blender renders and emulator screenshots.

    python tools/art/make_readme_images.py [screenshot folder]

banner.png comes from tools/blender/out/ (surface.png, bunker.png, logo.png).
Screenshots (shot_*.png at 1080x2400) are scaled to 360x800 if a folder is given.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
OUT = os.path.join(ROOT, "tools", "blender", "out")
DST = os.path.join(ROOT, "docs", "images")
os.makedirs(DST, exist_ok=True)

# ---- banner: the bunker at dusk, darkened on the left, logo and one line of facts on top
W, H = 1280, 420
bg = Image.open(os.path.join(OUT, "surface.png")).convert("RGB")      # dusk skyline
scale = W / bg.width
bg = bg.resize((W, int(bg.height * scale)), Image.LANCZOS)
top = int(bg.height * 0.22)            # skyline and sunset band
bg = bg.crop((0, top, W, top + H)).convert("RGBA")
bunker = Image.open(os.path.join(OUT, "bunker.png")).convert("RGBA")   # our bunker, right side
bw = 500
bunker = bunker.resize((bw, int(bunker.height * bw / bunker.width)), Image.LANCZOS)
bg.alpha_composite(bunker, (W - bw - 20, H - bunker.height + 10))
bg = bg.convert("RGB")
shade = Image.new("L", (W, H))
d = ImageDraw.Draw(shade)
for x in range(W):                                 # dark on the left where the logo sits
    d.line([(x, 0), (x, H)], fill=int(190 * max(0.0, 1 - x / (W * 0.55))))
bg = Image.composite(Image.new("RGB", (W, H), (10, 9, 8)), bg, shade)
banner = bg.convert("RGBA")

logo = Image.open(os.path.join(OUT, "logo.png")).convert("RGBA")
lw = 520
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
glow = logo.split()[3].filter(ImageFilter.GaussianBlur(14))
halo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
halo.putalpha(glow.point(lambda v: int(v * 0.7)))
lx, ly = 56, (H - logo.height) // 2
banner.alpha_composite(halo, (lx, ly + 6))
banner.alpha_composite(logo, (lx, ly))
banner.convert("RGB").save(os.path.join(DST, "banner.png"), optimize=True)
print("banner.png")

# ---- screenshots
if len(sys.argv) > 1:
    src = sys.argv[1]
    for name in sorted(os.listdir(src)):
        if name.startswith("shot_") and name.endswith(".png"):
            im = Image.open(os.path.join(src, name)).convert("RGB").resize((360, 800), Image.LANCZOS)
            im.save(os.path.join(DST, name[5:]), optimize=True)
            print(name[5:])
