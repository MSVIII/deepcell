# Small transparent sprites: survivors, enemies and the two resource icons.
# Every sprite gets its own fresh scene so nothing leaks between renders.
exec(open(BL_DIR + "/common.py").read())

WARM = (1.0, 0.55, 0.28)
COOL = (0.45, 0.6, 0.95)


def setup(name, ortho, cam_z=0.0, tilt=75, rim=0.6):
    new_scene("Sprite_" + name)
    base_materials(bands=BANDS_NEUTRAL, rim=rim)
    sun("Key", (55, 0, 30), 3.0, (1.0, 0.92, 0.82))
    sun("Back", (60, 0, 200), 2.0, WARM)
    d = 20
    t = math.radians(tilt)
    camera((0, -d * math.sin(t), cam_z + d * math.cos(t)), (tilt, 0, 0), ortho=ortho)


# ---------------------------------------------------------------- survivors

def survivor(name, vest, helmet, tool):
    setup(name, 1.85, cam_z=0.8, tilt=80)
    toon("DC_Vest", *vest, scale=8, grime=0.3, bands=BANDS_NEUTRAL, rim=0.6, rim_col=WARM)
    toon("DC_Helmet", *helmet, scale=6, grime=0.2, bands=BANDS_NEUTRAL, rim=0.6, rim_col=WARM)
    toon("DC_Pants", (0.20, 0.21, 0.18), (0.24, 0.25, 0.21), scale=8, bands=BANDS_NEUTRAL, rim=0.5, rim_col=WARM)
    for sx in (-0.13, 0.13):
        cyl(f"Leg{sx}", 0.1, 0.5, (sx, 0, 0.3), "DC_Pants", verts=10, outline=0.02)
        box(f"Boot{sx}", (0.18, 0.26, 0.12), (sx, -0.03, 0.06), "DC_Dark", bevel=0.04, outline=0.02)
    ball("Body", 0.3, (0, 0, 0.78), "DC_Vest", scale=(1.0, 0.75, 1.0), outline=0.025)
    box("Belt", (0.56, 0.42, 0.07), (0, 0, 0.58), "DC_Dark", bevel=0.02)
    box("Pack", (0.38, 0.2, 0.42), (0, 0.27, 0.82), "DC_Cloth", bevel=0.05, outline=0.02)
    for sx in (-1, 1):
        cyl(f"Arm{sx}", 0.075, 0.42, (sx * 0.33, -0.04, 0.72), "DC_Vest", rot=(0, sx * 12, 0), verts=10, outline=0.02)
        ball(f"Hand{sx}", 0.075, (sx * 0.37, -0.06, 0.5), "DC_Skin", outline=0.015)
    ball("Head", 0.24, (0, -0.02, 1.27), "DC_Skin", outline=0.025)
    for sx in (-0.08, 0.08):
        ball(f"Eye{sx}", 0.03, (sx, -0.24, 1.25), "DC_Dark")
    tool()
    render(f"survivor_{name}.png", 256, 384, transparent=True)


def hard_hat():
    ball("Hat", 0.27, (0, -0.02, 1.37), "DC_Helmet", scale=(1, 1, 0.65), outline=0.025)
    cyl("Brim", 0.32, 0.04, (0, -0.04, 1.33), "DC_Helmet", verts=20)
    cyl("HeadLamp", 0.06, 0.06, (0, -0.28, 1.42), "DC_Bulb", rot=(90, 0, 0), verts=12)


def pickaxe():
    cyl("PickHandle", 0.03, 0.9, (0.42, -0.1, 0.75), "DC_Wood", rot=(0, -20, 0), outline=0.015)
    box("PickHead", (0.5, 0.06, 0.07), (0.56, -0.1, 1.17), "DC_Steel", rot=(0, -20, 0), outline=0.015)


def cap():
    ball("Cap", 0.26, (0, 0.0, 1.35), "DC_Helmet", scale=(1, 1, 0.6), outline=0.025)
    box("CapBill", (0.3, 0.18, 0.03), (0, -0.22, 1.32), "DC_Helmet", rot=(-10, 0, 0))


def basket():
    cyl("Basket", 0.16, 0.18, (0.4, -0.12, 0.45), "DC_Wood", verts=12, outline=0.015)
    for k, dx in enumerate((-0.06, 0.05)):
        ball(f"Shroom{k}", 0.07, (0.4 + dx, -0.12, 0.56), "DC_MushroomCap", scale=(1, 1, 0.6))


