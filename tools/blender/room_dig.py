# Scrap Dig room. Renders room_dig.png (manual) and room_dig_auto.png (with the Drill Rig).
# Layout matches row_floor.xml: workers stand on the left third, the machine sits in the
# centre, the scrap heap fills the right. Labels cover the top corners.
exec(open(BL_DIR + "/common.py").read())
exec(open(BL_DIR + "/room_shell.py").read())

sc = new_scene("RoomDig", haze=0.06)
base_materials()
random.seed(9)
room_shell(lamp_x=(-2.4, 2.2))

D = ROOM_D
# ---- left: lockers and pegboard against the wall (behind the workers)
for i in range(2):
    x = -4.4 + i * 0.62
    box(f"Locker{i}", (0.58, 0.45, 1.9), (x, D - 0.28, 0.95), "DC_Olive", bevel=0.03, outline=True)
    box(f"LockerVent{i}", (0.3, 0.02, 0.12), (x, D - 0.52, 1.6), "DC_Dark")
    box(f"LockerHandle{i}", (0.03, 0.03, 0.18), (x + 0.2, D - 0.52, 1.05), "DC_Steel")
box("Pegboard", (1.4, 0.04, 0.8), (-2.4, D - 0.06, 1.75), "DC_Wood")
for i, (x, z, s) in enumerate([(-2.9, 1.8, 0.35), (-2.6, 1.65, 0.45), (-2.25, 1.8, 0.3), (-1.95, 1.7, 0.4)]):
    box(f"Tool{i}", (0.05, 0.03, s), (x, D - 0.1, z), "DC_Dark")
box("BenchTop", (1.6, 0.6, 0.08), (-2.4, D - 0.4, 0.9), "DC_Wood", bevel=0.02, outline=True)
for dx in (-0.72, 0.72):
    box(f"BenchLeg{dx}", (0.08, 0.5, 0.86), (-2.4 + dx, D - 0.4, 0.43), "DC_Steel", outline=True)
box("Toolbox", (0.5, 0.25, 0.22), (-2.8, D - 0.4, 1.05), "DC_Red", bevel=0.03, outline=True)
cyl("Vice", 0.08, 0.3, (-1.9, D - 0.5, 1.0), "DC_Steel", rot=(0, 90, 0), outline=True)

# ---- right: the scrap heap
mats = ["DC_Rust", "DC_Steel", "DC_Olive", "DC_Rust", "DC_Dark", "DC_Wood"]
n = 0
for layer in range(5):
    count = 18 - layer * 3
    for k in range(count):
        cx = random.uniform(1.9 + layer * 0.3, 4.7 - layer * 0.3)
        cy = random.uniform(0.9 + layer * 0.15, D - 0.3)
        cz = 0.12 + layer * 0.3 + random.uniform(0, 0.1)
        m = random.choice(mats)
        rot = (random.uniform(-40, 40), random.uniform(-40, 40), random.uniform(0, 180))
        r = random.random()
        if r < 0.5:
            s = (random.uniform(0.25, 0.7), random.uniform(0.2, 0.5), random.uniform(0.1, 0.3))
            box(f"Scrap{n}", s, (cx, cy, cz), m, bevel=0.03, rot=rot, outline=True)
        elif r < 0.8:
            cyl(f"Scrap{n}", random.uniform(0.06, 0.16), random.uniform(0.4, 1.0), (cx, cy, cz), m,
                rot=rot, verts=10, outline=True)
        else:
            box(f"Scrap{n}", (random.uniform(0.5, 0.9), 0.04, random.uniform(0.3, 0.6)), (cx, cy, cz),
                "DC_Steel", rot=rot, outline=True)
        n += 1
torus("Tyre", 0.32, 0.11, (3.1, 1.2, 0.55), "DC_Dark", rot=(80, 15, 10), outline=True)
torus("Tyre2", 0.28, 0.1, (4.2, 1.6, 1.25), "DC_Dark", rot=(60, -20, 30), outline=True)
box("CarDoor", (1.0, 0.06, 0.7), (3.6, 1.9, 1.5), "DC_Red", rot=(12, -20, 8), bevel=0.04, outline=True)
box("CarWindow", (0.6, 0.07, 0.25), (3.6, 1.87, 1.68), "DC_Dark", rot=(12, -20, 8))
cyl("Drum", 0.27, 0.85, (4.55, 0.85, 0.425), "DC_Steel", verts=20, bevel=0.03, outline=True)
torus("DrumRing", 0.275, 0.025, (4.55, 0.85, 0.55), "DC_Dark")
# crates behind the heap
for i, (x, z, s) in enumerate([(4.4, 0.35, 0.7), (4.35, 1.05, 0.6)]):
    box(f"Crate{i}", (s, s, s), (x, D - 0.45, z), "DC_Wood", bevel=0.03, outline=True)
    box(f"CrateBand{i}", (s + 0.02, s + 0.02, 0.06), (x, D - 0.45, z), "DC_Dark")

