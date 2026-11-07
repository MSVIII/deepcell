# Stylized interface icons (tabs, upgrades, settings, automation gear). Transparent, 3/4 view,
# outlined and rim lit like the rest of the art. Renders icon_*.png.
exec(open(BL_DIR + "/common.py").read())

WARM = (1.0, 0.55, 0.28)


def setup(name, ortho=1.5, tilt=60, yaw=0):
    new_scene("Icon_" + name)
    base_materials(bands=BANDS_NEUTRAL, rim=0.9)
    toon("DC_Brass", (0.78, 0.56, 0.22), (0.86, 0.64, 0.28), scale=6, bands=BANDS_NEUTRAL, rim=0.9, rim_col=WARM)
    toon("DC_Amber", (0.86, 0.56, 0.16), (0.92, 0.62, 0.20), scale=5, rust=0.2, bands=BANDS_NEUTRAL, rim=0.9, rim_col=WARM)
    sun("Key", (45, 0, 35), 3.4, (1.0, 0.95, 0.88))
    sun("Back", (60, 0, 200), 1.8, WARM)
    t = math.radians(tilt)
    cam = camera((0, -20 * math.sin(t), 20 * math.cos(t)), (tilt, 0, 0), ortho=ortho)
    if yaw:
        # orbit the camera around the icon instead of rotating every part
        r = 20 * math.sin(t)
        cam.location = (r * math.sin(math.radians(yaw)), -r * math.cos(math.radians(yaw)), 20 * math.cos(t))
        cam.rotation_euler = (t, 0, math.radians(yaw))


def gear(name, r, depth, mat, teeth=8, loc=(0, 0, 0), rot=(0, 0, 0)):
    cyl(name, r, depth, loc, mat, rot=rot, verts=32, bevel=0.03, outline=0.04)
    for k in range(teeth):
        a = 360 / teeth * k
        x = loc[0] + math.cos(math.radians(a)) * (r + 0.09)
        y = loc[1] + math.sin(math.radians(a)) * (r + 0.09)
        box(f"{name}T{k}", (0.2, 0.22, depth), (x, y, loc[2]), mat, rot=(0, 0, a), bevel=0.03, outline=0.04)
    cyl(name + "Hole", r * 0.35, depth + 0.02, loc, "DC_Dark", verts=20)


def out(name):
    render(f"icon_{name}.png", 160, 160, transparent=True)


# ---- tabs
setup("tab_defense", 1.45, tilt=85)
torus("Ring", 0.5, 0.07, (0, 0, 0), "DC_Steel", rot=(90, 0, 0), segs=40, outline=True)
for k, (dx, dz, w, h) in enumerate([(0, 0.48, 0.07, 0.35), (0, -0.48, 0.07, 0.35), (0.48, 0, 0.35, 0.07), (-0.48, 0, 0.35, 0.07)]):
    box(f"Tick{k}", (w, 0.08, h), (dx, 0, dz), "DC_Steel", bevel=0.02, outline=0.03)
ball("Dot", 0.11, (0, -0.05, 0), "DC_RedEye")
out("tab_defense")

setup("tab_supplies", 1.6, tilt=62, yaw=30)
box("Crate", (0.95, 0.95, 0.75), (0, 0, 0), "DC_Wood", bevel=0.05, outline=0.05)
for z in (-0.25, 0.25):
    box(f"Band{z}", (0.98, 0.98, 0.08), (0, 0, z), "DC_Steel")
box("Lid", (0.99, 0.99, 0.08), (0, 0, 0.38), "DC_Wood", bevel=0.02)
out("tab_supplies")

setup("tab_automation", 1.5, tilt=45)
gear("Gear", 0.42, 0.22, "DC_Amber", teeth=9)
out("tab_automation")

setup("tab_survivors", 1.7, tilt=72)
for k, (x, mat) in enumerate([(-0.33, "DC_Hazard"), (0.33, "DC_Olive")]):
    ball(f"Head{k}", 0.26, (x, 0, 0.0), "DC_Skin", outline=0.04)
    ball(f"Hat{k}", 0.3, (x, 0.02, 0.12), mat, scale=(1, 1, 0.7), outline=0.04)
    cyl(f"Brim{k}", 0.34, 0.04, (x, -0.02, 0.06), mat, verts=24)
    ball(f"Body{k}", 0.3, (x, 0.05, -0.45), mat, scale=(1, 0.8, 0.8), outline=0.04)
out("tab_survivors")

# ---- upgrades
setup("up_tap_power", 1.05, tilt=75, yaw=10)
cyl("Case", 0.18, 0.7, (0, 0, -0.1), "DC_Brass", verts=20, bevel=0.02, outline=0.04, rot=(0, 30, 0))
cyl("Tip", 0.18, 0.35, (0.26, 0, 0.35), "DC_Steel", r2=0.03, verts=20, outline=0.04, rot=(0, 30, 0))
cyl("Rim", 0.2, 0.06, (-0.18, 0, -0.42), "DC_Brass", verts=20, rot=(0, 30, 0))
out("up_tap_power")

