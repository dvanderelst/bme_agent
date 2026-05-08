"""Render the Q1 image for the taxis learning rubric.

Scene: robot facing east with two bare sound sensors mounted at the front
(one front-left, one front-right). Two speakers at equal distance —
speaker 1 directly in front of the robot (east), speaker 2 at 45° from
front (south-east). Both speakers face the robot.
"""

import math
from pathlib import Path

from PIL import Image

from render_lib import (
    crop_to_content,
    draw_label,
    load_svg,
    paste_rotated,
    save_on_white,
    speaker_rotation_facing_robot,
)

OUTPUT = Path(__file__).parent / "images" / "q1_taxis.png"

SCALE = 3
MARGIN_PX = 30
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SPEAKER_H_BASE = 90
SENSOR_H_BASE = 40

ROBOT_CENTER_BASE = (200, 350)
# Two bare sensors at the front of the (east-facing) robot, offset north and
# south from the body's centerline. Both face east (forward).
SENSOR_L_CENTER_BASE = (275, 325)
SENSOR_R_CENTER_BASE = (275, 375)
SPEAKER_DISTANCE_BASE = 290


def speaker_position(angle_from_north_deg: float) -> tuple[int, int]:
    rx, ry = ROBOT_CENTER_BASE
    rad = math.radians(angle_from_north_deg)
    x = rx + SPEAKER_DISTANCE_BASE * math.sin(rad)
    y = ry - SPEAKER_DISTANCE_BASE * math.cos(rad)
    return (round(x), round(y))


def main() -> None:
    canvas = Image.new("RGBA", (800 * SCALE, 800 * SCALE), (0, 0, 0, 0))

    rx, ry = ROBOT_CENTER_BASE

    # Robot facing east.
    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-90)

    # Two bare sensors at the front, also pointing east.
    sensor = load_svg("sound_sensor", height_px=SENSOR_H_BASE * SCALE)
    for cx, cy in (SENSOR_L_CENTER_BASE, SENSOR_R_CENTER_BASE):
        paste_rotated(canvas, sensor, center=(cx * SCALE, cy * SCALE), rotation_deg=-90)

    # Two speakers at equal distance, both facing the robot.
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)
    speaker_compass = {1: 90, 2: 135}
    speaker_pos = {n: speaker_position(a) for n, a in speaker_compass.items()}
    for n, angle in speaker_compass.items():
        sx, sy = speaker_pos[n]
        paste_rotated(
            canvas, speaker,
            center=(sx * SCALE, sy * SCALE),
            rotation_deg=speaker_rotation_facing_robot(angle),
        )

    # Labels.
    draw_label(canvas, "Robot",        (200, 470), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Left sensor",  (340, 285), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Right sensor", (340, 415), SCALE, LABEL_FONT_BASE)
    s1x, s1y = speaker_pos[1]
    s2x, s2y = speaker_pos[2]
    draw_label(canvas, "Speaker 1", (s1x, s1y - 65), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Speaker 2", (s2x, s2y + 65), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
