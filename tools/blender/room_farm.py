# Mushroom Farm room. Renders room_farm.png.
# Workers stand on the left third; grow beds fill the centre and right.
exec(open(BL_DIR + "/common.py").read())
exec(open(BL_DIR + "/room_shell.py").read())

sc = new_scene("RoomFarm", haze=0.14)
base_materials()
emit("DC_GlowCap", (0.30, 0.95, 0.80), 2.5)
random.seed(4)
GROW = (0.80, 1.0, 0.60)
room_shell(lamp_x=(-3.2, 0.2, 3.3), lamp_color=(1.0, 0.72, 0.42))
D = ROOM_D

# ---- left: water tank, sacks, shelf with jars
cyl("Tank", 0.55, 1.7, (-4.2, D - 0.65, 0.85), "DC_Steel", verts=24, bevel=0.04, outline=True)
for z in (0.4, 1.3):
    torus(f"TankRing{z}", 0.555, 0.03, (-4.2, D - 0.65, z), "DC_Dark")
cyl("TankPipe", 0.05, 2.0, (-3.4, D - 0.4, 1.9), "DC_Rust", rot=(0, 90, 0), outline=True)
cyl("TankTap", 0.06, 0.25, (-3.75, D - 0.9, 0.5), "DC_Red", rot=(0, 90, 0), outline=True)
for i, (x, y) in enumerate([(-3.1, 1.5), (-2.7, 1.7), (-2.95, 1.75)]):
    z = 0.25 if i < 2 else 0.62
    ball(f"Sack{i}", 0.35, (x, y + 0.4, z), "DC_Cloth", scale=(1.0, 0.8, 0.7), outline=True)
box("Shelf", (1.3, 0.35, 0.05), (-2.3, D - 0.2, 1.75), "DC_Wood", outline=True)
for i in range(5):
    cyl(f"Jar{i}", 0.08, 0.22, (-2.8 + i * 0.25, D - 0.2, 1.89), "DC_Mushroom" if i % 2 else "DC_Olive",
        verts=12, outline=True)


# ---- grow beds
def mushroom(name, x, y, z, s, glow=False):
    cyl(name + "Stem", 0.05 * s, 0.22 * s, (x, y, z + 0.11 * s), "DC_Mushroom", verts=8)
    ball(name + "Cap", 0.13 * s, (x, y, z + 0.22 * s), "DC_GlowCap" if glow else "DC_MushroomCap",
         scale=(1, 1, 0.55), segs=12, rings=8, outline=0.015)


def bed(i, x0, x1, y, z):
    w = x1 - x0
    cx = (x0 + x1) / 2
    box(f"Bed{i}", (w, 0.7, 0.3), (cx, y, z), "DC_Wood", bevel=0.03, outline=True)
    box(f"BedSoil{i}", (w - 0.12, 0.58, 0.05), (cx, y, z + 0.14), "DC_Soil")
    for lx in (x0 + 0.1, x1 - 0.1):
        box(f"BedLeg{i}{lx}", (0.08, 0.08, z), (lx, y, z / 2 - 0.15), "DC_Steel")
    k = 0
    x = x0 + 0.2
    while x < x1 - 0.15:
        for dy in (-0.15, 0.12):
            s = random.uniform(0.8, 1.5)
            mushroom(f"M{i}_{k}", x + random.uniform(-0.06, 0.06), y + dy, z + 0.16, s, glow=random.random() < 0.15)
            k += 1
        x += random.uniform(0.22, 0.32)


bed(0, -1.2, 1.4, 1.5, 0.75)
bed(1, 1.9, 4.6, 1.5, 0.75)
bed(2, -0.6, 2.6, D - 0.45, 1.65)      # upper rack bed against the wall
for x in (-0.5, 2.5):
    box(f"RackPost{x}", (0.08, 0.08, 1.6), (x, D - 0.45, 0.8), "DC_Steel", outline=True)

# drip line over the front beds
cyl("DripPipe", 0.035, 6.0, (1.7, 1.5, 2.55), "DC_Steel", rot=(0, 90, 0), outline=True)
for i in range(10):
    cyl(f"Drip{i}", 0.012, 0.25, (-1.0 + i * 0.6, 1.5, 2.42), "DC_Dark")

# grow light tubes over the beds
for i, (x, y, z) in enumerate([(0.1, 1.5, 2.25), (3.25, 1.5, 2.25)]):
    box(f"GrowTube{i}", (1.6, 0.12, 0.06), (x, y, z), "DC_GrowLight")
    box(f"GrowHood{i}", (1.7, 0.2, 0.06), (x, y, z + 0.06), "DC_Dark", outline=True)
    area(f"Grow{i}", (x, y, z - 0.08), 45, GROW, size=1.5, rot=(0, 0, 0))

# right corner: crates of harvest
for i, (x, z) in enumerate([(4.5, 0.25), (4.5, 0.72)]):
    box(f"HarvestCrate{i}", (0.6, 0.5, 0.45), (x, D - 0.4, z), "DC_Wood", bevel=0.03, outline=True)
    for j in range(3):
        ball(f"Harvest{i}{j}", 0.1, (x - 0.15 + j * 0.15, D - 0.55, z + 0.25), "DC_MushroomCap",
             scale=(1, 1, 0.6), segs=10, rings=6)

room_camera()
render("room_farm.png", 1500, 600)
