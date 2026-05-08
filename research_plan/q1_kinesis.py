"""Render the Q1 image for the kinesis learning rubric.

Scene: robot with a bare microphone (no external ear), facing east.
Two speakers at equal distance — speaker 1 directly in front of the robot
(east), speaker 2 at 45° from front (south-east). Both speakers face the
robot.
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

OUTPUT = Path(__file__).parent / "images" / "q1_kinesis.png"

SCALE = 3
MARGIN_PX = 30
CANVAS_BASE = (800, 800)

ROBOT_H_BASE = 180
SPEAKER_H_BASE = 90
MIC_H_BASE = 40
LABEL_FONT_BASE = 11

ROBOT_CENTER_BASE = (200, 350)
MIC_CENTER_BASE = (275, 350)   # at the front (east) of the east-facing robot
SPEAKER_DISTANCE_BASE = 290    # equal radius for both speakers


def speaker_position(angle_from_north_deg: float) -> tuple[int, int]:
    """Compass placement (CW from north) at SPEAKER_DISTANCE_BASE from the
    robot center. North is -y in image coordinates."""
    rx, ry = ROBOT_CENTER_BASE
    rad = math.radians(angle_from_north_deg)
    x = rx + SPEAKER_DISTANCE_BASE * math.sin(rad)
    y = ry - SPEAKER_DISTANCE_BASE * math.cos(rad)
    return (round(x), round(y))


def main() -> None:
    canvas_size = (CANVAS_BASE[0] * SCALE, CANVAS_BASE[1] * SCALE)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    # Robot facing east: clockwise 90° from native north = CCW -90° in PIL.
    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(
        canvas, robot,
        center=(ROBOT_CENTER_BASE[0] * SCALE, ROBOT_CENTER_BASE[1] * SCALE),
        rotation_deg=-90,
    )

    # Bare microphone (the sound_sensor asset), mounted at the front of the
    # robot, also facing east.
    mic = load_svg("sound_sensor", height_px=MIC_H_BASE * SCALE)
    paste_rotated(
        canvas, mic,
        center=(MIC_CENTER_BASE[0] * SCALE, MIC_CENTER_BASE[1] * SCALE),
        rotation_deg=-90,
    )

    # Two speakers at compass 90° (east, in front of the robot) and 135° (SE,
    # 45° clockwise from in-front), both facing the robot. Equal distances.
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
    draw_label(canvas, "Robot",      (200, 460), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Sound sensor", (350, 350), SCALE, LABEL_FONT_BASE)
    s1x, s1y = speaker_pos[1]
    s2x, s2y = speaker_pos[2]
    draw_label(canvas, "Speaker 1", (s1x, s1y - 65), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Speaker 2", (s2x, s2y - 65), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
