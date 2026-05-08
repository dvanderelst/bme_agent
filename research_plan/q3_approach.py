"""Render the Q3 image for the Approach Color learning rubric.

Same two-panel layout as Q2, but the robot now has *two* filtered light
detectors at the front — one with a red filter (offset to the body's
left), one with a green filter (offset to the body's right). Both
sensors rotate with the body and point along the body's forward axis. A
red LED and a green LED are at fixed positions NW and NE, equally
distant from the robot. Panel 1: body turned toward the green LED.
Panel 2: body turned toward the red LED. Drawn on the standard
question-image canvas.

Predicted reading pattern: the two-filter signature flips across the
panels — facing red gives (red-filter high, green-filter low), facing
green gives (red-filter low, green-filter high). The contrast across
filters reveals which way the robot is facing regardless of overall
brightness.
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

OUTPUT = Path(__file__).parent / "images" / "q3_approach.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2, PANEL_H_BASE // 2 + 30)
ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_BASE = 25
LIGHT_DISTANCE_BASE = 220

RED_LED_COMPASS = 315   # NW
GREEN_LED_COMPASS = 45  # NE

PANELS = [
    ("Situation 1  (facing green)", GREEN_LED_COMPASS),
    ("Situation 2  (facing red)",   RED_LED_COMPASS),
]
N_PANELS = 2


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    sensor_red = load_svg("light_sensor_red", height_px=SENSOR_H_BASE * SCALE)
    sensor_green = load_svg("light_sensor_green", height_px=SENSOR_H_BASE * SCALE)
    red_light = load_svg("red_light", height_px=LIGHT_H_BASE * SCALE)
    green_light = load_svg("green_light", height_px=LIGHT_H_BASE * SCALE)

    for i, (header, body_compass) in enumerate(PANELS):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=header)

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-body_compass)

        # Two filtered sensors at the front. Red on body's left, green on
        # body's right. Filter color is conveyed by the colored dot inside
        # each sensor sprite.
        fdx, fdy = polar_offset(SENSOR_FORWARD_BASE, body_compass)
        left_compass = (body_compass - 90) % 360
        right_compass = (body_compass + 90) % 360
        ldx, ldy = polar_offset(SENSOR_LATERAL_BASE, left_compass)
        rdx, rdy = polar_offset(SENSOR_LATERAL_BASE, right_compass)

        for sprite, sx, sy in [
            (sensor_red,   rx + fdx + ldx, ry + fdy + ldy),
            (sensor_green, rx + fdx + rdx, ry + fdy + rdy),
        ]:
            paste_rotated(
                canvas, sprite,
                center=(round(sx * SCALE), round(sy * SCALE)),
                rotation_deg=-body_compass,
            )

        for sprite, compass, label in [
            (red_light,   RED_LED_COMPASS,   "Red LED"),
            (green_light, GREEN_LED_COMPASS, "Green LED"),
        ]:
            ldx_, ldy_ = polar_offset(LIGHT_DISTANCE_BASE, compass)
            lx = rx + ldx_
            ly = ry + ldy_
            paste_rotated(canvas, sprite, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)
            draw_label(canvas, label, (round(lx), round(ly) - 60), SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
