# Our bunker on the surface. Renders bunker.png with a transparent background (2:1).
# The flat roof deck is where the Roof guards stand (roofCrew in activity_game.xml).
exec(open(BL_DIR + "/common.py").read())

sc = new_scene("Bunker")
base_materials(bands=BANDS_NEUTRAL, rim=0.5)
WARM = (1.0, 0.55, 0.28)
toon("DC_BunkerConcrete", (0.27, 0.27, 0.25), (0.34, 0.33, 0.30), scale=3, grime=0.8,
     bands=BANDS_NEUTRAL, rim=0.3, rim_col=WARM, grime_height=1.2)
toon("DC_Sandbag", (0.42, 0.37, 0.26), (0.50, 0.44, 0.31), scale=12, grime=0.4, bands=BANDS_NEUTRAL,
     rim=0.35, rim_col=WARM, grime_height=0.6)
toon("DC_Mound", (0.13, 0.10, 0.08), (0.17, 0.12, 0.09), scale=5, bands=BANDS_NEUTRAL)
emit("DC_Slit", (1.0, 0.62, 0.28), 4.0)
random.seed(3)

# earth mound the bunker is dug into
ball("Mound", 1.0, (0, 0.4, -0.35), "DC_Mound", scale=(4.4, 2.2, 0.7), segs=32, rings=16)
# main blockhouse
box("Block", (5.6, 3.0, 1.9), (0, 0, 0.95), "DC_BunkerConcrete", bevel=0.22, segs=3, outline=0.04)
box("Deck", (5.2, 2.6, 0.12), (0, 0, 1.96), "DC_Plate", bevel=0.03)
for i in range(4):
    box(f"DeckSeam{i}", (0.04, 2.6, 0.01), (-1.95 + i * 1.3, 0, 2.03), "DC_Dark")
# front: blast door with hazard frame, slit windows
box("DoorFrame", (1.5, 0.12, 1.45), (0, -1.52, 0.72), "DC_Hazard", bevel=0.03, outline=0.03)
box("Door", (1.2, 0.14, 1.25), (0, -1.55, 0.65), "DC_Olive", bevel=0.03)
for dz in (0.3, 0.65, 1.0):
    box(f"DoorRib{dz}", (1.1, 0.16, 0.05), (0, -1.56, dz), "DC_Steel")
torus("DoorWheel", 0.16, 0.035, (0.0, -1.66, 0.75), "DC_Red", rot=(90, 0, 0))
for sx in (-1.0, 1.0):
    box(f"Slit{sx}", (1.2, 0.08, 0.16), (sx * 1.8, -1.52, 1.25), "DC_Dark", bevel=0.02)
    box(f"SlitGlow{sx}", (1.05, 0.06, 0.07), (sx * 1.8, -1.53, 1.25), "DC_Slit")
    point(f"SlitLight{sx}", (sx * 1.8, -1.9, 1.25), 20, WARM)
# deck railing
for i in range(7):
    cyl(f"RailPost{i}", 0.035, 0.55, (-2.4 + i * 0.8, -1.2, 2.3), "DC_Steel")
cyl("Rail", 0.03, 4.9, (0, -1.2, 2.55), "DC_Steel", rot=(0, 90, 0), outline=0.015)
# hatch at the back of the deck (enemies dive at it)
cyl("HatchRing", 0.75, 0.22, (0, 0.6, 2.1), "DC_Steel", verts=28, bevel=0.04, outline=0.03)
cyl("Hatch", 0.62, 0.12, (0, 0.6, 2.25), "DC_Olive", verts=28, bevel=0.04)
torus("HatchWheel", 0.25, 0.04, (0, 0.6, 2.36), "DC_Red", rot=(0, 0, 0))
box("HatchStripe", (1.3, 0.1, 0.02), (0, 0.6, 2.32), "DC_Hazard")
# antenna and vent
cyl("Mast", 0.05, 1.9, (2.2, 0.9, 2.95), "DC_Steel", outline=0.015)
for z in (3.0, 3.5):
    box(f"MastBar{z}", (0.5, 0.03, 0.03), (2.2, 0.9, z), "DC_Steel")
ball("MastLight", 0.09, (2.2, 0.9, 3.95), "DC_RedEye")
cyl("Vent", 0.22, 1.1, (-2.0, 0.8, 2.6), "DC_Rust", outline=0.03)
cyl("VentCap", 0.32, 0.12, (-2.0, 0.8, 3.2), "DC_Dark", r2=0.1)
# floodlight on the left corner
box("Flood", (0.35, 0.3, 0.25), (-2.5, -0.9, 2.25), "DC_Dark", rot=(0, 0, -30), bevel=0.03, outline=0.02)
box("FloodLens", (0.28, 0.03, 0.18), (-2.58, -1.05, 2.25), "DC_Bulb", rot=(0, 0, -30))
# sandbag walls either side of the door
for side in (-1, 1):
    for row in range(3):
        n = 3 - row
        for k in range(n):
            x = side * (3.05 + k * 0.42 + row * 0.21)
            ball(f"Bag{side}{row}{k}", 0.25, (x, -1.0 + random.uniform(-0.05, 0.05), 0.12 + row * 0.22),
                 "DC_Sandbag", scale=(0.95, 0.6, 0.62), rot=(0, 0, random.uniform(-8, 8)), segs=14, rings=8,
                 outline=0.015)
# a few crates and a barrel by the wall
box("Crate", (0.6, 0.6, 0.6), (-2.2, -1.75, 0.3), "DC_Wood", bevel=0.03, outline=0.02, rot=(0, 0, 12))
cyl("Barrel", 0.26, 0.8, (2.0, -1.8, 0.4), "DC_Rust", verts=20, bevel=0.03, outline=0.02)

sun("SunBack", (70, 0, 200), 3.0, WARM)
sun("SunFront", (50, 0, 25), 2.2, (0.85, 0.85, 1.0))
camera((0, -19.56, 5.96), (78, 0, 0), ortho=9.6)
render("bunker.png", 1400, 700, transparent=True)
