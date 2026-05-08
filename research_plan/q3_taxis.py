"""Render the Q3 image for the taxis learning rubric.

Two side-by-side panels showing the robot with two external ears at the
front, but with divergent axes — the left ear points 45° to the left of
forward, the right ear points 45° to the right of forward. A single
speaker appears in each panel: panel 1 shows it straight ahead (0°),
panel 2 shows it 30° to the right of forward.

Predicted reading pattern: in panel 1 the source is symmetric, so
left = right (with absolute level set by the off-axis angle of 45°). In
panel 2 the source is closer to the right ear's axis, so right > left —
the L/R contrast that reveals direction.
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

OUTPUT = Path(__file__).parent / "images" / "q3_taxis.png"

SCALE = 3
MARGIN_PX = 30
HEADER_FONT_BASE = 14

# Panel layout
PANEL_W_BASE = 400
PANEL_H_BASE = 400
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 2
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (110, 110)
ROBOT_H_BASE = 180
EAR_H_BASE = 45
SPEAKER_H_BASE = 90
SPEAKER_DISTANCE_BASE = 240
EAR_MOUNT_DIST_BASE = 75
EAR_LATERAL_OFFSET_BASE = 25

# Robot faces east. Left ear tilted 45° toward the robot's left (= NE in
# absolute terms). Right ear tilted 45° toward the robot's right (= SE).
BODY_COMPASS = 90
EAR_TILT_FROM_FORWARD = 45
LEFT_EAR_COMPASS = (BODY_COMPASS - EAR_TILT_FROM_FORWARD) % 360   # 45°  (NE)
RIGHT_EAR_COMPASS = (BODY_COMPASS + EAR_TILT_FROM_FORWARD) % 360  # 135° (SE)

SPEAKER_OFFSETS = [0, 30]   # angles from forward, per panel


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

        # Two divergent ears: left mounted on the upper-front, tilted toward
        # the robot's left; right mounted on the lower-front, tilted right.
        ear_x = rx + EAR_MOUNT_DIST_BASE
        # Left ear: lateral offset in the robot's left direction (= -y for
        # an east-facing robot).
        paste_rotated(
            canvas, ear,
            center=(round(ear_x * SCALE), round((ry - EAR_LATERAL_OFFSET_BASE) * SCALE)),
            rotation_deg=-LEFT_EAR_COMPASS,
        )
        # Right ear.
        paste_rotated(
            canvas, ear,
            center=(round(ear_x * SCALE), round((ry + EAR_LATERAL_OFFSET_BASE) * SCALE)),
            rotation_deg=-RIGHT_EAR_COMPASS,
        )

        # Speaker.
        speaker_compass = (BODY_COMPASS + offset) % 360
        sdx, sdy = polar_offset(SPEAKER_DISTANCE_BASE, speaker_compass)
        paste_rotated(
            canvas, speaker,
            center=(round((rx + sdx) * SCALE), round((ry + sdy) * SCALE)),
            rotation_deg=speaker_rotation_facing_robot(speaker_compass),
        )

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
