"""Render the Q4 image for the Mimic Color learning rubric.

Single-panel scene: robot facing east with three filtered light
detectors stacked at the front — red filter (top), green filter
(middle), blue filter (bottom). The three readings (R=200, G=190, B=50)
are annotated next to each sensor. The target LED is not shown —
students must reason about which of two candidate LEDs (described in
the question text) the pattern matches. Drawn on the standard
question-image canvas with the panel centered.
"""

from pathlib import Path

from PIL import ImageDraw

from render_lib import (
    HEADER_H_BASE,
    PANEL_H_BASE,
    PANEL_W_BASE,
    draw_label,
    draw_panel_frame,
    load_svg,
    make_canvas,
    panel_left,
    paste_rotated,
    save_on_white,
)

OUTPUT = Path(__file__).parent / "images" / "q4_mimic.png"

SCALE = 3
LABEL_FONT_BASE = 11
READING_FONT_BASE = 14

ROBOT_H_BASE = 180
SENSOR_H_BASE = 40

ROBOT_LOCAL_BASE = (PANEL_W_BASE // 2 - 60, PANEL_H_BASE // 2)
SENSOR_FORWARD_BASE = 75
SENSOR_LATERAL_OFFSET_BASE = 45

BODY_COMPASS = 90

R_READING = 200
G_READING = 190
B_READING = 50


def main() -> None:
    canvas = make_canvas(SCALE)
    draw = ImageDraw.Draw(canvas)

    px = panel_left(n_panels=1, panel_index=0)
    draw_panel_frame(canvas, draw, px, SCALE)

    rx = px + ROBOT_LOCAL_BASE[0]
    ry = HEADER_H_BASE + ROBOT_LOCAL_BASE[1]

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-BODY_COMPASS)

    # Three filtered sensors stacked at the front, all pointing east.
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

    save_on_white(canvas, OUTPUT)
    print(f"wrote {OUTPUT}  ({canvas.width}×{canvas.height})")


if __name__ == "__main__":
    main()
