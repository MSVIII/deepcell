# Lift shaft segment beside each room. Renders shaft.png (56 x 140 dp, same vertical frame
# as the room renders, so the landing lines up with the room floor).
exec(open(BL_DIR + "/common.py").read())

sc = new_scene("Shaft", haze=0.05)
base_materials()
H = 3.6
box("Back", (2.0, 0.3, 5.0), (0, 1.2, 1.8), "DC_Rock")
for k in range(10):
    ball(f"Stone{k}", random.uniform(0.15, 0.3), (random.uniform(-0.7, 0.7), 1.05, random.uniform(0.3, 3.4)),
         "DC_Earth", scale=(1, 0.4, 0.8), smooth=False, segs=8, rings=6)
for sx in (-0.48, 0.48):
    box(f"Rail{sx}", (0.1, 0.16, 5.0), (sx, 0.6, 1.8), "DC_Steel", outline=0.02)
    box(f"RailFlange{sx}", (0.22, 0.04, 5.0), (sx, 0.52, 1.8), "DC_Plate")
for z in (0.9, 2.7):
    box(f"Brace{z}", (1.0, 0.06, 0.06), (0, 0.65, z), "DC_Plate", rot=(0, 35, 0))
cyl("CableA", 0.02, 5.0, (-0.12, 0.4, 1.8), "DC_Dark")
cyl("CableB", 0.02, 5.0, (0.12, 0.4, 1.8), "DC_Dark")
# landing at floor level, ceiling slab at the top
box("Landing", (2.0, 1.2, 0.6), (0, 0.4, -0.3), "DC_Floor")
box("LandingEdge", (2.0, 0.1, 0.06), (0, -0.15, 0.02), "DC_Hazard")
box("Slab", (2.0, 1.2, 0.6), (0, 0.4, H + 0.3), "DC_Concrete")
cyl("Lamp", 0.08, 0.12, (0.55, 0.45, H - 0.25), "DC_Bulb", rot=(90, 0, 0), verts=12)
point("LampLight", (0.4, 0.1, H - 0.4), 22)
point("LowLight", (0, -0.6, 1.0), 6, (0.6, 0.7, 1.0))
camera((0, -10, 1.8), (90, 0, 0), ortho=4.0)
render("shaft.png", 240, 600)
