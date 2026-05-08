"""Render the Q4 image for the kinesis learning rubric.

Two consecutive panels showing the robot with a single forward-mounted
directional ear. Between the two panels the robot rotates 45° clockwise.
Panel 1: ear pointing at 0° (north), reading = 3. Panel 2: ear pointing at
45° (NE), reading = 7. The speaker's position is not shown — students must
infer it from the readings.
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
)

OUTPUT = Path(__file__).parent / "images" / "q4_kinesis.png"

SCALE = 3
MARGIN_PX = 30
HEADER_FONT_BASE = 14
READING_FONT_BASE = 18

# Panel layout
PANEL_W_BASE = 350
PANEL_H_BASE = 350
GAP_BASE = 30
HEADER_H_BASE = 60
N_PANELS = 2
BORDER_W_BASE = 2

# Within each panel
ROBOT_LOCAL_BASE = (175, 175)
ROBOT_H_BASE = 160
EAR_H_BASE = 45
EAR_MOUNT_DIST_BASE = 65

EAR_ANGLES = [0, 45]
READINGS = [126, 233]


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

    draw = ImageDraw.Draw(canvas)

    for i, (ear_angle, reading) in enumerate(zip(EAR_ANGLES, READINGS)):
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
            f"Situation {i + 1}  (ear: {ear_angle}°)",
            (px + PANEL_W_BASE // 2, HEADER_H_BASE // 2),
            SCALE,
            HEADER_FONT_BASE,
        )

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

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
