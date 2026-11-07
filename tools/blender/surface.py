# Surface backdrop: storm sky, ruined skyline, rubble ground. Renders surface.png.
# The bunker is a separate transparent image (bunker.py) so the app can tap and shake it.
exec(open(BL_DIR + "/common.py").read())

sc = new_scene("Surface", haze=0.025)
base_materials(bands=BANDS_NEUTRAL, rim=0.0)
WARM = (1.0, 0.55, 0.28)
random.seed(21)

# sky: a big plane with an emission gradient and noise clouds
sky = bpy.data.materials.get("DC_Sky") or bpy.data.materials.new("DC_Sky")
sky.use_nodes = True
nt = sky.node_tree
nt.nodes.clear()
L = nt.links
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
L.new(tc.outputs["Generated"], sep.inputs[0])
grad = ramp(nt, [(0.0, (1.0, 0.58, 0.25)), (0.22, (0.95, 0.45, 0.18)), (0.32, (0.62, 0.25, 0.14)),
                 (0.45, (0.30, 0.13, 0.12)), (0.62, (0.12, 0.07, 0.10)), (1.0, (0.04, 0.03, 0.06))])
L.new(sep.outputs["Z"], grad.inputs["Fac"])
cn = nt.nodes.new("ShaderNodeTexNoise")
cn.inputs["Scale"].default_value = 3.0
sock(cn.inputs, "Detail").default_value = 6.0
mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Scale"].default_value = (1.0, 1.0, 3.5)
L.new(tc.outputs["Generated"], mp.inputs["Vector"])
L.new(mp.outputs["Vector"], cn.inputs["Vector"])
cr = ramp(nt, [(0.45, (0, 0, 0)), (0.62, (1, 1, 1))], "CONSTANT")
L.new(cn.outputs["Fac"], cr.inputs["Fac"])
cloud_col = mix(nt, "MULTIPLY", 1.0, grad.outputs["Color"], (0.55, 0.45, 0.45))
col = mix(nt, "MIX", cr.outputs["Color"], grad.outputs["Color"], cloud_col)
em = nt.nodes.new("ShaderNodeEmission")
em.inputs["Strength"].default_value = 1.5
L.new(col, em.inputs["Color"])
out = nt.nodes.new("ShaderNodeOutputMaterial")
L.new(em.outputs[0], out.inputs["Surface"])
skyp = box("Sky", (80, 0.1, 40), (0, 40, 14), None)
skyp.data.materials.append(sky)

# far skyline: flat dark silhouettes with lit windows
toon("DC_Far", (0.10, 0.07, 0.08), (0.12, 0.08, 0.09), scale=2, bands=BANDS_NEUTRAL)
toon("DC_Mid", (0.16, 0.12, 0.11), (0.20, 0.15, 0.13), scale=3, grime=0.3, bands=BANDS_NEUTRAL,
     rim=0.55, rim_col=WARM)
emit("DC_Window", (1.0, 0.6, 0.25), 2.0)


def building(name, x, y, w, h, mat, broken=True, windows=0.0):
    box(name, (w, 2.0, h), (x, y, h / 2 - 0.5), mat)
    if broken:
        for k in range(3):
            bw = random.uniform(0.3, 0.6) * w
            box(f"{name}Top{k}", (bw, 2.0, random.uniform(0.5, 2.0)),
                (x + random.uniform(-w / 3, w / 3), y, h - 0.5), mat, rot=(0, random.uniform(-25, 25), 0))
    if windows > 0:
        rows = int(h / 1.4)
        cols = max(1, int(w / 1.2))
        for r in range(rows):
            for c in range(cols):
                if random.random() < windows:
                    box(f"{name}W{r}_{c}", (0.35, 0.05, 0.5),
                        (x - w / 2 + 0.6 + c * (w - 1.2) / max(1, cols - 1 or 1), y - 1.03, 1.0 + r * 1.4),
                        "DC_Window")


x = -20
while x < 20:
    w = random.uniform(2.5, 5)
    building(f"Far{x:.0f}", x, 30, w, random.uniform(4, 11), "DC_Far", windows=0.06)
    x += w + random.uniform(0.2, 1.5)
x = -16
while x < 16:
    w = random.uniform(2.5, 4.5)
    if abs(x) > 3.5 or random.random() < 0.3:
        building(f"Mid{x:.0f}", x, 14, w, random.uniform(2, 5), "DC_Mid", windows=0.0)
    x += w + random.uniform(1.0, 3.0)

# storm sun low behind the city
emit("DC_SunDisc", (1.0, 0.62, 0.30), 2.2)
cyl("SunDisc", 3.0, 0.05, (-4.0, 39, 7.5), "DC_SunDisc", rot=(90, 0, 0), verts=48)
# power pylon and a crane silhouette
for k, px in enumerate((-9.0, 10.5)):
    for dx in (-0.6, 0.6):
        cyl(f"Pylon{k}{dx}", 0.08, 9, (px + dx * 0.5, 12, 4), "DC_Mid", rot=(0, dx * 6, 0))
    box(f"PylonArm{k}", (3.0, 0.15, 0.15), (px, 12, 7.5), "DC_Mid")
cyl("CraneMast", 0.25, 14, (6.5, 22, 6.5), "DC_Far")
box("CraneJib", (9, 0.3, 0.4), (9.5, 22, 13.2), "DC_Far", rot=(0, -4, 0))

# ground: rubble field in front
box("Ground", (80, 44, 1.0), (0, 0, -1.0), "DC_Earth")
toon("DC_Debris", (0.14, 0.11, 0.09), (0.19, 0.14, 0.11), scale=6, grime=0.3, bands=BANDS_NEUTRAL,
     rim=0.45, rim_col=WARM)
for i in range(90):
    x = random.uniform(-14, 14)
    y = random.uniform(0.5, 12)
    s = random.uniform(0.2, 0.9) * (1 + y / 10)
    if abs(x) < 3.8 and y < 4:
        continue                          # keep the bunker spot clear
    box(f"Rubble{i}", (s, s * 0.8, s * 0.5), (x, y, -0.5 + s * 0.2), "DC_Debris",
        rot=(random.uniform(-20, 20), random.uniform(-20, 20), random.uniform(0, 90)), bevel=0.05)
for i in range(7):
    x = random.choice([-1, 1]) * random.uniform(4.5, 11)
    cyl(f"FencePost{i}", 0.06, 1.4, (x, random.uniform(2, 5), 0.1), "DC_Dark",
        rot=(random.uniform(-15, 15), random.uniform(-15, 15), 0))
# wrecked car on the left
box("CarBody", (2.6, 1.2, 0.7), (-7.5, 3.5, -0.05), "DC_Rust", rot=(0, 6, 15), bevel=0.15, outline=True)
box("CarCabin", (1.4, 1.1, 0.55), (-7.7, 3.5, 0.5), "DC_Rust", rot=(0, 6, 15), bevel=0.1, outline=True)

# light: low warm sun behind the city (rims) + soft front fill
sun("SunBack", (70, 0, 190), 3.0, WARM)
sun("SunFront", (55, 0, 20), 1.6, (0.75, 0.75, 0.95))
camera((0, -14, 2.2), (93, 0, 0), lens=30)
render("surface.png", 1400, 1100)
