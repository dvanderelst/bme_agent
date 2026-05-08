"""Render the Q2 image for the Mimic Color learning rubric.

Same scene as Q1 but the single light detector now has a red filter
placed in front of it (light_sensor_red asset). Three target LEDs at
equal distance — red, green, blue — lit one at a time.
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
)

OUTPUT = Path(__file__).parent / "images" / "q2_mimic.png"

SCALE = 3
MARGIN_PX = 30
LABEL_FONT_BASE = 11

ROBOT_H_BASE = 180
SENSOR_H_BASE = 40
LIGHT_H_BASE = 80

ROBOT_CENTER_BASE = (200, 400)
SENSOR_CENTER_BASE = (275, 400)
LIGHT_DISTANCE_BASE = 290

LIGHTS = [
    ("red",   "red_light",   60),
    ("green", "green_light", 90),
    ("blue",  "blue_light",  120),
]


def light_position(angle_from_north_deg: float) -> tuple[int, int]:
    rx, ry = ROBOT_CENTER_BASE
    rad = math.radians(angle_from_north_deg)
    x = rx + LIGHT_DISTANCE_BASE * math.sin(rad)
    y = ry - LIGHT_DISTANCE_BASE * math.cos(rad)
    return (round(x), round(y))


def main() -> None:
    canvas = Image.new("RGBA", (800 * SCALE, 800 * SCALE), (0, 0, 0, 0))

    rx, ry = ROBOT_CENTER_BASE

    robot = load_svg("robot", height_px=ROBOT_H_BASE * SCALE)
    paste_rotated(canvas, robot, center=(rx * SCALE, ry * SCALE), rotation_deg=-90)

    # Light detector with a red filter, mounted at the front and facing east.
    sensor = load_svg("light_sensor_red", height_px=SENSOR_H_BASE * SCALE)
    sx, sy = SENSOR_CENTER_BASE
    paste_rotated(canvas, sensor, center=(sx * SCALE, sy * SCALE), rotation_deg=-90)

    light_positions = {name: light_position(a) for name, _, a in LIGHTS}
    for name, asset, _ in LIGHTS:
        sprite = load_svg(asset, height_px=LIGHT_H_BASE * SCALE)
        lx, ly = light_positions[name]
        paste_rotated(canvas, sprite, center=(lx * SCALE, ly * SCALE), rotation_deg=0)

    draw_label(canvas, "Robot", (200, 510), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Light sensor (red filter)", (350, 365), SCALE, LABEL_FONT_BASE)

    red_x, red_y = light_positions["red"]
    grn_x, grn_y = light_positions["green"]
    blu_x, blu_y = light_positions["blue"]
    draw_label(canvas, "Red LED",   (red_x, red_y - 60), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Green LED", (grn_x + 65, grn_y), SCALE, LABEL_FONT_BASE)
    draw_label(canvas, "Blue LED",  (blu_x, blu_y + 60), SCALE, LABEL_FONT_BASE)

    cropped = crop_to_content(canvas, margin=MARGIN_PX * SCALE)
    save_on_white(cropped, OUTPUT)
    print(f"wrote {OUTPUT}  ({cropped.width}×{cropped.height})")


if __name__ == "__main__":
    main()
