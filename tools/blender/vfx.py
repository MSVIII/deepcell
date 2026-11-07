# Visual effects as flipbooks (transparent numbered PNGs), played with AnimationDrawable.
#   fx_explode_*  enemy destroyed / hit on the hatch (8)   fx_dust_*   pickaxe hits scrap (6)
#   fx_spores_*   mushroom picked (6)                      fx_sparks_* bullet hits an enemy (4)
# export_to_app.py fades the last frames out, so the effects end on nothing.
exec(open(BL_DIR + "/common.py").read())

random.seed(7)


def fx_scene(name, ortho):
    new_scene("Fx_" + name)
    base_materials(bands=BANDS_NEUTRAL, rim=0.3)
    sun("Key", (50, 0, 25), 3.0, (1.0, 0.9, 0.8))
    sun("Back", (60, 0, 200), 1.5, (1.0, 0.55, 0.28))
    camera((0, -20, 0), (90, 0, 0), ortho=ortho)
    tex = bpy.data.textures.get("FxClouds") or bpy.data.textures.new("FxClouds", "CLOUDS")
    tex.noise_scale = 0.35
    return tex


def puff(name, r, loc, mat, tex, strength=0.18):
    """Lumpy ball: a sphere pushed out by a cloud texture."""
    o = ball(name, r, loc, mat, segs=24, rings=16, outline=0.02)
    d = o.modifiers.new("Lumps", "DISPLACE")
    d.texture = tex
    d.strength = strength
    d.mid_level = 0.5
    o.modifiers.move(len(o.modifiers) - 1, 0)   # displace before the outline shell
    return o


def set_mat(o, mat):
    o.data.materials[0] = bpy.data.materials[mat]


def shots(name, w, h, n, pose):
    for i in range(n):
        pose(i)
        bpy.context.view_layer.update()
        render(f"{name}_{i}.png", w, h, transparent=True)


def ease_out(p):
    return 1 - (1 - p) ** 3


# ---------------------------------------------------------------- explosion

def explode():
    tex = fx_scene("explode", 2.7)
    emit("DC_FxHot", (1.0, 0.86, 0.5), 1.25)
    emit("DC_FxFire", (1.0, 0.45, 0.10), 1.15)
    emit("DC_FxEmber", (0.62, 0.14, 0.04), 1.0)
    toon("DC_FxSmoke", (0.34, 0.31, 0.29), (0.44, 0.40, 0.36), scale=5, grime=0.0,
         bands=BANDS_NEUTRAL, rim=0.35, rim_col=(1.0, 0.5, 0.25))
    balls = []
    for k in range(7):
        a = random.uniform(0, 2 * math.pi)
        d = random.uniform(0.1, 0.45) if k else 0.0
        balls.append((puff(f"Fire{k}", 0.3, (0, 0, 0), "DC_FxHot", tex), (math.cos(a) * d, math.sin(a) * d * 0.8), k * 0.25))
    flash = cyl("Flash", 1.0, 0.02, (0, -1.5, 0), "DC_FxHot", rot=(90, 0, 0), verts=12, r2=1.0)
    chips = []
    for k in range(10):
        a = random.uniform(0.2, math.pi - 0.2) if k < 7 else random.uniform(-0.6, 0.6) + math.pi * (k % 2)
        v = random.uniform(1.6, 2.4)
        o = box(f"Chip{k}", (0.09, 0.09, 0.06), (0, -0.6, 0), random.choice(("DC_Dark", "DC_Steel", "DC_Rust")),
                outline=0.012)
        chips.append((o, math.cos(a) * v, math.sin(a) * v, random.uniform(-400, 400)))
    stages = ["DC_FxHot", "DC_FxHot", "DC_FxFire", "DC_FxFire", "DC_FxEmber", "DC_FxSmoke", "DC_FxSmoke", "DC_FxSmoke"]

    def pose(i):
        flash.hide_render = i > 1
        flash.scale = (0.35 + i * 0.3,) * 3
        for o, (dx, dz), lag in balls:
            p = max(0.0, (i - lag) / 7)
            s = 0.35 + 1.2 * ease_out(min(1, p * 1.6))
            if i >= 5:
                s *= 1 - (i - 5) * 0.18
            o.scale = (s, s, s)
            o.location = (dx * (1 + p * 1.5), (0.3 if i >= 5 else 0.0), dz * (1 + p * 1.5) + p * 0.45 - 0.15)
            set_mat(o, stages[min(7, int(i - lag + 0.5))])
        t = i * 0.12
        for o, vx, vz, spin in chips:
            o.location = (vx * t, -0.6, vz * t - 4.5 * t * t)
            o.rotation_euler = (math.radians(spin * t), math.radians(spin * t * 0.6), 0)
            o.hide_render = i == 0
    shots("fx_explode", 256, 256, 8, pose)


# ---------------------------------------------------------------- dig dust

