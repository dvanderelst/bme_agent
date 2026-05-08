"""Render the Q4 image for the Approach Color learning rubric.

Two-panel scene with the same layout as Q3 but a different filter pair
and target set. The robot has a green-filter and a blue-filter sensor at
the front. A white LED sits at NW, a cyan LED at NE. Panel 1 shows the
body turned toward the cyan LED, panel 2 toward the white LED. Each
panel includes a reading caption with the green-filter and blue-filter
values for that orientation.

Predicted reading pattern: white and cyan both contain green and blue
components, so the green-filter and blue-filter readings barely differ
between panels — the two-filter signature can't disambiguate them. The
red dimension that separates white from cyan is invisible to this
filter pair, so the robot cannot reliably approach cyan.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

from render_lib import (
    crop_to_content,
    draw_label,
    load_svg,
    paste_rotated,
    save_on_white,
)

OUTPUT = Path(__file__).parent / "images" / "q4_approach.png"

SCALE = 3
MARGIN_PX = 30
HEADER_FONT_BASE = 14
LABEL_FONT_BASE = 11
READING_FONT_BASE = 14

# Panel layout
PANEL_W_BASE = 460
PANEL_H_BASE = 460
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 2
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (230, 280)
ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_BASE = 25
LIGHT_DISTANCE_BASE = 220

# LEDs at fixed compass bearings from the robot.
WHITE_LED_COMPASS = 315  # NW
CYAN_LED_COMPASS = 45    # NE

# (header, body compass, green-filter reading, blue-filter reading)
PANELS = [
    ("Situation 1  (facing cyan)",  CYAN_LED_COMPASS,  205, 210),
    ("Situation 2  (facing white)", WHITE_LED_COMPASS, 210, 200),
]


def panel_left(i: int) -> int:
    return i * (PANEL_W_BASE + GAP_BASE)


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas_w = N_PANELS * PANEL_W_BASE + (N_PANELS - 1) * GAP_BASE
    canvas_h = HEADER_H_BASE + PANEL_H_BASE
    canvas = Image.new("RGBA", (canvas_w * SCALE, canvas_h * SCALE), (0, 0, 0, 0))

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    sensor_green = load_svg("light_sensor_green", height_px=SENSOR_H_BASE * SCALE)
    sensor_blue = load_svg("light_sensor_blue", height_px=SENSOR_H_BASE * SCALE)
    white_light = load_svg("white_light", height_px=LIGHT_H_BASE * SCALE)
    cyan_light = load_svg("cyan_light", height_px=LIGHT_H_BASE * SCALE)

    draw = ImageDraw.Draw(canvas)

    for i, (header, body_compass, g_reading, b_reading) in enumerate(PANELS):
        px = panel_left(i)

        draw.rectangle(
            [
                px * SCALE,
                HEADER_H_BASE * SCALE,
                (px + PANEL_W_BASE) * SCALE,
                (HEADER_H_BASE + PANEL_H_BASE) * SCALE,
            ],
            outline=(0, 0, 0, 255),
            width=BORDER_W_BASE * SCALE,
        )

        draw_label(
            canvas, header,
            (px + PANEL_W_BASE // 2, HEADER_H_BASE // 2),
            SCALE, HEADER_FONT_BASE,
        )

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-body_compass)

        # Two filtered sensors at the front. Green on the body's left,
        # blue on the body's right. Both rotate with the body and point
        # along the forward axis. Filter color is conveyed by the
        # colored dot inside each sensor sprite.
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

        # Two LEDs at fixed bearings (same in both panels).
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

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
