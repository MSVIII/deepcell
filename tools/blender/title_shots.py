# Title screen shots, portrait 1080x2340 (full phone resolution, so nothing is upscaled).
# Each shot has one subject in focus (depth of field) and everything else falls off:
#   title_surface  the 3D bunker on the surface at dusk, a guard on the roof
#   title_dig      a digger mid-swing at the scrap heap, under a lamp cone
#   title_farm     a farmer reaching into a grow table
# The characters are the posed models from anim_sprites.py, linked into the room scenes.
# The app adds the motion on top: slow camera pans, drifting dust, drones crossing the sky.
ANIM_DEFS_ONLY = True
exec(open(BL_DIR + "/anim_sprites.py").read())   # brings common.py and sprites.py too

W, H = 1080, 2340   # the phone screen shape (19.5:9)


def take_character(fn, key_index):
    """Build and pose a character in its own scene; return its collection and root pivot."""
    pose, keys = fn(frames=False)
    pose(keys[key_index])
    coll = next(c for c in scene().collection.children if c.name.startswith("Build_Sprite_"))
    for o in list(coll.objects):
        if o.type in ("LIGHT", "CAMERA"):      # keep the sprite lights out of the room
            coll.objects.unlink(o)
            scene().collection.objects.link(o)
    root = next(o for o in coll.objects if o.name.startswith("Root"))
    return coll, root


def put(coll, root, loc, yaw, scale=1.1):
    scene().collection.children.link(coll)
    root.location = (loc[0], loc[1], loc[2] + root.location.z)
    root.rotation_euler = (0, 0, math.radians(yaw))
    root.scale = (scale, scale, scale)


def aim(cam_loc, target, lens):
    """Camera at cam_loc looking at target."""
    d = Vector(target) - Vector(cam_loc)
    cam = camera(cam_loc, (0, 0, 0), lens=lens)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return cam


def focus(cam, target, fstop):
    e = bpy.data.objects.new("Focus_" + scene().name, None)
    e.location = target
    link(e)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = e
    cam.data.dof.aperture_fstop = fstop


def quality():
    """More samples than the game renders: smooth lamp cones and depth of field at full size."""
    e = scene().eevee
    for attr, v in (("taa_render_samples", 128), ("volumetric_samples", 128), ("volumetric_tile_size", "4")):
        try:
            setattr(e, attr, v)
        except (AttributeError, TypeError):
            pass


def fill(loc, energy):
    """Soft warm fill from the camera side so the subject's face isn't lost in shadow."""
    point("TitleFill", loc, energy, (1.0, 0.8, 0.6), size=0.6)


def set_haze(density):
    vol = next((n for n in scene().world.node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
    if vol:
        vol.inputs["Density"].default_value = density


# ---------------------------------------------------------------- dig
def shot_dig():
    coll, root = take_character(digger, 4)              # pickaxe hitting the heap
    exec(open(BL_DIR + "/room_dig.py").read(), globals())   # scene scripts define globals (show, auto, ...)
    show(auto, False)
    show(manual, True)
    put(coll, root, (1.15, 1.0, 0), 62)
    set_haze(0.06)
    quality()
    fill((2.4, -1.2, 1.6), 40)
    cam = aim((2.7, -2.6, 1.15), (1.45, 1.2, 1.05), 26)
    focus(cam, (1.3, 1.0, 0.95), 1.6)
    render("title_dig.png", W, H)

# ---------------------------------------------------------------- farm
def shot_farm():
    coll, root = take_character(farmer, 3)              # reaching in, mushroom in hand
    exec(open(BL_DIR + "/room_farm.py").read(), globals())   # scene scripts define globals (show, auto, ...)
    put(coll, root, (1.55, 1.0, 0), 70)
    set_haze(0.05)
    quality()
    fill((2.8, -1.0, 1.7), 35)
    cam = aim((3.1, -2.4, 1.3), (1.75, 1.2, 1.05), 26)
    focus(cam, (1.65, 1.0, 1.0), 1.6)
    render("title_farm.png", W, H)

# ---------------------------------------------------------------- surface with the bunker
def shot_surface():
    g_coll, g_root = take_character(guard, 2)
    exec(open(BL_DIR + "/surface.py").read(), globals())   # scene scripts define globals (show, auto, ...)
    surface_scene = scene()
    surface_lights = {o.name: o for o in surface_scene.objects if o.type == "LIGHT"}
    exec(open(BL_DIR + "/bunker.py").read(), globals())   # scene scripts define globals (show, auto, ...)
    bunker_coll = next(c for c in scene().collection.children if c.name.startswith("Build_"))
    bpy.context.window.scene = surface_scene
    surface_scene.collection.children.link(bunker_coll)
# One warm sun from behind (the surface's) and the bunker's faint cold front light; the
# bunker's own lamps do the rest. Two of each would wash the bunker out.
    for o in bunker_coll.objects:
        if o.type == "LIGHT" and o.data.type == "SUN" and o.name.startswith("SunBack"):
            o.hide_render = True
    for name, o in surface_lights.items():
        if name.startswith("SunFront"):
            o.hide_render = True
    bpy.data.objects["Ground"].location.z = -0.5         # ground top level with the bunker base
    bpy.data.objects["Sky"].scale.z = 2.2                # the tall frame sees above the sky plane otherwise
    put(g_coll, g_root, (-1.45, -0.35, 2.02), 40, scale=1.0)   # on the deck, left of the hatch
    quality()
    cam = aim((3.2, -15.0, 1.4), (0.4, 0.0, 0.2), 32)       # looks a little down: bunker sits mid-screen, above the menu
    focus(cam, (0.0, -1.5, 1.6), 2.8)
    render("title_surface.png", W, H)


# Set TITLE_SHOTS_ONLY = ("dig",) before exec to render one shot (each takes a while).
for _name in globals().get("TITLE_SHOTS_ONLY", ("dig", "farm", "surface")):
    globals()["shot_" + _name]()
