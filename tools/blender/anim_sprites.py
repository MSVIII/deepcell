# Animated sprites: the same models as sprites.py, posed frame by frame and rendered as
# numbered PNGs (name_0.png, name_1.png, ...). The app plays them with AnimationDrawable.
#
#   survivor_digger_work_*   pickaxe swing (8)        survivor_farmer_work_*  pick and basket (8)
#   survivor_guard_idle_*    scanning the sky (6)     survivor_guard_fire_*   shot with muzzle flash (3)
#   survivor_collector_walk_* walk cycle (8)      survivor_collector_grab_* picks up a pile (4)
#   enemy_scout_*, enemy_bomber_*, enemy_boss_*  spinning rotors (4)   enemy_shrike_*  wing flap (6)
#
# Each character function rigs and poses the model and returns (pose, keys). With frames=False
# it renders nothing, so title_shots.py can drop a posed character into a room scene.
#
# Characters are rigged with empties (hips, shoulders, head) instead of bones: the parts are
# rigid, so parenting is enough and keeps the toon outlines intact.
SPRITES_DEFS_ONLY = True
exec(open(BL_DIR + "/sprites.py").read())

_built = []


def _capture(filename, w, h, transparent=False):
    """Stand-in for render() while a builder runs: remember the shot, render later."""
    _built.append((filename, w, h))


def build(fn, *args):
    global render
    # Empty the earlier sprite, effect and icon scenes first, so part names stay exact
    # (no Arm1.001, no Flash.001 because vfx.py also has a "Flash").
    for sc in bpy.data.scenes:
        if sc.name.startswith(("Sprite_", "Fx_", "Icon_")):
            for o in list(sc.objects):
                bpy.data.objects.remove(o, do_unlink=True)
    real = render
    render = _capture
    try:
        fn(*args)
    finally:
        render = real
    return _built.pop()


def ob(name):
    return scene().objects[name]


def pivot(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    link(e)
    if parent:
        e.parent = parent
        e.matrix_parent_inverse = parent.matrix_world.inverted()
    bpy.context.view_layer.update()
    return e


def attach(names, piv):
    bpy.context.view_layer.update()
    for n in names:
        o = ob(n)
        mw = o.matrix_world.copy()
        o.parent = piv
        o.matrix_parent_inverse = piv.matrix_world.inverted()
        o.matrix_world = mw


def place(name, loc, rot=(0, 0, 0)):
    o = ob(name)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]


def frame_camera(ortho, cam_z, tilt=80):
    cam = scene().camera
    cam.data.ortho_scale = ortho
    d, t = 20, math.radians(tilt)
    cam.location = (0, -d * math.sin(t), cam_z + d * math.cos(t))
    cam.rotation_euler = (t, 0, 0)


def shoot(name, w, h, frames, pose):
    """Pose and render each frame."""
    for i, f in enumerate(frames):
        pose(f)
        bpy.context.view_layer.update()
        render(f"{name}_{i}.png", w, h, transparent=True)


def rig_survivor():
    """Root -> (LegR, LegL, Hips -> (ShoulderR, ShoulderL, Head)). Returns the upper pivots;
    the leg pivots are in LEGS (only the walk cycle moves them)."""
    root = pivot("Root", (0, 0, 0))
    hips = pivot("Hips", (0, 0, 0.55), root)
    sh_r = pivot("ShoulderR", (0.33, -0.04, 0.92), hips)
    sh_l = pivot("ShoulderL", (-0.33, -0.04, 0.92), hips)
    head = pivot("HeadPivot", (0, 0, 1.05), hips)
    LEGS.clear()
    for sx, side in ((0.13, "R"), (-0.13, "L")):
        leg = pivot("Leg" + side, (sx, 0, 0.55), root)
        attach([f"Leg{sx}", f"Boot{sx}"], leg)
        LEGS[side] = leg
    attach(["Body", "Belt", "Pack"], hips)
    attach(["Arm1", "Hand1"], sh_r)
    attach(["Arm-1", "Hand-1"], sh_l)
    head_parts = [o.name for o in scene().objects
                  if o.name.startswith(("Head", "Eye", "Hat", "Brim", "Cap", "Helmet", "Goggles", "Lens"))
                  and o.type == "MESH" and not o.name.startswith("HeadPivot")]
    attach(head_parts, head)
    return root, hips, sh_r, sh_l, head


