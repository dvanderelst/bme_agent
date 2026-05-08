"""Render the Q3 image for the Approach Color learning rubric.

Same two-panel layout as Q2, but the robot now has *two* filtered light
detectors at the front — one with a red filter (offset to the body's
left), one with a green filter (offset to the body's right). Both
sensors rotate with the body and point along the body's forward axis. A
red LED and a green LED are at fixed positions NW and NE, equally
distant from the robot. Panel 1: body turned toward the green LED.
Panel 2: body turned toward the red LED.

Predicted reading pattern: the two-filter signature flips across the
panels — facing red gives (red-filter high, green-filter low), facing
green gives (red-filter low, green-filter high). The contrast across
filters reveals which way the robot is facing regardless of overall
brightness.
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

OUTPUT = Path(__file__).parent / "images" / "q3_approach.png"

SCALE = 3
MARGIN_PX = 30
HEADER_FONT_BASE = 14
LABEL_FONT_BASE = 11

# Panel layout
PANEL_W_BASE = 460
PANEL_H_BASE = 420
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 2
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (230, 290)
ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_BASE = 25
LIGHT_DISTANCE_BASE = 220

# LEDs at fixed compass bearings from the robot.
RED_LED_COMPASS = 315   # NW
GREEN_LED_COMPASS = 45  # NE

# (header, body compass)
PANELS = [
    ("Situation 1  (facing green)", GREEN_LED_COMPASS),
    ("Situation 2  (facing red)",   RED_LED_COMPASS),
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
    sensor_red = load_svg("light_sensor_red", height_px=SENSOR_H_BASE * SCALE)
    sensor_green = load_svg("light_sensor_green", height_px=SENSOR_H_BASE * SCALE)
    red_light = load_svg("red_light", height_px=LIGHT_H_BASE * SCALE)
    green_light = load_svg("green_light", height_px=LIGHT_H_BASE * SCALE)

    draw = ImageDraw.Draw(canvas)

    for i, (header, body_compass) in enumerate(PANELS):
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

        # Sensor positions: forward of robot center, with a small lateral
        # offset perpendicular to the body's forward axis. Red sensor on
        # the body's left, green on the body's right. Both still point
        # along the forward axis. Filter color is identified by the
        # colored dot inside each sensor sprite (same convention as
        # mimic Q3/Q4) — no per-sensor text label.
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

        # Two LEDs at fixed bearings.
        for sprite, compass, label in [
            (red_light,   RED_LED_COMPASS,   "Red LED"),
            (green_light, GREEN_LED_COMPASS, "Green LED"),
        ]:
            ldx_, ldy_ = polar_offset(LIGHT_DISTANCE_BASE, compass)
            lx = rx + ldx_
            ly = ry + ldy_
            paste_rotated(canvas, sprite, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)
            draw_label(canvas, label, (round(lx), round(ly) - 60), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
