"""Render the Q2 image for the Mimic Color learning rubric.

Same single-panel scene as Q1 but the single light detector now has a
red filter placed in front of it (light_sensor_red asset). Three target
LEDs at equal distance — red, green, blue — lit one at a time. Drawn on
the standard question-image canvas with the panel centered.
"""

import math
from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    HEADER_H_BASE,
    PANEL_H_BASE,
    PANEL_W_BASE,
    draw_label,
    draw_panel_frame,
    load_svg,
    make_canvas,
    panel_left,
    paste_rotated,
    save_on_white,
)

OUTPUT = Path(__file__).parent / "images" / "q2_mimic.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2 - 80, PANEL_H_BASE // 2)
SENSOR_FORWARD_BASE = 75
LIGHT_DISTANCE_BASE = 240

LIGHTS = [
    ("red",   "red_light",   60),
    ("green", "green_light", 90),
    ("blue",  "blue_light",  120),
]


def light_position(rx: int, ry: int, angle_from_north_deg: float) -> tuple[int, int]:
    rad = math.radians(angle_from_north_deg)
    x = rx + LIGHT_DISTANCE_BASE * math.sin(rad)
    y = ry - LIGHT_DISTANCE_BASE * math.cos(rad)
    return (round(x), round(y))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    px = panel_left(n_panels=1, panel_index=0)
    draw_panel_frame(canvas, draw, px, SCALE)

    rx = px + ROBOT_LOCAL_BASE[0]
    ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-90)

    # Light detector with a red filter, mounted at the front and facing east.
    sensor = load_svg("light_sensor_red", height_px=SENSOR_H_BASE * SCALE)
    paste_rotated(canvas, sensor, center=((rx + SENSOR_FORWARD_BASE) * SCALE, ry * SCALE), rotation_deg=-90)

    light_positions = {name: light_position(rx, ry, a) for name, _, a in LIGHTS}
    for name, asset, _ in LIGHTS:
        sprite = load_svg(asset, height_px=LIGHT_H_BASE * SCALE)
        lx, ly = light_positions[name]
        paste_rotated(canvas, sprite, center=(lx * SCALE, ly * SCALE), rotation_deg=0)

    draw_label(canvas, "Robot", (rx, ry + 110), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Light sensor (red filter)", (rx + SENSOR_FORWARD_BASE + 90, ry - 35), SCALE, LABEL_FONT_BASE)

    red_x, red_y = light_positions["red"]
    grn_x, grn_y = light_positions["green"]
    blu_x, blu_y = light_positions["blue"]
    draw_label(canvas, "Red LED",   (red_x, red_y - 60), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Green LED", (grn_x + 65, grn_y), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Blue LED",  (blu_x, blu_y + 60), SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
