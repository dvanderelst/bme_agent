"""Render the Q4 image for the Mimic Color learning rubric.

Single-panel scene: robot facing east with three filtered light detectors
stacked at the front — red filter (top), green filter (middle), blue
filter (bottom). The three readings (R=200, G=190, B=50) are annotated
next to each sensor. The target LED is not shown — students must reason
about which of two candidate LEDs (described in the question text) the
pattern matches.
"""

from pathlib import Path

from PIL import Image

from render_lib import (
    crop_to_content,
    draw_label,
    load_svg,
    paste_rotated,
    save_on_white,
)

OUTPUT = Path(__file__).parent / "images" / "q4_mimic.png"

SCALE = 3
MARGIN_PX = 30
LABEL_FONT_BASE = 11
READING_FONT_BASE = 14

ROBOT_H_BASE = 180
SENSOR_H_BASE = 40

ROBOT_CENTER_BASE = (200, 400)
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_OFFSET_BASE = 45  # spacing between adjacent sensors

BODY_COMPASS = 90  # robot faces east

R_READING = 200
G_READING = 190
B_READING = 50


def main() -> None:
    canvas = Image.new("RGBA", (800 * SCALE, 800 * SCALE), (0, 0, 0, 0))

    rx, ry = ROBOT_CENTER_BASE

    # Robot facing east.
    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

    # Three filtered sensors stacked at the front, all pointing east.
    # Top → bottom: red, green, blue. Reading text sits on the same row as
    # its sensor; the colored dot inside each sensor sprite already
    # indicates the filter, so no separate filter label is needed.
    sensor_x = rx + SENSOR_FORWARD_BASE
    rows = [
        ("light_sensor_red",   ry - SENSOR_LATERAL_OFFSET_BASE, f"R = {R_READING}"),
        ("light_sensor_green", ry,                              f"G = {G_READING}"),
        ("light_sensor_blue",  ry + SENSOR_LATERAL_OFFSET_BASE, f"B = {B_READING}"),
    ]
    for asset, sy, reading_label in rows:
        sprite = load_svg(asset, height_px=SENSOR_H_BASE * SCALE)
        paste_rotated(canvas, sprite, center=(sensor_x * SCALE, sy * SCALE), rotation_deg=-BODY_COMPASS)
        draw_label(canvas, reading_label, (sensor_x + 65, sy), SCALE, READING_FONT_BASE)

    draw_label(canvas, "Robot", (rx, ry + 110), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
