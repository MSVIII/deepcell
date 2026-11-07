# Deepcell logo: a steel hex badge with a hatch wheel around a glowing cell, and the DEEPCELL
# wordmark in Barlow Condensed ExtraBold (fonts/, SIL Open Font License).
# Renders logo.png (emblem + wordmark, title screen) and emblem.png (launcher icon).
exec(open(BL_DIR + "/common.py").read())

WARM = (1.0, 0.55, 0.28)
FONT = os.path.join(BL_DIR, "fonts", "BarlowCondensed-ExtraBold.ttf")


def lights_and_mats():
    base_materials(bands=BANDS_NEUTRAL, rim=0.8)
    toon("DC_LogoSteel", (0.62, 0.64, 0.66), (0.70, 0.72, 0.74), scale=5, rust=0.15, grime=0.0,
         bands=BANDS_NEUTRAL, rim=0.8, rim_col=WARM)
    toon("DC_LogoAmber", (0.90, 0.58, 0.16), (0.96, 0.66, 0.22), scale=5, grime=0.0,
         bands=BANDS_NEUTRAL, rim=0.8, rim_col=(1.0, 0.85, 0.5))
    toon("DC_LogoDark", (0.10, 0.11, 0.12), (0.13, 0.14, 0.15), scale=5, bands=BANDS_NEUTRAL, rim=0.5)
    emit("DC_CellGlow", (1.0, 0.62, 0.20), 3.0)
    sun("Key", (35, 0, 20), 3.2, (1.0, 0.95, 0.88))
    sun("Back", (60, 0, 200), 2.2, WARM)


def emblem(z=0.0, s=1.0):
    def L(x, y, zz):
        return (x * s, y * s, z + zz * s)
    cyl("Badge", 1.0 * s, 0.25 * s, L(0, 0, 0), "DC_LogoDark", rot=(90, 30, 0), verts=6, bevel=0.06 * s, outline=0.04 * s)
    cyl("BadgeRim", 1.08 * s, 0.18 * s, L(0, 0.05, 0), "DC_LogoSteel", rot=(90, 30, 0), verts=6, bevel=0.05 * s)
    for k in range(6):
        a = math.radians(k * 60)
        ball(f"Bolt{k}", 0.06 * s, L(math.cos(a) * 0.9, -0.14, math.sin(a) * 0.9), "DC_LogoSteel")
    torus("Wheel", 0.62 * s, 0.07 * s, L(0, -0.16, 0), "DC_LogoAmber", rot=(90, 0, 0), segs=40, outline=True)
    for k in range(4):
        a = 45 + k * 90
        box(f"Spoke{k}", (0.09 * s, 0.08 * s, 0.5 * s), L(math.cos(math.radians(a)) * 0.46, -0.16, math.sin(math.radians(a)) * 0.46),
            "DC_LogoAmber", rot=(0, -a + 90, 0), bevel=0.02 * s, outline=0.02 * s)
    cyl("Cell", 0.32 * s, 0.12 * s, L(0, -0.2, 0), "DC_LogoSteel", rot=(90, 30, 0), verts=6, bevel=0.03 * s, outline=0.03 * s)
    cyl("CellGlow", 0.24 * s, 0.13 * s, L(0, -0.21, 0), "DC_CellGlow", rot=(90, 30, 0), verts=6)
    cyl("Arrow", 0.13 * s, 0.22 * s, L(0, -0.3, -0.03), "DC_LogoDark", rot=(180, 0, 0), r2=0.0, verts=3)
    box("ArrowStem", (0.07 * s, 0.05 * s, 0.14 * s), L(0, -0.3, 0.12), "DC_LogoDark")


def word(text, x, z, size, mat):
    cu = bpy.data.curves.new(text, "FONT")
    cu.body = text
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.size = size
    cu.extrude = 0.06
    cu.bevel_depth = 0.012
    cu.align_x = "LEFT"
    ob = bpy.data.objects.new(text, cu)
    ob.location = (x, 0, z)
    ob.rotation_euler = (math.radians(90), 0, 0)
    link(ob)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    mo = bpy.data.objects.new(text + "Mesh", me)
    mo.matrix_world = ob.matrix_world.copy()
    link(mo)
    bpy.data.objects.remove(ob, do_unlink=True)
    bm = bmesh.new()                  # text meshes have doubled points; merge them so the
    bm.from_mesh(me)                  # outline shell doesn't poke through at the corners
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    mo.data.materials.clear()
    mo.data.materials.append(bpy.data.materials[mat])
    add_outline(mo, 0.015)
    return mo


# ---- title logo: emblem above the wordmark
new_scene("Logo")
lights_and_mats()
emblem(z=0.95, s=0.75)
spacing = 0.06
d = word("DEEP", 0, -0.45, 1.05, "DC_LogoSteel")
bpy.context.view_layer.update()
w_deep = d.dimensions.x
c = word("CELL", w_deep + spacing, -0.45, 1.05, "DC_LogoAmber")
bpy.context.view_layer.update()
total = w_deep + spacing + c.dimensions.x
for o in (d, c):
    o.location.x -= total / 2
camera((0, -20, 0.55), (90, 0, 0), ortho=3.7)
render("logo.png", 1200, 840, transparent=True)

# ---- launcher emblem alone
new_scene("Emblem")
lights_and_mats()
emblem(z=0.0, s=1.0)
camera((0, -20, 0.0), (90, 0, 0), ortho=2.5)
render("emblem.png", 512, 512, transparent=True)
