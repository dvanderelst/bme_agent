"""
Conversation management module for Anthropic Claude.
Sends messages with full conversation history and BME document context.

Unlike Mistral's server-side conversation API, Anthropic is stateless —
the full message history is sent with every request.

Documents from the file registry are attached to each new user message
as content blocks, giving the model access to BME reference material.
"""

import os
import logging
from typing import Optional

import anthropic

from anthropic_lib.config import get as anthropic_config
from anthropic_lib.file_management import document_block, image_block
from anthropic_lib.file_registry import load as load_registry
from shared_lib.config_manager import config

files_beta = "files-api-2025-04-14"


def _load_system_prompt() -> Optional[str]:
    """Load system prompt from the instructions file specified in config."""
    filename = anthropic_config("instructions")
    if not filename:
        return None

    instructions_dir = config.get("default_instructions_dir") or os.path.join("agent_files", "instructions")
    path = os.path.join(instructions_dir, filename)

    if not os.path.isfile(path):
        logging.warning(f"Instructions file not found: {path}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _build_document_blocks() -> list:
    """Build document content blocks for all files in the registry.

    Each block carries the title and description from the manifest so the
    model can tell the documents apart and pick the right one — without
    those, multiple unlabeled blobs tend to get glossed over.
    """
    registry = load_registry()
    if not registry:
        logging.warning("File registry is empty — no documents will be attached. Run script_configure_agents.py first.")
        return []
    return [
        document_block(meta["file_id"], title=meta["title"], context=meta["description"])
        for meta in registry.values()
    ]


def _build_image_blocks(images: Optional[list]) -> list:
    """Build base64 image content blocks for the new user message.

    ``images`` is a list of ``(filename, mime, raw_bytes, b64)`` tuples as
    produced by ``image_utils.prepare_uploaded_image``. We inline the base64
    rather than using the Files API: screenshots are single-turn, so there's
    no reuse to amortise an upload round trip against.
    """
    if not images:
        return []
    return [image_block(media_type=mime, data=b64) for (_, mime, _, b64) in images]


def _build_messages(history: list, user_message: str, images: Optional[list] = None) -> list:
    """
    Construct the full messages list for the API call.

    Historical messages are sent as plain text. The new user message has
    document blocks prepended — Anthropic's guidance is to place documents
    before the user's text so the model treats them as primary source
    material rather than appendices to skim after answering. Any uploaded
    images sit between the docs and the trailing text block.

    Images are single-turn: callers must not include them in ``history``, so
    past turns replay as text only and stale image tokens are never re-billed.
    """
    messages = [{"role": m["role"], "content": m["content"]} for m in history]

    doc_blocks = _build_document_blocks()
    image_blocks = _build_image_blocks(images)
    new_message_content = (
        doc_blocks + image_blocks + [{"type": "text", "text": user_message}]
    )

    messages.append({"role": "user", "content": new_message_content})
    return messages


def send_message(
    history: list,
    user_message: str,
    api_key: Optional[str] = None,
    images: Optional[list] = None,
) -> dict:
    """
    Send a message to Claude with full conversation history and document context.

    Args:
        history:      Previous conversation turns [{role, content}, ...]
                      as stored in st.session_state.messages.
        user_message: The new user message to send.
        api_key:      Anthropic API key. Falls back to config.get("anthropic_key").
        images:       Optional list of (filename, mime, raw_bytes, b64) tuples
                      to attach to this turn as inline image blocks. Single-turn
                      only — not carried into ``history``.

    Returns:
        dict with:
            assistant_response  — the model's reply as a string
            user_message        — the original user message
    """
    api_key = api_key or config.get("anthropic_key")
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = _load_system_prompt()
    messages = _build_messages(history, user_message, images=images)

    params = {
        "model":      anthropic_config("model"),
        "max_tokens": anthropic_config("max_tokens"),
        "messages":   messages,
        "betas":      [files_beta],
    }
    if system_prompt:
        params["system"] = system_prompt

    response = client.beta.messages.create(**params)

    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    return {
        "assistant_response": assistant_text,
        "user_message": user_message,
        # Surfaced so the chat UI can flag truncation. Anthropic returns
        # "end_turn" on a normal completion and "max_tokens" when the cap
        # was hit; "stop_sequence", "tool_use", etc. are also possible.
        "stop_reason": getattr(response, "stop_reason", None),
    }
