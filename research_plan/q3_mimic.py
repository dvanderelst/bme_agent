"""Render the Q3 image for the Mimic Color learning rubric.

Single-panel scene: robot facing east with two filtered light detectors
at the front — one with a red filter (upper), one with a green filter
(lower). A single cyan LED is placed straight ahead. Drawn on the
standard question-image canvas with the panel centered.

Predicted reading pattern: cyan light is roughly green + blue, so the
red-filter sensor reads low and the green-filter sensor reads high. The
contrast across two filters is the cue students need to identify color.
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

OUTPUT = Path(__file__).parent / "images" / "q3_mimic.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2 - 80, PANEL_H_BASE // 2)
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_OFFSET_BASE = 25
LIGHT_DISTANCE_BASE = 240

BODY_COMPASS = 90


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    px = panel_left(n_panels=1, panel_index=0)
    draw_panel_frame(canvas, draw, px, SCALE)

    rx = px + ROBOT_LOCAL_BASE[0]
    ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

    # Two filtered sensors at the front, both pointing east.
    sensor_x = rx + SENSOR_FORWARD_BASE
    red_y = ry - SENSOR_LATERAL_OFFSET_BASE
    green_y = ry + SENSOR_LATERAL_OFFSET_BASE

    sensor_red = load_svg("light_sensor_red", height_px=SENSOR_H_BASE * SCALE)
    sensor_green = load_svg("light_sensor_green", height_px=SENSOR_H_BASE * SCALE)
    paste_rotated(canvas, sensor_red, center=(sensor_x * SCALE, red_y * SCALE), rotation_deg=-BODY_COMPASS)
    paste_rotated(canvas, sensor_green, center=(sensor_x * SCALE, green_y * SCALE), rotation_deg=-BODY_COMPASS)

    # Single cyan LED straight ahead.
    ldx, ldy = polar_offset(LIGHT_DISTANCE_BASE, BODY_COMPASS)
    lx = rx + ldx
    ly = ry + ldy
    cyan = load_svg("cyan_light", height_px=LIGHT_H_BASE * SCALE)
    paste_rotated(canvas, cyan, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)

    draw_label(canvas, "Robot",        (rx, ry + 110),                 SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Red filter",   (sensor_x + 65, red_y - 10),    SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Green filter", (sensor_x + 65, green_y + 10),  SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Cyan LED",     (round(lx), round(ly) - 60),    SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