LEGS = {}


def turn(p, x=0.0, y=0.0, z=0.0):
    p.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


# Arm angles: 0 hangs down, negative swings forward and up (-90 straight ahead).
# Hips angle: positive bends the upper body forward.

def digger(frames=True):
    build(survivor, "digger", ORANGE, YELLOW, lambda: (hard_hat(), pickaxe()))
    root, hips, sh_r, sh_l, head = rig_survivor()
    # Pickaxe held at the end of the handle, in line with the arm.
    place("PickHandle", (0.33, -0.06, 0.2))
    ob("PickHandle").scale = (1.0, 1.0, 0.75)
    place("PickHead", (0.33, -0.06, -0.12))
    ob("PickHead").scale = (0.18, 9.0, 1.5)     # box was 0.5 wide along X; turn it along Y
    attach(["PickHandle", "PickHead"], sh_r)
    frame_camera(3.2, 1.05)
    turn(root, z=62)
    keys = [  # arms, hips, dip
        (-100, -4, 0.0), (-145, -10, 0.0), (-162, -14, 0.0), (-120, 4, 0.0),
        (-62, 22, -0.03), (-52, 25, -0.045), (-56, 20, -0.03), (-78, 10, 0.0)]

    def pose(k):
        a, b, dz = k
        turn(sh_r, a)
        turn(sh_l, a)
        turn(hips, b)
        root.location.z = dz
    if frames:
        shoot("survivor_digger_work", 512, 384, keys, pose)
    return pose, keys


def farmer(frames=True):
    build(survivor, "farmer", GREEN, BROWN, lambda: (cap(), basket()))
    root, hips, sh_r, sh_l, head = rig_survivor()
    # Basket hangs from the left hand; a picked mushroom rides in the right hand.
    for n, dx in (("Basket", 0), ("Shroom0", -0.06), ("Shroom1", 0.05)):
        o = ob(n)
        o.location = (-0.37 + dx, -0.12, 0.33 + (0.11 if n != "Basket" else 0))
    attach(["Basket", "Shroom0", "Shroom1"], sh_l)
    ball("Picked", 0.075, (0.37, -0.12, 0.42), "DC_MushroomCap", scale=(1, 1, 0.65), outline=0.015)
    cyl("PickedStem", 0.03, 0.08, (0.37, -0.12, 0.37), "DC_Mushroom", verts=8)
    attach(["Picked", "PickedStem"], sh_r)
    frame_camera(3.2, 1.05)
    turn(root, z=62)
    # Reaches forward into the grow table at waist height, plucks, drops it in the basket.
    keys = [  # hips, right arm (x, y), left arm, mushroom in hand
        (0, -15, 0, -28, False), (10, -50, 0, -30, False), (20, -84, 0, -32, False),
        (22, -88, 0, -32, True), (14, -72, 10, -30, True), (6, -52, 28, -30, True),
        (4, -38, 30, -28, False), (0, -22, 10, -28, False)]

    def pose(k):
        b, ax, ay, al, held = k
        turn(hips, b)
        turn(sh_r, ax, ay)
        turn(sh_l, al)
        for n in ("Picked", "PickedStem"):
            ob(n).hide_render = not held
    if frames:
        shoot("survivor_farmer_work", 512, 384, keys, pose)
    return pose, keys


