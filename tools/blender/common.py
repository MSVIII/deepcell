# Shared helpers for the Deepcell Blender scenes.
# Run inside Blender (Text Editor, or MCP). Each scene script does:
#     exec(open(BL_DIR + "/common.py").read())
# Every scene is built from code: stylized shapes, procedural toon materials, rim light.
import bpy, bmesh, math, random, os
from mathutils import Vector

OUT_DIR = os.path.join(BL_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------- scenes

def new_scene(name, haze=0.0):
    """Create (or empty) a scene, make it active, black world, optional haze."""
    sc = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    bpy.context.window.scene = sc
    for c in list(sc.collection.children):
        for ob in list(c.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(c)
    for ob in list(sc.collection.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print(e)
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    sc.eevee.use_volumetric_shadows = True
    w = bpy.data.worlds.get("DC_World_" + name) or bpy.data.worlds.new("DC_World_" + name)
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs[0].default_value = (0, 0, 0, 1)
    bg.inputs[1].default_value = 0.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if haze > 0:
        vs = nt.nodes.new("ShaderNodeVolumePrincipled")
        vs.inputs["Density"].default_value = haze
        vs.inputs["Color"].default_value = (0.9, 0.8, 0.7, 1)
        nt.links.new(vs.outputs[0], out.inputs["Volume"])
    sc.render.film_transparent = False
    return sc


def scene():
    return bpy.context.window.scene


def link(ob):
    sc = scene()
    c = bpy.data.collections.get("Build_" + sc.name)
    if c is None or c.name not in sc.collection.children:
        c = bpy.data.collections.new("Build_" + sc.name)
        sc.collection.children.link(c)
    c.objects.link(ob)
    return ob


# ---------------------------------------------------------------- materials

def sock(sockets, name, typ=None):
    for s in sockets:
        if s.name == name and (typ is None or s.type == typ) and s.enabled:
            return s
    for s in sockets:
        if s.name == name and (typ is None or s.type == typ):
            return s
    raise KeyError(name)


def ramp(nt, stops, interp="LINEAR"):
    r = nt.nodes.new("ShaderNodeValToRGB")
    cr = r.color_ramp
    cr.interpolation = interp
    while len(cr.elements) > len(stops):
        cr.elements.remove(cr.elements[-1])
    while len(cr.elements) < len(stops):
        cr.elements.new(0.5)
    for el, (pos, col) in zip(cr.elements, stops):
        el.position = pos
        el.color = (*col, 1.0) if len(col) == 3 else col
    return r


def mix(nt, mode, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = mode
    L = nt.links
    if isinstance(fac, (int, float)):
        sock(m.inputs, "Factor", "VALUE").default_value = fac
    else:
        L.new(fac, sock(m.inputs, "Factor", "VALUE"))
    for name, v in (("A", a), ("B", b)):
        s = sock(m.inputs, name, "RGBA")
        if isinstance(v, tuple):
            s.default_value = (*v, 1.0)
        else:
            L.new(v, s)
    return sock(m.outputs, "Result", "RGBA")


# Light bands: shadow (cool, dark) -> mid (warm) -> lit (warm, bright). Soft steps.
BANDS = [(0.0, (0.03, 0.035, 0.05)), (0.04, (0.03, 0.035, 0.05)), (0.07, (0.22, 0.18, 0.16)),
         (0.18, (0.22, 0.18, 0.16)), (0.24, (0.62, 0.48, 0.34)), (0.50, (0.70, 0.54, 0.38)),
         (0.62, (1.0, 0.80, 0.55)), (1.0, (1.05, 0.85, 0.58))]
# Neutral bands for outdoor / sprite scenes (no warm lamp tint).
BANDS_NEUTRAL = [(0.0, (0.05, 0.05, 0.07)), (0.05, (0.05, 0.05, 0.07)), (0.10, (0.28, 0.27, 0.28)),
                 (0.22, (0.30, 0.29, 0.30)), (0.30, (0.70, 0.66, 0.62)), (0.55, (0.76, 0.72, 0.66)),
                 (0.68, (1.0, 0.95, 0.86)), (1.0, (1.05, 1.0, 0.9))]


def toon(name, c1, c2, scale=6.0, grime=0.5, rust=0.0, rust_col=(0.32, 0.12, 0.05),
         streaks=False, rim=0.0, rim_col=(0.30, 0.45, 0.75), bands=None, grime_height=1.4):
    """Stylized material: noise colour variation, rust patches, grime low down, banded
    lighting (Shader to RGB), optional facing-based rim. Output is emission, so the colour
    in the render is exactly what the bands produce."""
    bands = bands or BANDS
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = scale
    sock(n1.inputs, "Detail").default_value = 4.0
    L.new(pos, n1.inputs["Vector"])
    r1 = ramp(nt, [(0.35, c1), (0.65, c2)])
    L.new(n1.outputs["Fac"], r1.inputs["Fac"])
    col = r1.outputs["Color"]
    if rust > 0:
        n2 = nt.nodes.new("ShaderNodeTexNoise")
        n2.inputs["Scale"].default_value = 2.5
        sock(n2.inputs, "Detail").default_value = 8.0
        sock(n2.inputs, "Roughness").default_value = 0.7
        L.new(pos, n2.inputs["Vector"])
        r2 = ramp(nt, [(0.62 - rust * 0.2, (0, 0, 0)), (0.66 - rust * 0.2, (1, 1, 1))])
        L.new(n2.outputs["Fac"], r2.inputs["Fac"])
        col = mix(nt, "MIX", r2.outputs["Color"], col, rust_col)
    if grime > 0:
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        L.new(pos, sep.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        L.new(sep.outputs["Z"], mr.inputs["Value"])
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = grime_height
        mr.inputs["To Min"].default_value = grime
        mr.inputs["To Max"].default_value = 0.0
        n3 = nt.nodes.new("ShaderNodeTexNoise")
        n3.inputs["Scale"].default_value = 1.6
        sock(n3.inputs, "Detail").default_value = 6.0
        L.new(pos, n3.inputs["Vector"])
        r3 = ramp(nt, [(0.5, (0, 0, 0)), (0.75, (grime * 0.8,) * 3)])
        L.new(n3.outputs["Fac"], r3.inputs["Fac"])
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        add.use_clamp = True
        L.new(mr.outputs["Result"], add.inputs[0])
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        L.new(r3.outputs["Color"], bw.inputs[0])
        L.new(bw.outputs[0], add.inputs[1])
        if streaks:
            wv = nt.nodes.new("ShaderNodeTexWave")
            wv.wave_type = "BANDS"
            wv.bands_direction = "X"
            wv.inputs["Scale"].default_value = 3.0
            wv.inputs["Distortion"].default_value = 6.0
            L.new(pos, wv.inputs["Vector"])
            r4 = ramp(nt, [(0.9, (0, 0, 0)), (1.0, (0.18,) * 3)])
            L.new(wv.outputs["Fac"], r4.inputs["Fac"])
            add2 = nt.nodes.new("ShaderNodeMath")
            add2.operation = "ADD"
            add2.use_clamp = True
            bw2 = nt.nodes.new("ShaderNodeRGBToBW")
            L.new(r4.outputs["Color"], bw2.inputs[0])
            L.new(add.outputs[0], add2.inputs[0])
            L.new(bw2.outputs[0], add2.inputs[1])
            add = add2
        col = mix(nt, "MIX", add.outputs[0], col, (0.03, 0.025, 0.02))
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    L.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    L.new(s2r.outputs["Color"], bw.inputs[0])
    rb = ramp(nt, bands, "LINEAR")
    L.new(bw.outputs[0], rb.inputs["Fac"])
    lit = mix(nt, "MULTIPLY", 1.0, col, rb.outputs["Color"])
    if rim > 0:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        rr = ramp(nt, [(0.55, (0, 0, 0)), (0.75, tuple(c * rim for c in rim_col))])
        L.new(lw.outputs["Facing"], rr.inputs["Fac"])
        lit = mix(nt, "ADD", 1.0, lit, rr.outputs["Color"])
    em = nt.nodes.new("ShaderNodeEmission")
    L.new(lit, em.inputs["Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    L.new(em.outputs[0], out.inputs["Surface"])
    return m


def emit(name, col, strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*col, 1)
    em.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def outline_material():
    """Black inverted-hull outline. Back faces culled; transparent to shadow rays."""
    o = emit("DC_Outline", (0.012, 0.01, 0.01), 1.0)
    o.use_backface_culling = True
    nt = o.node_tree
    em = next(n for n in nt.nodes if n.type == "EMISSION")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    lp = nt.nodes.new("ShaderNodeLightPath")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    nt.links.new(em.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return o


def base_materials(bands=None, rim=0.35):
    """The shared palette. Call again with other bands to retune a scene."""
    outline_material()
    b = bands
    toon("DC_Concrete", (0.20, 0.20, 0.19), (0.27, 0.26, 0.23), scale=4, grime=0.7, streaks=True, bands=b)
    toon("DC_Floor", (0.22, 0.21, 0.19), (0.30, 0.28, 0.25), scale=3, grime=0.6, bands=b)
    toon("DC_Rock", (0.10, 0.08, 0.07), (0.17, 0.13, 0.10), scale=3, grime=0.0, bands=b)
    toon("DC_Earth", (0.16, 0.11, 0.08), (0.22, 0.15, 0.10), scale=5, grime=0.0, bands=b)
    toon("DC_Olive", (0.25, 0.28, 0.16), (0.32, 0.35, 0.20), scale=5, grime=0.4, rust=0.45, rim=rim, bands=b)
    toon("DC_Rust", (0.36, 0.17, 0.08), (0.46, 0.24, 0.10), scale=8, grime=0.3, rust=0.3,
         rust_col=(0.2, 0.08, 0.03), rim=rim, bands=b)
    toon("DC_Steel", (0.30, 0.33, 0.36), (0.40, 0.43, 0.45), scale=6, grime=0.4, rust=0.4, rim=rim, bands=b)
    toon("DC_Plate", (0.26, 0.28, 0.30), (0.33, 0.35, 0.37), scale=6, grime=0.5, rust=0.3, bands=b)
    toon("DC_Wood", (0.36, 0.23, 0.12), (0.48, 0.32, 0.17), scale=12, grime=0.3, rim=rim, bands=b)
    toon("DC_Hazard", (0.75, 0.55, 0.08), (0.80, 0.60, 0.12), scale=4, grime=0.4, rust=0.3, rim=rim, bands=b)
    toon("DC_Dark", (0.06, 0.06, 0.07), (0.09, 0.09, 0.10), scale=4, grime=0.0, rim=rim, bands=b)
    toon("DC_Red", (0.45, 0.08, 0.06), (0.55, 0.12, 0.08), scale=5, grime=0.3, rust=0.3, rim=rim, bands=b)
    toon("DC_Cloth", (0.30, 0.27, 0.20), (0.36, 0.32, 0.24), scale=10, grime=0.3, rim=rim, bands=b)
    toon("DC_Soil", (0.12, 0.08, 0.05), (0.18, 0.12, 0.07), scale=14, grime=0.0, bands=b)
    toon("DC_Mushroom", (0.78, 0.70, 0.56), (0.86, 0.78, 0.62), scale=9, grime=0.0, rim=rim, bands=b)
    toon("DC_MushroomCap", (0.62, 0.36, 0.20), (0.72, 0.44, 0.24), scale=7, grime=0.0, rim=rim, bands=b)
    toon("DC_Skin", (0.72, 0.52, 0.38), (0.76, 0.56, 0.42), scale=4, grime=0.0, rim=rim, bands=b)
    emit("DC_Bulb", (1.0, 0.75, 0.40), 12.0)
    emit("DC_Screen", (0.25, 0.9, 0.55), 3.0)
    emit("DC_Ember", (1.0, 0.45, 0.12), 6.0)
    emit("DC_RedEye", (1.0, 0.12, 0.08), 2.2)
    emit("DC_GrowLight", (0.85, 1.0, 0.6), 6.0)


# ---------------------------------------------------------------- shapes

def finish(ob, mat, bevel, outline, segs=2, smooth=False):
    if mat:
        ob.data.materials.append(bpy.data.materials[mat])
    if bevel > 0:
        m = ob.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = segs
        m.limit_method = "ANGLE"
    for p in ob.data.polygons:
        p.use_smooth = smooth
    if outline:
        add_outline(ob, outline if isinstance(outline, float) else 0.025)


def add_outline(ob, th=0.025):
    ob.data.materials.append(bpy.data.materials["DC_Outline"])
    m = ob.modifiers.new("Outline", "SOLIDIFY")
    m.thickness = th
    m.offset = 1.0
    m.use_flip_normals = True
    m.material_offset = len(ob.data.materials) - 1
    m.use_rim = False


def _obj(name, bm, loc, rot, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    ob.scale = scale
    link(ob)
    return ob


def box(name, size, loc, mat=None, bevel=0.0, rot=(0, 0, 0), outline=False, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    ob = _obj(name, bm, loc, rot)
    finish(ob, mat, bevel, outline, segs)
    return ob


def cyl(name, r, depth, loc, mat=None, rot=(0, 0, 0), verts=16, bevel=0.0, outline=False, segs=2, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    ob = _obj(name, bm, loc, rot)
    finish(ob, mat, bevel, outline, segs)
    return ob


def ball(name, r, loc, mat=None, scale=(1, 1, 1), rot=(0, 0, 0), segs=16, rings=10, outline=False, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    ob = _obj(name, bm, loc, rot, scale)
    finish(ob, mat, 0.0, outline, smooth=smooth)
    return ob


def torus(name, r, thick, loc, mat=None, rot=(0, 0, 0), segs=20, outline=False):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, segments=segs, radius=r)
    ob = _obj(name, bm, loc, rot)
    if mat:
        ob.data.materials.append(bpy.data.materials[mat])
    sk = ob.modifiers.new("Skin", "SKIN")
    for v in ob.data.skin_vertices[0].data:
        v.radius = (thick, thick)
    if outline:
        add_outline(ob)
    return ob


# ---------------------------------------------------------------- lights, camera, render

def point(name, loc, energy, color=(1, 0.7, 0.4), size=0.1):
    L = bpy.data.lights.new(name, "POINT")
    L.energy = energy
    L.color = color
    L.shadow_soft_size = size
    o = bpy.data.objects.new(name, L)
    o.location = loc
    link(o)
    return o


def spot(name, loc, energy, color=(1, 0.66, 0.35), angle=85, blend=0.35, rot=(0, 0, 0), size=0.12):
    L = bpy.data.lights.new(name, "SPOT")
    L.energy = energy
    L.color = color
    L.spot_size = math.radians(angle)
    L.spot_blend = blend
    L.shadow_soft_size = size
    o = bpy.data.objects.new(name, L)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    link(o)
    return o


def area(name, loc, energy, color=(0.55, 0.65, 0.9), size=6, rot=(90, 0, 0)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy = energy
    L.color = color
    L.size = size
    o = bpy.data.objects.new(name, L)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    link(o)
    return o


def sun(name, rot, energy, color=(1, 0.9, 0.8), angle=5):
    L = bpy.data.lights.new(name, "SUN")
    L.energy = energy
    L.color = color
    L.angle = math.radians(angle)
    o = bpy.data.objects.new(name, L)
    o.rotation_euler = [math.radians(a) for a in rot]
    link(o)
    return o


def camera(loc, rot, lens=50, ortho=None):
    cam = bpy.data.cameras.new("Cam_" + scene().name)
    cam.lens = lens
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    co = bpy.data.objects.new("Cam_" + scene().name, cam)
    co.location = loc
    co.rotation_euler = [math.radians(a) for a in rot]
    link(co)
    scene().camera = co
    return co


def render(filename, w, h, transparent=False):
    sc = scene()
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print("rendered", sc.render.filepath)
