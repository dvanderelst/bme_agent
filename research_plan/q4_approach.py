"""Render the Q4 image for the Approach Color learning rubric.

Two-panel scene with the same layout as Q3 but a different filter pair
and target set. The robot has a green-filter and a blue-filter sensor at
the front. A white LED sits at NW, a cyan LED at NE. Panel 1 shows the
body turned toward the cyan LED, panel 2 toward the white LED. Each
panel includes a reading caption with the green-filter and blue-filter
values for that orientation. Drawn on the standard question-image
canvas.

Predicted reading pattern: white and cyan both contain green and blue
components, so the green-filter and blue-filter readings barely differ
between panels — the two-filter signature can't disambiguate them. The
red dimension that separates white from cyan is invisible to this
filter pair, so the robot cannot reliably approach cyan.
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

OUTPUT = Path(__file__).parent / "images" / "q4_approach.png"

SCALE = 3
LABEL_FONT_BASE = 11
READING_FONT_BASE = 14

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2, PANEL_H_BASE // 2 + 10)
ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_BASE = 25
LIGHT_DISTANCE_BASE = 220

WHITE_LED_COMPASS = 315  # NW
CYAN_LED_COMPASS = 45    # NE

# (header, body compass, green-filter reading, blue-filter reading)
PANELS = [
    ("Situation 1  (facing cyan)",  CYAN_LED_COMPASS,  205, 210),
    ("Situation 2  (facing white)", WHITE_LED_COMPASS, 210, 200),
]
N_PANELS = 2


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    sensor_green = load_svg("light_sensor_green", height_px=SENSOR_H_BASE * SCALE)
    sensor_blue = load_svg("light_sensor_blue", height_px=SENSOR_H_BASE * SCALE)
    white_light = load_svg("white_light", height_px=LIGHT_H_BASE * SCALE)
    cyan_light = load_svg("cyan_light", height_px=LIGHT_H_BASE * SCALE)

    for i, (header, body_compass, g_reading, b_reading) in enumerate(PANELS):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=header)

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-body_compass)

        fdx, fdy = polar_offset(SENSOR_FORWARD_BASE, body_compass)
        left_compass = (body_compass - 90) % 360
        right_compass = (body_compass + 90) % 360
        ldx, ldy = polar_offset(SENSOR_LATERAL_BASE, left_compass)
        rdx, rdy = polar_offset(SENSOR_LATERAL_BASE, right_compass)

        for sprite, sx, sy in [
            (sensor_green, rx + fdx + ldx, ry + fdy + ldy),
            (sensor_blue,  rx + fdx + rdx, ry + fdy + rdy),
        ]:
            paste_rotated(
                canvas, sprite,
                center=(round(sx * SCALE), round(sy * SCALE)),
                rotation_deg=-body_compass,
            )

        for sprite, compass, label in [
            (white_light, WHITE_LED_COMPASS, "White LED"),
            (cyan_light,  CYAN_LED_COMPASS,  "Cyan LED"),
        ]:
            ldx_, ldy_ = polar_offset(LIGHT_DISTANCE_BASE, compass)
            lx = rx + ldx_
            ly = ry + ldy_
            paste_rotated(canvas, sprite, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)
            draw_label(canvas, label, (round(lx), round(ly) - 60), SCALE, LABEL_FONT_BASE)

        # Reading caption at the bottom of the panel.
        draw_label(
            canvas,
            f"Green-filter reading: {g_reading}     Blue-filter reading: {b_reading}",
            (px + PANEL_W_BASE // 2, HEADER_H_BASE + PANEL_H_BASE - 30),
            SCALE, READING_FONT_BASE,
        )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
