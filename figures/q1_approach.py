"""Render the Q1 image for the Approach Color learning rubric.

Two side-by-side panels showing the robot with one bare light detector
(no color filter). A red LED and a green LED are placed at fixed
positions NW and NE of the robot, at equal distance. Across panels only
the robot's body orientation changes — panel 1 shows the body turned
toward the green LED (NE), panel 2 shows it turned toward the red LED
(NW). Drawn on the standard question-image canvas.
"""

import math
from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    BORDER_W_BASE,
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

OUTPUT = Path(__file__).parent / "images" / "q1_approach.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2, PANEL_H_BASE // 2 + 30)
ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80
SENSOR_FORWARD_BASE = 75
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
    sensor = load_svg("light_sensor_blank", height_px=SENSOR_H_BASE * SCALE)
    red_light = load_svg("red_light", height_px=LIGHT_H_BASE * SCALE)
    green_light = load_svg("green_light", height_px=LIGHT_H_BASE * SCALE)

    for i, (header, body_compass) in enumerate(PANELS):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=header)

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-body_compass)

        sdx, sdy = polar_offset(SENSOR_FORWARD_BASE, body_compass)
        sensor_x = rx + sdx
        sensor_y = ry + sdy
        paste_rotated(
            canvas, sensor,
            center=(round(sensor_x * SCALE), round(sensor_y * SCALE)),
            rotation_deg=-body_compass,
        )

        # Sensor label with a short leader line.
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

        for sprite, compass, label in [
            (red_light,   RED_LED_COMPASS,   "Red LED"),
            (green_light, GREEN_LED_COMPASS, "Green LED"),
        ]:
            ldx, ldy = polar_offset(LIGHT_DISTANCE_BASE, compass)
            lx = rx + ldx
            ly = ry + ldy
            paste_rotated(canvas, sprite, center=(round(lx * SCALE), round(ly * SCALE)), rotation_deg=0)
            draw_label(canvas, label, (round(lx), round(ly) - 60), SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
