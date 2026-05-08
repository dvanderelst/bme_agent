"""Render the Q1 image for the Approach Color learning rubric.

Two side-by-side panels showing the robot with one bare light detector
(no color filter). A red LED and a green LED are placed at fixed
positions NW and NE of the robot, at equal distance. Across panels only
the robot's body orientation changes — panel 1 shows the body turned
toward the green LED (NE), panel 2 shows it turned toward the red LED
(NW).

Predicted reading pattern: the bare sensor responds to total brightness,
so rotating between the two LEDs at equal distance produces the same
reading — orientation alone cannot reveal which color the robot is
facing.
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

OUTPUT = Path(__file__).parent / "images" / "q1_approach.png"

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
    sensor = load_svg("light_sensor_blank", height_px=SENSOR_H_BASE * SCALE)
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

        # Robot at the panel's body orientation.
        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-body_compass)

        # Bare sensor mounted at the front, rotates with the body.
        sdx, sdy = polar_offset(SENSOR_FORWARD_BASE, body_compass)
        sensor_x = rx + sdx
        sensor_y = ry + sdy
        paste_rotated(
            canvas, sensor,
            center=(round(sensor_x * SCALE), round(sensor_y * SCALE)),
            rotation_deg=-body_compass,
        )

        # Sensor label with a short leader line so the attribution is
        # unambiguous regardless of body orientation.
        label_x = sensor_x
        label_y = sensor_y - 45
        draw.line(
            [
                (round(label_x * SCALE), round((label_y + 10) * SCALE)),
                (round(sensor_x * SCALE), round((sensor_y - 18) * SCALE)),
            ],
            fill=(0, 0, 0, 255),
            width=BORDER_W_BASE * SCALE // 2,
        )
        draw_label(
            canvas, "Sensor (no filter)",
            (round(label_x), round(label_y)),
            SCALE, LABEL_FONT_BASE,
        )

        # Two LEDs at fixed bearings (same in both panels).
        for sprite, compass, label in [
            (red_light,   RED_LED_COMPASS,   "Red LED"),
            (green_light, GREEN_LED_COMPASS, "Green LED"),
        ]:
            ldx, ldy = polar_offset(LIGHT_DISTANCE_BASE, compass)
            lx = rx + ldx
            ly = ry + ldy
            paste_rotated(canvas, sprite, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)
            draw_label(canvas, label, (round(lx), round(ly) - 60), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