# ---- centre (manual): wheelbarrow + shovel + loose scrap
manual = []
wb = [box("BarrowTub", (0.9, 0.55, 0.35), (0.4, 1.3, 0.55), "DC_Rust", rot=(0, 8, 0), bevel=0.05, outline=True),
      torus("BarrowWheel", 0.17, 0.05, (0.95, 1.3, 0.2), "DC_Dark", rot=(90, 0, 0), outline=True),
      cyl("BarrowHandleL", 0.025, 0.9, (-0.2, 1.1, 0.5), "DC_Wood", rot=(0, 75, 0)),
      cyl("BarrowHandleR", 0.025, 0.9, (-0.2, 1.5, 0.5), "DC_Wood", rot=(0, 75, 0)),
      cyl("BarrowLeg", 0.025, 0.35, (0.1, 1.3, 0.2), "DC_Steel")]
for i in range(6):
    wb.append(box(f"BarrowScrap{i}", (random.uniform(0.15, 0.3), 0.15, 0.1),
                  (0.4 + random.uniform(-0.3, 0.3), 1.3 + random.uniform(-0.15, 0.15), 0.8),
                  random.choice(mats), rot=(random.uniform(0, 90), random.uniform(0, 90), 0), outline=True))
wb.append(cyl("ShovelHandle", 0.025, 1.3, (1.35, D - 0.35, 0.7), "DC_Wood", rot=(0, -12, 0)))
wb.append(box("ShovelBlade", (0.25, 0.04, 0.3), (1.2, D - 0.35, 0.12), "DC_Steel", rot=(0, -12, 0), outline=True))
manual += wb

# ---- centre (automated): the Drill Rig
auto = []
X = 0.4
auto.append(box("RigBase", (1.5, 1.0, 0.25), (X, 1.4, 0.125), "DC_Steel", bevel=0.04, outline=True))
auto.append(box("RigStripe", (1.52, 1.02, 0.08), (X, 1.4, 0.24), "DC_Hazard"))
for dx in (-0.55, 0.55):
    auto.append(box(f"RigTower{dx}", (0.12, 0.12, 2.6), (X + dx, 1.4, 1.5), "DC_Olive", bevel=0.02, outline=True))
for z in (0.9, 1.7, 2.5):
    auto.append(box(f"RigCross{z}", (1.1, 0.08, 0.08), (X, 1.4, z), "DC_Olive", outline=True))
auto.append(box("RigMotor", (0.8, 0.7, 0.6), (X, 1.4, 2.1), "DC_Olive", bevel=0.05, outline=True))
auto.append(box("RigMotorStripe", (0.82, 0.72, 0.1), (X, 1.4, 1.85), "DC_Hazard"))
auto.append(cyl("RigShaft", 0.08, 1.6, (X, 1.4, 1.0), "DC_Steel", outline=True))
auto.append(cyl("RigBit", 0.2, 0.5, (X, 1.4, 0.15), "DC_Steel", r2=0.02, rot=(180, 0, 0), verts=12, outline=True))
auto.append(cyl("RigExhaust", 0.07, 0.7, (X + 0.3, 1.5, 2.65), "DC_Rust", outline=True))
auto.append(box("RigScreen", (0.3, 0.03, 0.18), (X - 0.15, 1.04, 2.15), "DC_Screen"))
auto.append(cyl("RigGauge", 0.08, 0.04, (X + 0.2, 1.04, 2.15), "DC_Steel", rot=(90, 0, 0), outline=True))
auto.append(cyl("RigGaugeFace", 0.06, 0.02, (X + 0.2, 1.02, 2.15), "DC_Bulb", rot=(90, 0, 0)))
auto.append(cyl("RigCable", 0.03, 2.4, (X - 1.5, D - 0.2, 2.6), "DC_Dark", rot=(0, 90, 0)))
auto.append(point("RigGlow", (X - 0.15, 0.7, 2.15), 15, (0.3, 1.0, 0.6)))
# loose rubble around the bit
for i in range(8):
    auto.append(box(f"Rubble{i}", (0.12, 0.1, 0.06),
                    (X + random.uniform(-0.6, 0.6), 1.0 + random.uniform(0, 0.6), 0.03),
                    "DC_Rock", rot=(0, 0, random.uniform(0, 90))))

room_camera()


def show(objs, on):
    for o in objs:
        o.hide_render = not on
        o.hide_viewport = not on


show(auto, False); show(manual, True)
render("room_dig.png", 1500, 600)
show(auto, True); show(manual, False)
render("room_dig_auto.png", 1500, 600)
