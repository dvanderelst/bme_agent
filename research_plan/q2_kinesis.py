"""Render the Q2 image for the kinesis learning rubric.

Three side-by-side panels showing the robot at three body orientations
(0°, 45°, 90° — compass: north, NE, east). A single speaker is fixed at
compass 45° (NE) from the robot in all three panels. The robot has one
external ear mounted along its forward axis (rotates with the body); the
ear is left/right symmetric.

Predicted readings: panels 1 and 3 are both 45° off-axis (equal readings,
since the ear is symmetric); panel 2 is on-axis (peak).
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
    speaker_rotation_facing_robot,
)

OUTPUT = Path(__file__).parent / "images" / "q2_kinesis.png"

SCALE = 3
MARGIN_PX = 30
LABEL_FONT_BASE = 11
HEADER_FONT_BASE = 14

# Panel layout (base pixels)
PANEL_W_BASE = 400
PANEL_H_BASE = 380
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 3
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (110, 260)   # robot center, measured from panel top-left
ROBOT_H_BASE = 180
EAR_H_BASE = 50
SPEAKER_H_BASE = 90
EAR_MOUNT_DIST_BASE = 75
SPEAKER_DISTANCE_BASE = 230
SPEAKER_COMPASS = 45            # speaker fixed at compass 45° (NE) of robot

BODY_ANGLES = [0, 45, 90]


def panel_left(i: int) -> int:
    return i * (PANEL_W_BASE + GAP_BASE)


def polar_offset(distance: float, compass_deg: float) -> tuple[float, float]:
    """Return (dx, dy) for a point at `distance` and `compass_deg` (CW from
    north) from an origin. y is image-down."""
    rad = math.radians(compass_deg)
    return (distance * math.sin(rad), -distance * math.cos(rad))


def main() -> None:
    canvas_w = N_PANELS * PANEL_W_BASE + (N_PANELS - 1) * GAP_BASE
    canvas_h = HEADER_H_BASE + PANEL_H_BASE
    canvas = Image.new("RGBA", (canvas_w * SCALE, canvas_h * SCALE), (0, 0, 0, 0))

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)

    draw = ImageDraw.Draw(canvas)

    for i, body_angle in enumerate(BODY_ANGLES):
        px = panel_left(i)

        # Panel border.
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

        # Header text above panel.
        draw_label(
            canvas,
            f"Situation {i + 1}  (body: {body_angle}°)",
            (px + PANEL_W_BASE // 2, HEADER_H_BASE // 2),
            SCALE,
            HEADER_FONT_BASE,
        )

        # Robot center in canvas coords.
        robot_x = px + ROBOT_LOCAL_BASE[0]
        robot_y = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        # Robot — rotated to body angle (compass CW = PIL CCW negative).
        paste_rotated(
            canvas, robot,
            center=(robot_x * SCALE, robot_y * SCALE),
            rotation_deg=-body_angle,
        )

        # Ear — mounted at the front, rotates with body.
        ear_dx, ear_dy = polar_offset(EAR_MOUNT_DIST_BASE, body_angle)
        paste_rotated(
            canvas, ear,
            center=(round((robot_x + ear_dx) * SCALE), round((robot_y + ear_dy) * SCALE)),
            rotation_deg=-body_angle,
        )

        # Speaker — fixed at compass 45° from the robot, facing the robot.
        sp_dx, sp_dy = polar_offset(SPEAKER_DISTANCE_BASE, SPEAKER_COMPASS)
        paste_rotated(
            canvas, speaker,
            center=(round((robot_x + sp_dx) * SCALE), round((robot_y + sp_dy) * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(SPEAKER_COMPASS),
        )

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