setup("up_hatch_plating", 1.4, tilt=78, yaw=-20)
box("Plate", (0.95, 0.15, 1.0), (0, 0, 0), "DC_Steel", bevel=0.1, segs=3, outline=0.05)
box("Stripe", (0.97, 0.17, 0.14), (0, 0, -0.25), "DC_Hazard")
for x in (-0.35, 0.35):
    for z in (0.35, 0.05):
        ball(f"Rivet{x}{z}", 0.05, (x, -0.09, z), "DC_Dark")
out("up_hatch_plating")

setup("up_dig_tools", 1.5, tilt=82)
cyl("Handle", 0.05, 1.2, (0, 0, -0.05), "DC_Wood", rot=(0, 40, 0), outline=0.035)
box("Head", (0.95, 0.12, 0.14), (0.3, 0, 0.38), "DC_Steel", rot=(0, 40, 0), bevel=0.04, outline=0.04)
cyl("TipA", 0.07, 0.2, (0.72, 0, 0.0), "DC_Steel", r2=0.0, rot=(0, 220, 0))
out("up_dig_tools")

setup("up_farm_tools", 1.5, tilt=55)
cyl("Stem", 0.13, 0.4, (0, 0, -0.2), "DC_Mushroom", verts=14, outline=0.04)
ball("Cap", 0.42, (0, 0, 0.08), "DC_MushroomCap", scale=(1, 1, 0.6), outline=0.04)
for k, (x, y) in enumerate([(-0.18, -0.22), (0.15, -0.28), (0.02, -0.05)]):
    ball(f"Spot{k}", 0.06, (x, y, 0.3), "DC_Mushroom", scale=(1, 1, 0.4))
cyl("Drop", 0.08, 0.16, (0.42, -0.1, 0.45), "DC_Screen", r2=0.0, verts=12)
out("up_farm_tools")

setup("up_auto_turret", 1.6, tilt=58, yaw=-30)
cyl("Base", 0.42, 0.25, (0, 0, -0.35), "DC_Steel", verts=24, bevel=0.03, outline=0.04)
box("Head", (0.55, 0.55, 0.38), (0, 0, 0.0), "DC_Olive", bevel=0.06, outline=0.04)
box("HeadStripe", (0.57, 0.57, 0.07), (0, 0, -0.12), "DC_Hazard")
cyl("Barrel", 0.07, 0.8, (0, -0.55, 0.05), "DC_Dark", rot=(90, 0, 0), outline=0.03)
ball("Eye", 0.07, (0.15, -0.28, 0.08), "DC_RedEye")
out("up_auto_turret")

setup("up_drill_rig", 1.5, tilt=72, yaw=20)
cyl("Motor", 0.3, 0.4, (0, 0, 0.35), "DC_Olive", verts=20, bevel=0.04, outline=0.04)
box("MotorStripe", (0.62, 0.62, 0.08), (0, 0, 0.18), "DC_Hazard", rot=(0, 0, 45))
cyl("Bit", 0.26, 0.75, (0, 0, -0.28), "DC_Steel", r2=0.0, rot=(180, 0, 0), verts=10, outline=0.04)
for k in range(3):
    torus(f"Flute{k}", 0.2 - k * 0.06, 0.025, (0, 0, -0.1 - k * 0.18), "DC_Dark", rot=(12, 0, 0), segs=16)
out("up_drill_rig")

# ---- small interface icons
setup("settings", 1.5, tilt=45)
gear("Gear", 0.42, 0.22, "DC_Steel", teeth=8)
out("settings")

setup("gear", 1.5, tilt=45)
gear("Gear", 0.42, 0.22, "DC_Amber", teeth=8)
out("gear")

# ---- Collector: a full sack with a scrap nut and a mushroom poking out
setup("up_collector", 1.45, tilt=65)
ball("Sack", 0.42, (0, 0, -0.05), "DC_Cloth", scale=(1, 0.9, 1.05), outline=True)
cyl("SackNeck", 0.17, 0.22, (0, 0, 0.45), "DC_Cloth", r2=0.11, outline=True)
torus("Tie", 0.14, 0.04, (0, 0, 0.42), "DC_Brass")
cyl("Nut", 0.16, 0.08, (0.25, -0.28, 0.4), "DC_Steel", verts=6, rot=(60, 0, 20), bevel=0.02, outline=True)
cyl("NutHole", 0.06, 0.1, (0.25, -0.28, 0.4), "DC_Dark", verts=12, rot=(60, 0, 20))
ball("Shroom", 0.14, (-0.22, -0.26, 0.5), "DC_MushroomCap", scale=(1, 1, 0.6), outline=True)
out("up_collector")

