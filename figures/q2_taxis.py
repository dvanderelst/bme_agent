"""Render the Q2 image for the taxis learning rubric.

Three side-by-side panels showing the robot with two external ears, both
pointing along the body's forward axis (aligned). A single speaker
appears in each panel at three different angles relative to the robot's
forward direction: 0° (in front), 45°, and 90° (off to the side). Drawn
on the standard question-image canvas.

Predicted reading pattern: left and right readings are equal across all
three panels (the two ears are oriented identically and any small
asymmetry from physical separation is treated as noise). The magnitude
decreases as the speaker moves off-axis — the tuning curve.
"""

import math
from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    HEADER_H_BASE,
    PANEL_W_BASE,
    draw_panel_frame,
    load_svg,
    make_canvas,
    panel_left,
    paste_rotated,
    save_on_white,
    speaker_rotation_facing_robot,
)

OUTPUT = Path(__file__).parent / "images" / "q2_taxis.png"

SCALE = 3

# Within each panel
ROBOT_LOCAL_BASE = (140, 140)        # panel-relative offset of robot center
ROBOT_H_BASE = 180
EAR_H_BASE = 45
SPEAKER_H_BASE = 90
SPEAKER_DISTANCE_BASE = 240
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25

# Robot faces east. "Speaker at θ" is θ from the body's forward direction
# (compass 90°), so the absolute compass position is 90° + θ.
BODY_COMPASS = 90
SPEAKER_OFFSETS = [0, 45, 90]      # angles from forward, per panel
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

    for i, offset in enumerate(SPEAKER_OFFSETS):
        px = panel_left(N_PANELS, i)
        draw_panel_frame(canvas, draw, px, SCALE, header_text=f"Situation {i + 1}  (speaker: {offset}°)")

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        # Robot facing east.
        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

        # Two aligned ears at the front of the robot. Both pointing east.
        ear_forward_x = rx + EAR_MOUNT_DIST_BASE       # forward = east = +x
        for lateral in (-EAR_LATERAL_OFFSET_BASE, +EAR_LATERAL_OFFSET_BASE):
            ear_y = ry + lateral
            paste_rotated(
                canvas, ear,
                center=(round(ear_forward_x * SCALE), round(ear_y * SCALE)),
                rotation_deg=-BODY_COMPASS,
            )

        # Speaker at the panel-specific offset from forward.
        speaker_compass = (BODY_COMPASS + offset) % 360
        sdx, sdy = polar_offset(SPEAKER_DISTANCE_BASE, speaker_compass)
        sx_base = rx + sdx
        sy_base = ry + sdy
        # For the 90° panel, shift the speaker east so it sits in line with
        # the front of the robot rather than the body centerline.
        if offset == 90:
            sx_base += EAR_MOUNT_DIST_BASE
        paste_rotated(
            canvas, speaker,
            center=(round(sx_base * SCALE), round(sy_base * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(speaker_compass),
        )

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
