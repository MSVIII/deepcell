# Portrait camera shots for the title screen slideshow (it pans each shot, then blurs across
# to the next). Rebuilds each scene, then renders title_*.png at 720x1280.
# The bunker is laid over the surface shot by export_to_app.py.

def portrait(name, loc, rot, lens, haze=None):
    if haze is not None:              # less haze when the camera stands inside the room
        vol = next((n for n in scene().world.node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
        if vol:
            vol.inputs["Density"].default_value = haze
    camera(loc, rot, lens=lens)
    render(f"title_{name}.png", 720, 1280)


exec(open(BL_DIR + "/surface.py").read())
bpy.data.objects["Sky"].scale.z = 1.6     # the tall frame sees above the sky plane otherwise
portrait("surface", (0, -14, 1.6), (92, 0, 0), 30)

exec(open(BL_DIR + "/room_dig.py").read())          # leaves the Drill Rig shown
portrait("dig", (1.0, -1.7, 1.8), (90, 0, -10), 24, haze=0.04)

exec(open(BL_DIR + "/room_farm.py").read())
portrait("farm", (0.7, -1.5, 1.8), (90, 0, 0), 24, haze=0.04)
