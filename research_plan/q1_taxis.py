"""Render the Q1 image for the taxis learning rubric.

Scene: robot facing east with two bare sound sensors mounted at the
front (one front-left, one front-right). Two speakers at equal distance —
speaker 1 directly in front of the robot (east), speaker 2 at 45° from
front (south-east). Both speakers face the robot. Drawn on the standard
question-image canvas with the panel centered.
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

OUTPUT = Path(__file__).parent / "images" / "q1_taxis.png"

SCALE = 3
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SPEAKER_H_BASE = 90
SENSOR_H_BASE = 40

ROBOT_LOCAL_BASE = (110, 170)
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_OFFSET_BASE = 25
SPEAKER_DISTANCE_BASE = 240


def speaker_position(rx: int, ry: int, angle_from_north_deg: float) -> tuple[int, int]:
    rad = math.radians(angle_from_north_deg)
    x = rx + SPEAKER_DISTANCE_BASE * math.sin(rad)
    y = ry - SPEAKER_DISTANCE_BASE * math.cos(rad)
    return (round(x), round(y))


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    px = panel_left(n_panels=1, panel_index=0)
    draw_panel_frame(canvas, draw, px, SCALE)

    rx = px + ROBOT_LOCAL_BASE[0]
    ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

    # Robot facing east.
    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-90)

    # Two bare sensors at the front, also facing east.
    sensor = load_svg("sound_sensor", height_px=SENSOR_H_BASE * SCALE)
    sensor_x = rx + SENSOR_FORWARD_BASE
    for sy in (ry - SENSOR_LATERAL_OFFSET_BASE, ry + SENSOR_LATERAL_OFFSET_BASE):
        paste_rotated(canvas, sensor, center=(sensor_x * SCALE, sy * SCALE), rotation_deg=-90)

    # Two speakers at equal distance, both facing the robot.
    speaker = load_svg("speaker", height_px=SPEAKER_H_BASE * SCALE)
    speaker_compass = {1: 90, 2: 135}
    speaker_pos = {n: speaker_position(rx, ry, a) for n, a in speaker_compass.items()}
    for n, angle in speaker_compass.items():
        sx, sy = speaker_pos[n]
        paste_rotated(
            canvas, speaker,
            center=(sx * SCALE, sy * SCALE),
            rotation_deg=speaker_rotation_facing_robot(angle),
        )

    # Labels.
    draw_label(canvas, "Robot",        (rx, ry + 110),                                      SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Left sensor",  (sensor_x + 65, ry - SENSOR_LATERAL_OFFSET_BASE - 25), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Right sensor", (sensor_x + 65, ry + SENSOR_LATERAL_OFFSET_BASE + 25), SCALE, LABEL_FONT_BASE)
    s1x, s1y = speaker_pos[1]
    s2x, s2y = speaker_pos[2]
    draw_label(canvas, "Speaker 1", (s1x, s1y - 65), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Speaker 2", (s2x, s2y + 65), SCALE, LABEL_FONT_BASE)

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