def combat_helmet():
    ball("Helmet", 0.28, (0, 0.0, 1.35), "DC_Helmet", scale=(1, 1, 0.75), outline=0.025)
    box("Goggles", (0.34, 0.06, 0.08), (0, -0.24, 1.37), "DC_Dark")
    for sx in (-0.08, 0.08):
        cyl(f"Lens{sx}", 0.045, 0.02, (sx, -0.275, 1.37), "DC_Screen", rot=(90, 0, 0), verts=12)


def rifle():
    box("Rifle", (0.08, 0.7, 0.1), (0.3, -0.25, 0.72), "DC_Dark", rot=(30, 0, 0), outline=0.015)
    box("RifleStock", (0.08, 0.2, 0.14), (0.3, 0.05, 0.6), "DC_Wood", rot=(30, 0, 0))


# ---------------------------------------------------------------- enemies

def rotor(name, x, y, z, r):
    cyl(name + "Arm", 0.04, 0.1, (x, y, z), "DC_Dark")
    cyl(name, r, 0.02, (x, y, z + 0.06), "DC_Dark", verts=20)
    box(name + "Blade", (r * 2.1, 0.06, 0.015), (x, y, z + 0.08), "DC_Steel", rot=(0, 0, 30))


def scout():
    setup("scout", 1.75, cam_z=0.0, tilt=65)
    ball("Body", 0.42, (0, 0, 0), "DC_Steel", scale=(1, 1, 0.7), segs=20, rings=12, outline=0.03)
    box("Band", (0.9, 0.9, 0.08), (0, 0, 0), "DC_Hazard", rot=(0, 0, 45))
    ball("Eye", 0.13, (0, -0.37, -0.05), "DC_RedEye")
    for k in range(4):
        a = math.radians(45 + k * 90)
        x, y = math.cos(a) * 0.62, math.sin(a) * 0.62
        cyl(f"Strut{k}", 0.03, 0.42, (x / 2, y / 2, 0.1), "DC_Dark", rot=(0, 90, math.degrees(a)))
        rotor(f"Rotor{k}", x, y, 0.12, 0.26)
    cyl("Antenna", 0.012, 0.35, (0.15, 0.1, 0.42), "DC_Dark")
    render("enemy_scout.png", 256, 256, transparent=True)


def shrike():
    setup("shrike", 2.7, cam_z=0.0, tilt=42, rim=0.3)
    toon("DC_Feather", (0.20, 0.17, 0.20), (0.27, 0.22, 0.26), scale=10, bands=BANDS_NEUTRAL, rim=0.3, rim_col=WARM)
    toon("DC_Beak", (0.70, 0.60, 0.35), (0.78, 0.66, 0.40), scale=6, bands=BANDS_NEUTRAL, rim=0.4)
    ball("Body", 0.3, (0, 0, 0), "DC_Feather", scale=(0.8, 1.4, 0.8), outline=0.025)
    ball("Head", 0.2, (0, -0.42, 0.12), "DC_Feather", outline=0.02)
    cyl("Beak", 0.08, 0.28, (0, -0.68, 0.08), "DC_Beak", rot=(90, 0, 0), r2=0.0, verts=8)
    for sx in (-0.08, 0.08):
        ball(f"Eye{sx}", 0.045, (sx, -0.58, 0.18), "DC_RedEye")
    for sx in (-1, 1):
        w = box(f"Wing{sx}", (0.9, 0.45, 0.04), (sx * 0.62, 0.05, 0.12), "DC_Feather",
                rot=(0, sx * -18, sx * -10), outline=0.02)
        for k in range(3):
            box(f"Feather{sx}{k}", (0.32, 0.12, 0.03), (sx * (0.95 + k * 0.05), 0.12 + k * 0.12, 0.2),
                "DC_Feather", rot=(0, sx * -22, sx * (-25 - k * 12)), outline=0.015)
    box("Tail", (0.3, 0.4, 0.03), (0, 0.55, 0.0), "DC_Feather", rot=(-10, 0, 0), outline=0.015)
    render("enemy_shrike.png", 256, 256, transparent=True)


