"""
Image pre-processing for student-uploaded screenshots.

Students can attach a screenshot (robot code, robot behaviour, or an error
message) to a chat turn. This module turns a Streamlit ``UploadedFile`` into
the two representations the rest of the app needs:

    * raw bytes  — persisted to the Postgres ``attachments`` table.
    * base64 str — inlined into the LLM request as an image content block.

Images are single-turn: they are sent only on the turn they are uploaded and
are never replayed in later history, so we go base64-inline rather than via a
file-upload API (no reuse benefit, one fewer round trip).
"""

import base64
import io
from typing import Tuple

from PIL import Image

# Hard cap on the uploaded file size. Screenshots are well under this; the
# limit is a guard against someone attaching a huge image (cost + memory).
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

# MIME types we accept. Mirrors the file_type filter on st.chat_input and the
# formats both Claude and Mistral vision accept.
ALLOWED_MIMES = {"image/png", "image/jpeg", "image/webp"}

# Anthropic auto-downscales above ~1568 px on the long edge anyway; doing it
# ourselves keeps the base64 payload (and the DB blob) small and makes the
# token cost predictable. Mistral benefits equally.
MAX_DIMENSION_PX = 1568


class ImageValidationError(ValueError):
    """Raised when an uploaded file fails a size or type check."""


def prepare_uploaded_image(uploaded_file) -> Tuple[str, str, bytes, str]:
    """Validate and normalise a single Streamlit-uploaded image.

    Args:
        uploaded_file: a Streamlit ``UploadedFile`` (has ``.name``, ``.type``,
            and ``.getvalue()``).

    Returns:
        ``(filename, mime, raw_bytes, base64_str)`` where ``raw_bytes`` is the
        (possibly downscaled) image for DB storage and ``base64_str`` is the
        same bytes base64-encoded for the LLM payload.

    Raises:
        ImageValidationError: if the file is too large or not an accepted type.
    """
    filename = getattr(uploaded_file, "name", "upload")
    mime = getattr(uploaded_file, "type", "") or ""
    data = uploaded_file.getvalue()

    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageValidationError(
            f"'{filename}' is {len(data) // (1024 * 1024)} MB; the limit is "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )
    if mime not in ALLOWED_MIMES:
        raise ImageValidationError(
            f"'{filename}' has unsupported type '{mime or 'unknown'}'. "
            "Use PNG, JPEG, or WebP."
        )

    data, mime = _maybe_downscale(data, mime)
    b64 = base64.standard_b64encode(data).decode("ascii")
    return filename, mime, data, b64


def _maybe_downscale(data: bytes, mime: str) -> Tuple[bytes, str]:
    """Downscale the image if its longest edge exceeds MAX_DIMENSION_PX.

    Returns the (possibly re-encoded) bytes and the resulting MIME type. If
    the image is already small enough, the original bytes/MIME are returned
    untouched so we don't needlessly re-encode (and risk quality loss). On any
    Pillow error we fall back to the original bytes — a slightly oversized
    image is still usable, and Anthropic downscales server-side anyway.
    """
    try:
        with Image.open(io.BytesIO(data)) as img:
            longest = max(img.size)
            if longest <= MAX_DIMENSION_PX:
                return data, mime

            scale = MAX_DIMENSION_PX / longest
            new_size = (round(img.width * scale), round(img.height * scale))
            resized = img.resize(new_size, Image.LANCZOS)

            # Re-encode in a format that preserves the original where it
            # matters. PNG/WebP keep transparency; everything else → JPEG.
            out = io.BytesIO()
            if mime == "image/png":
                resized.save(out, format="PNG", optimize=True)
                return out.getvalue(), "image/png"
            if mime == "image/webp":
                resized.save(out, format="WEBP")
                return out.getvalue(), "image/webp"
            resized.convert("RGB").save(out, format="JPEG", quality=85)
            return out.getvalue(), "image/jpeg"
    except Exception:
        return data, mime