def guard(frames=True):
    build(survivor, "guard", OLIVE, OLIVE, lambda: (combat_helmet(), rifle()))
    root, hips, sh_r, sh_l, head = rig_survivor()
    # Rifle along the arms, barrel pointing away from the shoulder.
    place("Rifle", (0.33, -0.06, 0.16))
    ob("Rifle").scale = (1.0, 0.14, 7.5)          # box was 0.7 long along Y; stand it along Z
    place("RifleStock", (0.33, -0.06, 0.6))
    ob("RifleStock").scale = (1.0, 0.7, 1.6)
    attach(["Rifle", "RifleStock"], sh_r)
    cyl("Flash", 0.13, 0.36, (0.33, -0.06, -0.38), "DC_Ember", r2=0.0, verts=6)
    cyl("FlashCross", 0.07, 0.5, (0.33, -0.06, -0.33), "DC_Bulb", r2=0.0, verts=4, rot=(0, 0, 45))
    attach(["Flash", "FlashCross"], sh_r)
    frame_camera(2.4, 1.05)
    turn(root, z=58)

    def pose(k):
        yaw, a, b, dz, fire = k
        turn(root, z=58 + yaw)
        turn(sh_r, a)
        turn(sh_l, a + 12, 0, -18)
        turn(hips, b)
        turn(head, -abs(yaw) * 0.3, 0, yaw * 0.8)
        root.location.z = dz
        for n in ("Flash", "FlashCross"):
            ob(n).hide_render = not fire
    idle = [(0, -140, 0, 0.0, False), (5, -142, 0, 0.008, False), (10, -145, 1, 0.012, False),
            (6, -143, 0, 0.008, False), (0, -140, 0, 0.0, False), (-5, -138, 0, -0.004, False)]
    fire = [(0, -141, 0, 0.0, True), (0, -152, -6, 0.0, False), (0, -145, -2, 0.0, False)]
    if frames:
        shoot("survivor_guard_idle", 384, 384, idle, pose)
        shoot("survivor_guard_fire", 384, 384, fire, pose)
    return pose, idle


def collector_still():
    """survivor_collector.png: the Collector standing, framed like the other survivor portraits."""
    build(survivor, "collector", STEEL_BLUE, GREY, lambda: (cap(), sack()))
    render("survivor_collector.png", 256, 384, transparent=True)


def collector(frames=True):
    """The Collector: walks into each room, picks up the pile into a sack, walks back."""
    build(survivor, "collector", STEEL_BLUE, GREY, lambda: (cap(), sack()))
    root, hips, sh_r, sh_l, head = rig_survivor()
    attach(["Sack", "SackTie"], hips)
    frame_camera(2.4, 1.05)

    def pose(k):
        b, ar, al, lr, ll, dz, yaw = k
        turn(root, z=yaw)
        turn(hips, b)
        turn(sh_r, ar)
        turn(sh_l, al)
        turn(LEGS["R"], lr)
        turn(LEGS["L"], ll)
        root.location.z = dz
    # Walk to the right, seen three-quarter: legs swing opposite to the arms, the body dips
    # when a foot lands and rises when the legs pass (two bobs per cycle).
    walk = []
    for i in range(8):
        ph = i / 8 * 2 * math.pi
        sw = math.sin(ph)
        walk.append((6, 24 * sw, -24 * sw, -28 * sw, 28 * sw, -0.035 * abs(math.cos(ph)) + 0.01, 72))
    # Grab: crouch, scoop with both hands, swing it over the shoulder into the sack.
    grab = [(25, -40, -40, -10, 8, -0.05, 40), (40, -70, -70, -18, 14, -0.09, 40),
            (15, -150, -150, -6, 4, -0.02, 40), (4, -20, -20, 0, 0, 0.0, 40)]
    if frames:
        shoot("survivor_collector_walk", 384, 384, walk, pose)
        shoot("survivor_collector_grab", 384, 384, grab, pose)
    return pose, walk


def spin_rotors(name, builder, frames=4, size=256):
    build(builder)
    blades = [o for o in scene().objects if o.name.endswith("Blade")]
    base = {o.name: o.rotation_euler.z for o in blades}
    body = [o for o in scene().objects if o.type == "MESH"]
    z0 = {o.name: o.location.z for o in body}

    def pose(i):
        for o in blades:
            o.rotation_euler.z = base[o.name] + math.radians(45 * i + (i % 2) * 7)
        for o in body:
            o.location.z = z0[o.name] + 0.025 * math.sin(i / frames * 2 * math.pi)
    shoot(name, size, size, range(frames), pose)


def shrike_flap():
    build(shrike)
    body_parts = [o for o in scene().objects if o.type == "MESH"]
    wings = {}
    for sx in (-1, 1):
        piv = pivot(f"WingPivot{sx}", (sx * 0.2, 0.05, 0.1))
        names = [f"Wing{sx}"] + [f"Feather{sx}{k}" for k in range(3)]
        attach(names, piv)
        wings[sx] = piv
    z0 = {o.name: o.location.z for o in body_parts if o.parent is None}
    flap = [26, 12, -8, -24, -10, 10]

    def pose(i):
        a = flap[i]
        for sx, piv in wings.items():
            piv.rotation_euler = (0, math.radians(-sx * a), 0)
        lift = -0.03 * math.sin(i / 6 * 2 * math.pi)
        for o in body_parts:
            if o.parent is None:
                o.location.z = z0[o.name] + lift
    shoot("enemy_shrike", 256, 256, range(6), pose)