def bomber():
    setup("bomber", 2.2, cam_z=-0.1, tilt=65)
    cyl("Body", 0.42, 1.0, (0, 0, 0), "DC_Olive", rot=(0, 90, 0), verts=20, bevel=0.08, outline=0.03)
    box("Stripe", (0.12, 0.88, 0.88), (0, 0, 0), "DC_Hazard")
    ball("Eye", 0.11, (0.3, -0.4, 0.05), "DC_RedEye")
    ball("Bomb", 0.22, (0, 0, -0.55), "DC_Dark", scale=(1, 1, 1.25), outline=0.02)
    cyl("BombFin", 0.14, 0.12, (0, 0, -0.85), "DC_Red", verts=8)
    cyl("Hook", 0.03, 0.2, (0, 0, -0.32), "DC_Steel")
    for sx in (-1, 1):
        cyl(f"Boom{sx}", 0.04, 0.45, (sx * 0.72, 0, 0.12), "DC_Dark", rot=(0, 90, 0))
        rotor(f"Rotor{sx}", sx * 0.92, 0, 0.14, 0.34)
    render("enemy_bomber.png", 256, 256, transparent=True)


def boss():
    setup("boss", 3.1, cam_z=0.0, tilt=65)
    cyl("Hull", 0.95, 0.45, (0, 0, 0), "DC_Steel", verts=6, bevel=0.08, outline=0.04)
    cyl("Armor", 0.8, 0.2, (0, 0, 0.3), "DC_Olive", verts=6, bevel=0.05, outline=0.03)
    cyl("Dome", 0.45, 0.25, (0, 0, 0.5), "DC_Dark", verts=16, r2=0.3, outline=0.03)
    box("Stripe", (1.85, 0.12, 0.06), (0, -0.82, 0.05), "DC_Hazard")
    for k, dx in enumerate((-0.35, 0.0, 0.35)):
        ball(f"Eye{k}", 0.11 if k == 1 else 0.08, (dx, -0.8, -0.05), "DC_RedEye")
    for k in range(6):
        a = math.radians(30 + k * 60)
        x, y = math.cos(a) * 1.25, math.sin(a) * 1.25
        cyl(f"Strut{k}", 0.05, 0.4, (math.cos(a) * 1.0, math.sin(a) * 1.0, 0.1), "DC_Dark",
            rot=(0, 90, math.degrees(a)))
        rotor(f"Rotor{k}", x, y, 0.12, 0.32)
    for dx in (-0.3, 0.3):
        cyl(f"Gun{dx}", 0.05, 0.5, (dx, -0.75, -0.3), "DC_Dark", rot=(70, 0, 0))
    cyl("Antenna", 0.015, 0.6, (0.25, 0.2, 0.9), "DC_Dark")
    ball("AntennaTip", 0.04, (0.25, 0.2, 1.2), "DC_RedEye")
    render("enemy_boss.png", 384, 384, transparent=True)


# ---------------------------------------------------------------- resource icons

def icon_scrap():
    setup("scrap", 1.15, cam_z=0.0, tilt=50, rim=0.8)
    cyl("Nut", 0.5, 0.3, (0, 0, 0), "DC_Steel", verts=6, bevel=0.05, outline=0.04)
    cyl("Hole", 0.2, 0.32, (0, 0, 0), "DC_Dark", verts=16)
    render("icon_scrap.png", 128, 128, transparent=True)


def icon_food():
    setup("food", 1.1, cam_z=0.3, tilt=70, rim=0.8)
    cyl("Stem", 0.14, 0.45, (0, 0, 0.1), "DC_Mushroom", verts=12, outline=0.04)
    ball("Cap", 0.42, (0, 0, 0.4), "DC_MushroomCap", scale=(1, 1, 0.6), outline=0.04)
    for k, (x, y) in enumerate([(-0.18, -0.25), (0.15, -0.3), (0.0, -0.1)]):
        ball(f"Spot{k}", 0.06, (x, y, 0.58), "DC_Mushroom", scale=(1, 1, 0.4))
    render("icon_food.png", 128, 128, transparent=True)


ORANGE = ((0.70, 0.36, 0.12), (0.78, 0.42, 0.15))
YELLOW = ((0.80, 0.62, 0.15), (0.86, 0.68, 0.20))
GREEN = ((0.28, 0.40, 0.22), (0.33, 0.46, 0.26))
BROWN = ((0.40, 0.30, 0.18), (0.46, 0.35, 0.21))
OLIVE = ((0.30, 0.33, 0.20), (0.36, 0.39, 0.24))
def build_static():
    survivor("digger", ORANGE, YELLOW, lambda: (hard_hat(), pickaxe()))
    survivor("farmer", GREEN, BROWN, lambda: (cap(), basket()))
    survivor("guard", OLIVE, OLIVE, lambda: (combat_helmet(), rifle()))
    scout()
    shrike()
    bomber()
    boss()
    icon_scrap()
    icon_food()


# anim_sprites.py runs this file with SPRITES_DEFS_ONLY = True to reuse the builders.
if not globals().get("SPRITES_DEFS_ONLY"):
    build_static()
