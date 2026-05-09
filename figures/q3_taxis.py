"""Render the Q3 image for the taxis learning rubric.

Two side-by-side panels showing the robot with two external ears at the
front, but with divergent axes — the left ear points 45° to the left of
forward, the right ear points 45° to the right of forward. A single
speaker appears in each panel: panel 1 shows it straight ahead (0°),
panel 2 shows it 30° to the right of forward. Drawn on the standard
question-image canvas with the two panels centered.

Predicted reading pattern: in panel 1 the source is symmetric, so
left = right (with absolute level set by the off-axis angle of 45°). In
panel 2 the source is closer to the right ear's axis, so right > left —
the L/R contrast that reveals direction.
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

OUTPUT = Path(__file__).parent / "images" / "q3_taxis.png"

SCALE = 3

ROBOT_LOCAL_BASE = (140, 140)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
SPEAKER_H_BASE = 90
SPEAKER_DISTANCE_BASE = 240
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25

BODY_COMPASS = 90
EAR_TILT_FROM_FORWARD = 45
LEFT_EAR_COMPASS = (BODY_COMPASS - EAR_TILT_FROM_FORWARD) % 360   # 45°  (NE)
RIGHT_EAR_COMPASS = (BODY_COMPASS + EAR_TILT_FROM_FORWARD) % 360  # 135° (SE)

SPEAKER_OFFSETS = [0, 30]
N_PANELS = 2


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)

    for i, offset in enumerate(SPEAKER_OFFSETS):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=f"Situation {i + 1}  (speaker: {offset}°)")

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

        ear_x = rx + EAR_MOUNT_DIST_BASE
        paste_rotated(
            canvas, ear,
            center=(round(ear_x * SCALE), round((ry - EAR_LATERAL_OFFSET_BASE) * SCALE)),
            rotation_deg=-LEFT_EAR_COMPASS,
        )
        paste_rotated(
            canvas, ear,
            center=(round(ear_x * SCALE), round((ry + EAR_LATERAL_OFFSET_BASE) * SCALE)),
            rotation_deg=-RIGHT_EAR_COMPASS,
        )

        speaker_compass = (BODY_COMPASS + offset) % 360
        sdx, sdy = polar_offset(SPEAKER_DISTANCE_BASE, speaker_compass)
        paste_rotated(
            canvas, speaker,
            center=(round((rx + sdx) * SCALE), round((ry + sdy) * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(speaker_compass),
        )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