def dust():
    tex = fx_scene("dust", 2.4)
    toon("DC_FxDust", (0.36, 0.31, 0.26), (0.44, 0.38, 0.31), scale=5, grime=0.0,
         bands=BANDS_NEUTRAL, rim=0.3, rim_col=(1.0, 0.6, 0.3))
    emit("DC_FxSpark", (1.0, 0.72, 0.25), 1.3)
    puffs = []
    for k in range(6):
        side = -1 if k % 2 else 1
        puffs.append((puff(f"Dust{k}", 0.2, (0, 0, 0), "DC_FxDust", tex, 0.12), side * random.uniform(0.2, 0.9),
                      random.uniform(0.1, 0.5), random.uniform(0.7, 1.1)))
    chips = []
    for k in range(7):
        a = random.uniform(0.5, math.pi - 0.5)
        v = random.uniform(1.8, 3.0)
        o = box(f"Chip{k}", (0.07, 0.07, 0.05), (0, -0.5, 0), random.choice(("DC_Steel", "DC_Rust", "DC_Dark")),
                outline=0.01)
        chips.append((o, math.cos(a) * v, math.sin(a) * v))
    sparks = []
    for k in range(5):
        a = math.radians(random.uniform(25, 155))
        o = box(f"Spark{k}", (0.32, 0.025, 0.025), (0, -0.7, 0), "DC_FxSpark", rot=(0, -math.degrees(a), 0))
        sparks.append((o, a))

    def pose(i):
        p = i / 5
        for o, dx, dz, s in puffs:
            r = (0.35 + 1.4 * ease_out(p)) * s * (1 - 0.35 * max(0, p - 0.6) / 0.4)
            o.scale = (r, r, r * 0.8)
            o.location = (dx * ease_out(p), 0, -0.7 + dz * ease_out(p) + 0.15 * r)
        t = i * 0.09
        for o, vx, vz in chips:
            o.location = (vx * t, -0.5, -0.7 + vz * t - 6 * t * t)
            o.hide_render = i == 0
        for o, a in sparks:
            d = 0.2 + i * 0.35
            o.location = (math.cos(a) * d, -0.7, -0.7 + math.sin(a) * d)
            o.hide_render = i > 2
    shots("fx_dust", 256, 256, 6, pose)


# ---------------------------------------------------------------- spores

def spores():
    tex = fx_scene("spores", 2.4)
    emit("DC_FxSpore", (0.72, 1.0, 0.4), 1.15)
    toon("DC_FxPuff", (0.55, 0.62, 0.42), (0.62, 0.70, 0.48), scale=5, grime=0.0,
         bands=BANDS_NEUTRAL, rim=0.4, rim_col=(0.8, 1.0, 0.6))
    motes = []
    for k in range(14):
        o = ball(f"Mote{k}", random.uniform(0.035, 0.06), (0, -0.5, 0), "DC_FxSpore", segs=8, rings=6)
        motes.append((o, random.uniform(-0.8, 0.8), random.uniform(0.6, 1.5), random.uniform(0, 6.28)))
    clouds = [puff(f"Puff{k}", 0.18, (0, 0, 0), "DC_FxPuff", tex, 0.1) for k in range(3)]

    def pose(i):
        p = i / 5
        for o, dx, up, ph in motes:
            o.location = (dx * ease_out(p) + 0.08 * math.sin(ph + i), -0.5, -0.6 + up * ease_out(p))
            s = 1 - 0.5 * p
            o.scale = (s, s, s)
        for k, o in enumerate(clouds):
            r = (0.5 + 1.2 * ease_out(p)) * (1 - 0.6 * max(0, p - 0.5) / 0.5)
            o.scale = (r, r, r * 0.7)
            o.location = ((k - 1) * 0.35 * ease_out(p), 0, -0.6 + 0.25 * p)
    shots("fx_spores", 256, 256, 6, pose)


# ---------------------------------------------------------------- bullet hit

def sparks():
    fx_scene("sparks", 1.6)
    emit("DC_FxSpark", (1.0, 0.72, 0.25), 1.3)
    emit("DC_FxHot", (1.0, 0.86, 0.5), 1.25)
    core = ball("Core", 0.18, (0, -0.4, 0), "DC_FxHot", segs=12, rings=8)
    rays = []
    for k in range(9):
        a = k / 9 * 2 * math.pi + random.uniform(-0.2, 0.2)
        o = box(f"Ray{k}", (0.3, 0.03, 0.03), (0, -0.5, 0), "DC_FxSpark", rot=(0, -math.degrees(a), 0))
        rays.append((o, a, random.uniform(0.8, 1.2)))
    sizes = [1.0, 1.3, 0.8, 0.4]

    def pose(i):
        core.scale = (sizes[i] * (1.4 if i == 0 else 1.0),) * 3
        core.hide_render = i == 3
        for o, a, v in rays:
            d = (0.15 + 0.22 * i) * v
            o.location = (math.cos(a) * d, -0.5, math.sin(a) * d)
            o.scale = (1.0 - 0.2 * i, 1, 1)
    shots("fx_sparks", 192, 192, 4, pose)


explode()
dust()
spores()
sparks()