def turret_model():
    """Auto-Turret on the bunker roof: a fixed base, and a twin-barrel gun that turns about
    the point (0, 0, 0.35). Both are framed by the same camera, centred on that point, so in
    the app the gun image rotates about its own centre and sits exactly on the base image.
    Base parts are named T*, gun parts G*."""
    setup("turret", 2.6, cam_z=0.35, tilt=80, rim=0.5)
    cyl("TFoot", 0.5, 0.12, (0, 0, 0.06), "DC_Hazard", verts=20, bevel=0.02, outline=0.02)
    cyl("TDrum", 0.36, 0.26, (0, 0, 0.24), "DC_Plate", verts=20, bevel=0.03, outline=0.02)
    for a in range(0, 360, 60):
        r = math.radians(a)
        box(f"TBolt{a}", (0.06, 0.06, 0.06), (0.37 * math.cos(r), 0.37 * math.sin(r), 0.2), "DC_Dark")
    ball("GHousing", 0.27, (0, 0, 0.38), "DC_Olive", scale=(1.15, 0.9, 0.85), outline=0.022)
    box("GShroud", (0.34, 0.24, 0.3), (0, 0, 0.62), "DC_Steel", bevel=0.04, outline=0.02)
    for i, sx in enumerate((-0.08, 0.08)):
        cyl(f"GBarrel{i}", 0.05, 0.62, (sx, 0, 0.95), "DC_Dark", verts=12, outline=0.015)
        cyl(f"GMuzzle{i}", 0.065, 0.08, (sx, 0, 1.25), "DC_Steel", verts=12)
    box("GAmmo", (0.16, 0.22, 0.24), (0.3, 0, 0.42), "DC_Hazard", bevel=0.02, outline=0.015)
    ball("GLens", 0.05, (-0.2, -0.17, 0.48), "DC_RedEye")
    cyl("GFlash", 0.16, 0.34, (0, 0, 1.45), "DC_Ember", r2=0.0, verts=6)
    cyl("GFlashCross", 0.09, 0.42, (0, 0, 1.44), "DC_Bulb", r2=0.0, verts=4, rot=(0, 0, 45))
    render("turret_base.png", 256, 256, transparent=True)


def turret():
    """turret_base.png, turret_gun.png (at rest), turret_gun_0..2 (flash, recoil, rest)."""
    build(turret_model)
    names = [o.name for o in scene().objects if o.type == "MESH"]
    gun = [n for n in names if n.startswith("G")]
    base = [n for n in names if n.startswith("T")]
    axis = pivot("GunAxis", (0, 0, 0.35))
    attach(gun, axis)

    def show(group, on):
        for n in group:
            ob(n).hide_render = not on
            for c in ob(n).children:       # toon outlines, if any are child objects
                c.hide_render = not on

    show(gun, False)
    show(base, True)
    render("turret_base.png", 256, 256, transparent=True)
    show(base, False)

    def pose(k):
        dz, flash = k
        show(gun, True)
        axis.location.z = 0.35 + dz
        show(["GFlash", "GFlashCross"], flash)
    # Firing: flash, recoil, back in place. turret_gun.png is the gun at rest.
    shoot("turret_gun", 256, 256, [(0.0, True), (-0.06, False), (0.0, False)], pose)
    render("turret_gun.png", 256, 256, transparent=True)


STEEL_BLUE = ((0.22, 0.30, 0.40), (0.27, 0.36, 0.46))
GREY = ((0.36, 0.36, 0.34), (0.42, 0.42, 0.40))

# title_shots.py runs this file with ANIM_DEFS_ONLY = True to reuse the posed characters.
if not globals().get("ANIM_DEFS_ONLY"):
    digger()
    farmer()
    guard()
    collector()
    collector_still()
    turret()
    spin_rotors("enemy_scout", scout)
    spin_rotors("enemy_bomber", bomber)
    spin_rotors("enemy_boss", boss, size=384)
    shrike_flap()
