"""Render the Q4 image for the taxis learning rubric.

Single-panel scene: robot with two external ears at the front, with
divergent axes — left ear tilted 45° toward the robot's left, right ear
tilted 45° toward the robot's right. The two readings (L=233, R=126) are
labelled next to the corresponding ear. No speaker is shown — students
must infer the speaker's bearing from the L/R contrast. Drawn on the
standard question-image canvas with the panel centered.
"""

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
)

OUTPUT = Path(__file__).parent / "images" / "q4_taxis.png"

SCALE = 3
READING_FONT_BASE = 16

ROBOT_LOCAL_BASE = (155, 230)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25

BODY_COMPASS = 90
EAR_TILT_FROM_FORWARD = 45
LEFT_EAR_COMPASS = (BODY_COMPASS - EAR_TILT_FROM_FORWARD) % 360   # 45°  (NE)
RIGHT_EAR_COMPASS = (BODY_COMPASS + EAR_TILT_FROM_FORWARD) % 360  # 135° (SE)

LEFT_READING = 233
RIGHT_READING = 126


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    px = panel_left(n_panels=1, panel_index=0)
    draw_panel_frame(canvas, draw, px, SCALE)

    rx = px + ROBOT_LOCAL_BASE[0]
    ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)

    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

    ear_x = rx + EAR_MOUNT_DIST_BASE
    left_ear_y = ry - EAR_LATERAL_OFFSET_BASE
    right_ear_y = ry + EAR_LATERAL_OFFSET_BASE

    paste_rotated(
        canvas, ear,
        center=(round(ear_x * SCALE), round(left_ear_y * SCALE)),
        rotation_deg=-LEFT_EAR_COMPASS,
    )
    paste_rotated(
        canvas, ear,
        center=(round(ear_x * SCALE), round(right_ear_y * SCALE)),
        rotation_deg=-RIGHT_EAR_COMPASS,
    )

    draw_label(
        canvas,
        f"Left reading = {LEFT_READING}",
        (ear_x + 130, left_ear_y - 110),
        SCALE,
        READING_FONT_BASE,
    )
    draw_label(
        canvas,
        f"Right reading = {RIGHT_READING}",
        (ear_x + 130, right_ear_y + 110),
        SCALE,
        READING_FONT_BASE,
    )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
