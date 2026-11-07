# The shared room box: concrete walls, floor plates, ceiling beams and pipes, hanging lamps.
# Frame: x -5..5, floor z=0, ceiling z=ROOM_H, open front at y=0, back wall at y=ROOM_D.
ROOM_W, ROOM_H, ROOM_D = 10.0, 3.6, 2.6


def room_shell(lamp_x=(-2.2, 2.0), lamp_color=(1.0, 0.66, 0.35), wall="DC_Concrete", pipes=True):
    W, H, D = ROOM_W, ROOM_H, ROOM_D
    box("Floor", (W + 1, D + 0.6, 0.6), (0, D / 2 - 0.3, -0.3), "DC_Floor")
    box("Ceiling", (W + 1, D + 0.6, 0.6), (0, D / 2 - 0.3, H + 0.3), "DC_Concrete")
    box("FloorSlabFront", (W + 1, 0.1, 0.6), (0, -0.55, -0.3), "DC_Rock")
    box("CeilSlabFront", (W + 1, 0.1, 0.6), (0, -0.55, H + 0.3), "DC_Rock")
    box("BackWall", (W, 0.3, H), (0, D + 0.15, H / 2), wall)
    box("WallL", (0.3, D, H), (-W / 2 - 0.15, D / 2, H / 2), wall)
    box("WallR", (0.3, D, H), (W / 2 + 0.15, D / 2, H / 2), wall)
    box("FloorEdge", (W, 0.14, 0.05), (0, 0.1, 0.025), "DC_Hazard")
    for i in range(5):
        box(f"Plate{i}", (1.9, 1.2, 0.03), (-4 + i * 2, 1.4, 0.015), "DC_Plate", bevel=0.02)
    for i in range(9):
        box(f"Seam{i}", (0.05, 0.04, H), (-4.5 + i * 1.125, D - 0.02, H / 2), "DC_Dark")
    box("WallBand", (W, 0.08, 0.6), (0, D - 0.05, 0.3), "DC_Olive", bevel=0.02)
    box("WallBandTrim", (W, 0.1, 0.06), (0, D - 0.06, 0.62), "DC_Plate")
    for x in (-3.3, 0.0, 3.3):
        box(f"Beam{x}", (0.3, D, 0.25), (x, D / 2, H - 0.125), "DC_Plate", bevel=0.03)
        box(f"Post{x}", (0.25, 0.2, H), (x, D - 0.12, H / 2), "DC_Plate", bevel=0.03)
    if pipes:
        cyl("PipeA", 0.11, W, (0, D - 0.35, H - 0.4), "DC_Rust", rot=(0, 90, 0), outline=True)
        cyl("PipeB", 0.07, W, (0, D - 0.6, H - 0.3), "DC_Olive", rot=(0, 90, 0), outline=True)
        for x in (-4.0, -1.5, 1.6, 4.1):
            cyl(f"Clamp{x}", 0.14, 0.08, (x, D - 0.35, H - 0.4), "DC_Dark", rot=(0, 90, 0))
    for i, x in enumerate(lamp_x):
        cyl(f"Cable{i}", 0.012, 0.6, (x, 0.9, H - 0.3), "DC_Dark")
        cyl(f"Shade{i}", 0.28, 0.16, (x, 0.9, H - 0.68), "DC_Olive", verts=20, bevel=0.03, outline=True)
        cyl(f"Bulb{i}", 0.11, 0.12, (x, 0.9, H - 0.8), "DC_Bulb", verts=12)
        # One strong cone per lamp: a pool of light on the floor, dark between lamps.
        spot(f"Lamp{i}", (x, 0.9, H - 0.95), 1700, lamp_color, angle=78, blend=0.35, rot=(14, 0, 0))
        point(f"LampGlow{i}", (x, 1.2, H - 0.45), 18, lamp_color)
    area("Fill", (0, -4, 1.8), 16)


def room_camera():
    # 2.5:1 frame showing the room plus a sliver of the slabs above and below.
    camera((0, -13.9, 1.8), (90, 0, 0), lens=50)
