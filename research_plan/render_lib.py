"""Shared rendering primitives for the kinesis/taxis question images.

Loads SVG assets from `assets/`, rasterizes via cairosvg, composes them onto a
canvas with Pillow. Native asset orientation is north (up); positive rotation
is CCW from north (PIL convention).

Coordinates are in *base pixels* — pre-SCALE units. Everything you specify in
a scene (positions, sprite heights) is multiplied by SCALE at render time.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_svg(name: str, height_px: int) -> Image.Image:
    png_bytes = cairosvg.svg2png(
        url=str(ASSETS / f"{name}.svg"),
        output_height=height_px,
    )
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def paste_rotated(canvas: Image.Image, sprite: Image.Image, center: tuple[int, int], rotation_deg: float) -> None:
    """Rotate `sprite` CCW by `rotation_deg` and paste it centered at `center`.
    Asset is drawn facing north; angle is degrees CCW from north."""
    rotated = sprite.rotate(rotation_deg, expand=True, resample=Image.BICUBIC)
    cx, cy = center
    w, h = rotated.size
    canvas.paste(rotated, (cx - w // 2, cy - h // 2), mask=rotated)


def crop_to_content(image: Image.Image, margin: int) -> Image.Image:
    bbox = image.getbbox()
    if bbox is None:
        return image
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - margin)
    y0 = max(0, y0 - margin)
    x1 = min(image.width, x1 + margin)
    y1 = min(image.height, y1 + margin)
    return image.crop((x0, y0, x1, y1))


def save_on_white(image: Image.Image, output_path: Path) -> None:
    """Composite an RGBA image onto a white background and save as RGB PNG."""
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    background.convert("RGB").save(output_path)


def draw_label(
    canvas: Image.Image,
    text: str,
    center_base: tuple[int, int],
    scale: int,
    font_size_base: int = 22,
    color: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> None:
    """Draw `text` centered at the given base-pixel position. Font size is in
    base pixels and gets scaled at draw time. Falls back to PIL's bitmap font
    if DejaVuSans isn't available."""
    cx = center_base[0] * scale
    cy = center_base[1] * scale
    font_size = font_size_base * scale
    try:
        font = ImageFont.truetype(DEFAULT_FONT, size=font_size)
    except OSError:
        font = ImageFont.load_default()
    ImageDraw.Draw(canvas).text((cx, cy), text, fill=color, font=font, anchor="mm")


def speaker_rotation_facing_robot(angle_from_robot_deg: float) -> float:
    """Given the speaker's compass-style angle from the robot (0° = north of
    robot, positive = clockwise), return the PIL rotation that makes the
    speaker face the robot.

    Derivation: a speaker at compass angle θ from the robot needs to face
    compass (180° + θ) — the reverse direction. Compass is CW; PIL rotation is
    CCW from native north. So PIL rotation = -(180° + θ).
    """
    return -(180 + angle_from_robot_deg)
