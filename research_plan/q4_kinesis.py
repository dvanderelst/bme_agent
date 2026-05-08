"""Render the Q4 image for the kinesis learning rubric.

Two consecutive panels showing the robot with a single forward-mounted
directional ear. Between the two panels the robot rotates 45° clockwise.
Panel 1: ear pointing at 0° (north), reading = 126. Panel 2: ear
pointing at 45° (NE), reading = 233. The speaker's position is not
shown — students must infer it from the readings. Drawn on the standard
question-image canvas with the two panels centered.
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

OUTPUT = Path(__file__).parent / "images" / "q4_kinesis.png"

SCALE = 3
READING_FONT_BASE = 18

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2, PANEL_H_BASE // 2 - 30)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
EAR_MOUNT_DIST_BASE = 75

EAR_ANGLES = [0, 45]
READINGS = [126, 233]
N_PANELS = 2


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)

    for i, (ear_angle, reading) in enumerate(zip(EAR_ANGLES, READINGS)):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=f"Situation {i + 1}  (ear: {ear_angle}°)")

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-ear_angle)

        edx, edy = polar_offset(EAR_MOUNT_DIST_BASE, ear_angle)
        paste_rotated(
            canvas, ear,
            center=(round((rx + edx) * SCALE), round((ry + edy) * SCALE)),
            rotation_deg=-ear_angle,
        )

        draw_label(
            canvas,
            f"Reading = {reading}",
            (px + PANEL_W_BASE // 2, HEADER_H_BASE + PANEL_H_BASE - 35),
            SCALE,
            READING_FONT_BASE,
        )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