# ---- Storage Racks: a banded crate with a nut and a mushroom on top
setup("up_storage", 1.5, tilt=60, yaw=30)
box("Crate", (0.8, 0.8, 0.62), (0, 0, -0.1), "DC_Wood", bevel=0.05, outline=True)
for z in (-0.32, 0.12):
    box(f"Band{z}", (0.82, 0.82, 0.08), (0, 0, z), "DC_Steel", bevel=0.01)
cyl("Nut", 0.16, 0.08, (-0.12, 0.05, 0.28), "DC_Steel", verts=6, bevel=0.02, outline=True)
cyl("NutHole", 0.06, 0.1, (-0.12, 0.05, 0.28), "DC_Dark", verts=12)
ball("Shroom", 0.13, (0.2, -0.1, 0.3), "DC_MushroomCap", scale=(1, 1, 0.6), outline=True)
out("up_storage")

# ---- Guard Training: a rifle with two brass rank chevrons
setup("up_guard_training", 1.5, tilt=78, yaw=-10)
box("Rifle", (1.15, 0.1, 0.12), (0.0, 0, 0.05), "DC_Dark", rot=(0, -30, 0), bevel=0.02, outline=0.035)
box("Stock", (0.32, 0.12, 0.2), (-0.5, 0, -0.24), "DC_Wood", rot=(0, -30, 0), bevel=0.03, outline=0.035)
for k, z in enumerate((-0.18, -0.42)):
    for s in (-1, 1):
        box(f"Chev{k}{s}", (0.36, 0.1, 0.1), (0.2 + s * 0.13, -0.15, z + 0.08), "DC_Brass",
            rot=(0, s * 35, 0), bevel=0.02, outline=0.03)
out("up_guard_training")

# ---- Work Shifts: a brass alarm clock
setup("up_work_shifts", 1.5, tilt=82)
cyl("Face", 0.42, 0.18, (0, 0, 0), "DC_Mushroom", rot=(90, 0, 0), verts=32, outline=0.04)
torus("Rim", 0.43, 0.06, (0, 0, 0), "DC_Brass", rot=(90, 0, 0), segs=32)
box("HandH", (0.06, 0.04, 0.24), (0, -0.11, 0.1), "DC_Dark")
box("HandM", (0.05, 0.04, 0.32), (0.11, -0.11, 0.02), "DC_Dark", rot=(0, 70, 0))
for x in (-0.3, 0.3):
    ball(f"Bell{x}", 0.14, (x, 0, 0.45), "DC_Brass", scale=(1, 1, 0.7), outline=0.03)
    cyl(f"Leg{x}", 0.04, 0.2, (x * 0.9, 0, -0.45), "DC_Brass", rot=(0, x * 60, 0))
out("up_work_shifts")

# ---- Sprinkler: a pipe head spraying glowing drops over a mushroom
setup("up_sprinkler", 1.55, tilt=62)
cyl("Pipe", 0.07, 0.7, (-0.25, 0, 0.05), "DC_Steel", verts=12, outline=0.03)
cyl("Head", 0.15, 0.12, (-0.25, 0, 0.42), "DC_Steel", verts=16, bevel=0.02, outline=0.03)
for k, (x, z) in enumerate([(0.0, 0.55), (0.18, 0.45), (0.32, 0.3), (0.42, 0.12)]):
    ball(f"Drop{k}", 0.05, (x, -0.05, z), "DC_Screen")
cyl("Stem", 0.09, 0.25, (0.3, 0, -0.35), "DC_Mushroom", verts=12, outline=0.03)
ball("Cap", 0.24, (0.3, 0, -0.18), "DC_MushroomCap", scale=(1, 1, 0.55), outline=0.035)
out("up_sprinkler")

# ---- Repair Arm: a wrench across a hazard-striped plate
setup("up_repair_arm", 1.5, tilt=78, yaw=15)
box("Plate", (0.8, 0.1, 0.8), (0, 0.1, 0), "DC_Steel", bevel=0.06, outline=0.04)
box("Stripe", (0.82, 0.12, 0.12), (0, 0.08, -0.25), "DC_Hazard")
box("Shaft", (0.14, 0.1, 0.95), (0, -0.08, 0), "DC_Brass", rot=(0, 40, 0), bevel=0.03, outline=0.035)
torus("Jaw", 0.15, 0.06, (0.33, -0.08, 0.38), "DC_Brass", rot=(90, 0, 0), segs=20)
torus("Ring", 0.12, 0.05, (-0.33, -0.08, -0.38), "DC_Brass", rot=(90, 0, 0), segs=20)
out("up_repair_arm")
