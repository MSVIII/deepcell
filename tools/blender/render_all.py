# Rebuild and render every Deepcell scene into tools/blender/out/.
# In Blender's Text Editor (or MCP), set BL_DIR to this folder first, for example:
#     BL_DIR = r"C:/path/to/Deepcell/tools/blender"
#     exec(open(BL_DIR + "/render_all.py").read())
# Then run `python tools/blender/export_to_app.py` to copy the images into the app.
for script in ("room_dig.py", "room_farm.py", "shaft.py", "surface.py", "bunker.py", "sprites.py"):
    print("==", script)
    exec(open(BL_DIR + "/" + script).read())
