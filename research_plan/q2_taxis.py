"""Render the Q2 image for the taxis learning rubric.

Three side-by-side panels showing the robot with two external ears, both
pointing along the body's forward axis (aligned). A single speaker
appears in each panel at three different angles relative to the robot's
forward direction: 0° (in front), 45°, and 90° (off to the side).

Predicted reading pattern: left and right readings are equal across all
three panels (the two ears are oriented identically and any small
asymmetry from physical separation is treated as noise). The magnitude
decreases as the speaker moves off-axis — the tuning curve.
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

OUTPUT = Path(__file__).parent / "images" / "q2_taxis.png"

SCALE = 3
MARGIN_PX = 30
HEADER_FONT_BASE = 14

# Panel layout
PANEL_W_BASE = 400
PANEL_H_BASE = 400
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 3
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (110, 110)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
SPEAKER_H_BASE = 90
SPEAKER_DISTANCE_BASE = 240
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25      # ear sideways offset from body centerline

# Robot faces east. "Speaker at θ" in the question is θ from the body's
# forward direction (compass 90°). So the absolute compass position of the
# speaker is 90° + θ.
BODY_COMPASS = 90
SPEAKER_OFFSETS = [0, 45, 90]      # angles from forward, per panel


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
    ear = load_svg("ear", height_px=EAR_H_BASE * SCALE)
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)

    draw = ImageDraw.Draw(canvas)

    for i, offset in enumerate(SPEAKER_OFFSETS):
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

        # Header.
        draw_label(
            canvas,
            f"Situation {i + 1}  (speaker: {offset}°)",
            (px + PANEL_W_BASE // 2, HEADER_H_BASE // 2),
            SCALE,
            HEADER_FONT_BASE,
        )

        rx = px + ROBOT_LOCAL_BASE[0]
        ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

        # Robot facing east.
        paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

        # Two aligned ears at the front of the robot. Both pointing east.
        # Lateral offset is perpendicular to forward — so along the y-axis
        # for an east-facing robot.
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
        # the front of the robot (the ear mount line) rather than the body
        # centerline — visually clearer.
        if offset == 90:
            sx_base += EAR_MOUNT_DIST_BASE
        paste_rotated(
            canvas, speaker,
            center=(round(sx_base * SCALE), round(sy_base * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(speaker_compass),
        )

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
