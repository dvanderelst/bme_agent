"""Render the Q3 image for the kinesis learning rubric.

Scene: robot facing east. The ear is mounted with a 45° offset from the
body's forward axis — it sticks out from the robot's south-east corner
and points SE. Two speakers at equal distance: speaker 1 at compass 90°
(east, in front of the body) and speaker 2 at compass 135° (SE, in
front of the ear). Drawn on the standard question-image canvas.

The point: the reading is determined by the ear's pointing direction,
not the body's facing direction. Speaker 2 (aligned with the ear) gives
the louder reading even though speaker 1 is in front of the body.
"""

import math
from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    HEADER_H_BASE,
    draw_label,
    draw_panel_frame,
    load_svg,
    make_canvas,
    panel_left,
    paste_rotated,
    save_on_white,
    speaker_rotation_facing_robot,
)

OUTPUT = Path(__file__).parent / "images" / "q3_kinesis.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SPEAKER_H_BASE = 90
EAR_H_BASE = 50
EAR_MOUNT_DIST_BASE = 75

ROBOT_LOCAL_BASE = (110, 170)
SPEAKER_DISTANCE_BASE = 240

BODY_COMPASS = 90
EAR_OFFSET_FROM_BODY = 45
EAR_COMPASS = (BODY_COMPASS + EAR_OFFSET_FROM_BODY) % 360  # 135° — SE

SPEAKER_COMPASS = {
    1: BODY_COMPASS,   # east — in front of the body
    2: EAR_COMPASS,    # SE — in front of the ear
}


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

    # Ear at the front-center of the robot but tilted 45° off forward.
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)
    edx, edy = polar_offset(EAR_MOUNT_DIST_BASE, BODY_COMPASS)
    ex, ey = rx + edx, ry + edy
    paste_rotated(canvas, ear, center=(round(ex * SCALE), round(ey * SCALE)), rotation_deg=-EAR_COMPASS)

    # Speakers — both at equal distance, both facing the robot.
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)
    speaker_pos: dict[int, tuple[float, float]] = {}
    for n, compass in SPEAKER_COMPASS.items():
        sdx, sdy = polar_offset(SPEAKER_DISTANCE_BASE, compass)
        sx, sy = rx + sdx, ry + sdy
        speaker_pos[n] = (sx, sy)
        paste_rotated(
            canvas, speaker,
            center=(round(sx * SCALE), round(sy * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(compass),
        )

    draw_label(canvas, "Robot", (rx, ry + 115), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Ear",   (round(ex + 60), round(ey + 60)), SCALE, LABEL_FONT_BASE)
    s1x, s1y = speaker_pos[1]
    s2x, s2y = speaker_pos[2]
    draw_label(canvas, "Speaker 1", (round(s1x), round(s1y) - 65), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Speaker 2", (round(s2x), round(s2y) + 65), SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
