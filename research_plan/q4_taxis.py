"""Render the Q4 image for the taxis learning rubric.

Single panel showing the robot with two external ears at the front, with
divergent axes — left ear tilted 45° toward the robot's left, right ear
tilted 45° toward the robot's right. The two readings (L=233, R=126) are
labelled next to the corresponding ear. No speaker is shown — students
must infer the speaker's bearing from the L/R contrast.
"""

from pathlib import Path

from PIL import Image, ImageDraw

from render_lib import (
    crop_to_content,
    draw_label,
    load_svg,
    paste_rotated,
    save_on_white,
)

OUTPUT = Path(__file__).parent / "images" / "q4_taxis.png"

SCALE = 3
MARGIN_PX = 30
READING_FONT_BASE = 16

# Panel layout
PANEL_W_BASE = 480
PANEL_H_BASE = 380
BORDER_W_BASE = 2

# Within the panel
ROBOT_LOCAL_BASE = (130, 190)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25

# Robot faces east. Ears tilted 45° from forward.
BODY_COMPASS = 90
EAR_TILT_FROM_FORWARD = 45
LEFT_EAR_COMPASS = (BODY_COMPASS - EAR_TILT_FROM_FORWARD) % 360   # 45°  (NE)
RIGHT_EAR_COMPASS = (BODY_COMPASS + EAR_TILT_FROM_FORWARD) % 360  # 135° (SE)

LEFT_READING = 233
RIGHT_READING = 126


def main() -> None:
    canvas = Image.new("RGBA", (PANEL_W_BASE * SCALE, PANEL_H_BASE * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle(
        [0, 0, PANEL_W_BASE * SCALE - 1, PANEL_H_BASE * SCALE - 1],
        outline=(0, 0, 0, 255),
        width=BORDER_W_BASE * SCALE,
    )

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)

    rx, ry = ROBOT_LOCAL_BASE

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

    # Reading labels next to each ear (further along the ear's axis).
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

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
