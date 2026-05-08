"""Shared rendering primitives for the kinesis/taxis question images.

Loads SVG assets from `assets/`, rasterizes via cairosvg, composes them onto a
canvas with Pillow. Native asset orientation is north (up); positive rotation
is CCW from north (PIL convention).

Coordinates are in *base pixels* — pre-SCALE units. Everything you specify in
a scene (positions, sprite heights) is multiplied by SCALE at render time.

All question images render onto a single standard canvas size so the
downstream interface can lay them out uniformly. The canvas holds up to
three panels side-by-side; scenes with fewer panels center their panels
on the same canvas. Each panel always carries a border and reserves a
header strip (which may be left empty).
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Standard canvas geometry, in base pixels (pre-SCALE).
PANEL_W_BASE = 460
PANEL_H_BASE = 460
GAP_BASE = 30
HEADER_H_BASE = 60
BORDER_W_BASE = 2
MAX_PANELS = 3
HEADER_FONT_BASE = 14

CANVAS_W_BASE = MAX_PANELS * PANEL_W_BASE + (MAX_PANELS - 1) * GAP_BASE
CANVAS_H_BASE = HEADER_H_BASE + PANEL_H_BASE


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


def make_canvas(scale: int) -> Image.Image:
    """Create a transparent RGBA canvas at the standard size × scale."""
    return Image.new(
        "RGBA",
        (CANVAS_W_BASE * scale, CANVAS_H_BASE * scale),
        (0, 0, 0, 0),
    )


def panel_left(n_panels: int, panel_index: int) -> int:
    """Return the base-pixel x of the left edge of panel `panel_index` of
    `n_panels`, centered horizontally on the standard canvas."""
    if not 1 <= n_panels <= MAX_PANELS:
        raise ValueError(f"n_panels must be 1..{MAX_PANELS}, got {n_panels}")
    total_w = n_panels * PANEL_W_BASE + (n_panels - 1) * GAP_BASE
    start_x = (CANVAS_W_BASE - total_w) // 2
    return start_x + panel_index * (PANEL_W_BASE + GAP_BASE)


def draw_panel_frame(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    panel_x: int,
    scale: int,
    header_text: str | None = None,
) -> None:
    """Draw the standard panel border at `panel_x`, and optionally a
    centered header text in the header strip above it."""
    draw.rectangle(
        [
            panel_x * scale,
            HEADER_H_BASE * scale,
            (panel_x + PANEL_W_BASE) * scale,
            (HEADER_H_BASE + PANEL_H_BASE) * scale,
        ],
        outline=(0, 0, 0, 255),
        width=BORDER_W_BASE * scale,
    )
    if header_text:
        draw_label(
            canvas,
            header_text,
            (panel_x + PANEL_W_BASE // 2, HEADER_H_BASE // 2),
            scale,
            HEADER_FONT_BASE,
        )


def speaker_rotation_facing_robot(angle_from_robot_deg: float) -> float:
    """Given the speaker's compass-style angle from the robot (0° = north of
    robot, positive = clockwise), return the PIL rotation that makes the
    speaker face the robot.

    Derivation: a speaker at compass angle θ from the robot needs to face
    compass (180° + θ) — the reverse direction. Compass is CW; PIL rotation is
    CCW from native north. So PIL rotation = -(180° + θ).
    """
    return -(180 + angle_from_robot_deg)
