"""
File management module for Anthropic Files API.
Upload, list, retrieve, and delete files for use in Claude messages.

Beta: files-api-2025-04-14

Supported file types:
    PDF        — application/pdf   → use document_block()
    Plain text — text/plain        → use document_block()
    JPEG       — image/jpeg        → use image_block()
    PNG        — image/png         → use image_block()
    GIF        — image/gif         → use image_block()
    WebP       — image/webp        → use image_block()

Limits:
    Max file size : 500 MB
    Total storage : 500 GB per organisation

Note: uploaded files cannot be downloaded back. Only files created
by the code execution tool are downloadable.
"""

import mimetypes
import os
from typing import Optional

import anthropic

from shared_lib.config_manager import config

# ---------------------------------------------------------------------------
# MIME type map — inferred from file extension when not supplied explicitly
# ---------------------------------------------------------------------------
_mime_types = {
    ".pdf":  "application/pdf",
    ".txt":  "text/plain",
    ".md":   "text/plain",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}


def _client(api_key: Optional[str] = None) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key or config.get("anthropic_key"))


def _infer_mime(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in _mime_types:
        return _mime_types[ext]
    mime, _ = mimetypes.guess_type(file_path)
    return mime or "application/octet-stream"


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def upload_file(
    file_path: str,
    mime_type: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Upload a file and return its file_id.

    Args:
        file_path: Path to the file. Looks in agent_files/documents/ if only
                   a filename is given and the file isn't found at the path.
        mime_type: MIME type override. Inferred from extension if not provided.
        api_key:   Anthropic API key. Falls back to config.get("anthropic_key").

    Returns:
        file_id string, e.g. "file_011CNha8iCJcU1wXNR6q4V8w"
    """
    # Try default documents dir if bare filename given
    if not os.path.isfile(file_path):
        candidate = os.path.join("agent_files", "documents", file_path)
        if os.path.isfile(candidate):
            file_path = candidate

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    mime = mime_type or _infer_mime(file_path)
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        response = _client(api_key).beta.files.upload(
            file=(filename, f, mime),
        )
    return response.id


def list_files(api_key: Optional[str] = None) -> list:
    """
    List all files in the workspace.

    Returns:
        List of file metadata objects (id, filename, size, created_at, etc.)
    """
    response = _client(api_key).beta.files.list()
    return list(response.data) if hasattr(response, "data") else list(response)


def get_file(file_id: str, api_key: Optional[str] = None):
    """
    Retrieve metadata for a specific file.

    Returns:
        File metadata object.
    """
    return _client(api_key).beta.files.retrieve_metadata(file_id)


def delete_file(file_id: str, api_key: Optional[str] = None) -> bool:
    """
    Delete a file from the workspace.

    Returns:
        True if deletion was successful.
    """
    _client(api_key).beta.files.delete(file_id)
    return True


# ---------------------------------------------------------------------------
# Content block helpers — use these when building Messages requests
# ---------------------------------------------------------------------------

def document_block(
    file_id: str,
    title: Optional[str] = None,
    context: Optional[str] = None,
    citations: bool = False,
) -> dict:
    """
    Build a document content block for a Messages request.
    Use for PDF and plain text files.

    Args:
        file_id:   The uploaded file ID.
        title:     Optional document title shown to the model.
        context:   Optional context about the document.
        citations: Set True to enable inline citations in the response.

    Returns:
        dict ready to include in a messages content list.

    Example:
        >>> block = document_block("file_011CNha...", title="BME Lecture Notes")
        >>> response = client.beta.messages.create(
        ...     model="claude-sonnet-4-6",
        ...     messages=[{"role": "user", "content": [
        ...         {"type": "text", "text": "Summarise this."},
        ...         block,
        ...     ]}],
        ...     betas=["files-api-2025-04-14"],
        ... )
    """
    block = {
        "type": "document",
        "source": {"type": "file", "file_id": file_id},
    }
    if title:
        block["title"] = title
    if context:
        block["context"] = context
    if citations:
        block["citations"] = {"enabled": True}
    return block


def image_block(file_id: str) -> dict:
    """
    Build an image content block for a Messages request.
    Use for JPEG, PNG, GIF, and WebP files.

    Returns:
        dict ready to include in a messages content list.
    """
    return {
        "type": "image",
        "source": {"type": "file", "file_id": file_id},
    }
