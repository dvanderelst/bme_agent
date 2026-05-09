"""Render the Q2 image for the kinesis learning rubric.

Three side-by-side panels showing the robot at three body orientations
(0°, 45°, 90° — compass: north, NE, east). A single speaker is fixed at
compass 45° (NE) from the robot in all three panels. The robot has one
external ear mounted along its forward axis (rotates with the body); the
ear is left/right symmetric. Drawn on the standard question-image
canvas.

Predicted readings: panels 1 and 3 are both 45° off-axis (equal
readings, since the ear is symmetric); panel 2 is on-axis (peak).
"""

import math
from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    HEADER_H_BASE,
    draw_panel_frame,
    load_svg,
    make_canvas,
    panel_left,
    paste_rotated,
    save_on_white,
    speaker_rotation_facing_robot,
)

OUTPUT = Path(__file__).parent / "images" / "q2_kinesis.png"

SCALE = 3

ROBOT_LOCAL_BASE = (140, 300)
ROBOT_H_BASE = 180
EAR_H_BASE = 50
SPEAKER_H_BASE = 90
EAR_MOUNT_DIST_BASE = 75
SPEAKER_DISTANCE_BASE = 240
SPEAKER_COMPASS = 45            # speaker fixed at compass 45° (NE) of robot

BODY_ANGLES = [0, 45, 90]
N_PANELS = 3


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)

    for i, body_angle in enumerate(BODY_ANGLES):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=f"Situation {i + 1}  (body: {body_angle}°)")

        robot_x = px + ROBOT_LOCAL_BASE[0]
        robot_y = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(robot_x * SCALE, robot_y * SCALE), rotation_deg=-body_angle)

        ear_dx, ear_dy = polar_offset(EAR_MOUNT_DIST_BASE, body_angle)
        paste_rotated(
            canvas, ear,
            center=(round((robot_x + ear_dx) * SCALE), round((robot_y + ear_dy) * SCALE)),
            rotation_deg=-body_angle,
        )

        sp_dx, sp_dy = polar_offset(SPEAKER_DISTANCE_BASE, SPEAKER_COMPASS)
        paste_rotated(
            canvas, speaker,
            center=(round((robot_x + sp_dx) * SCALE), round((robot_y + sp_dy) * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(SPEAKER_COMPASS),
        )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
