# Plan — Image/screenshot upload for the chatbot

Status: drafted 2026-05-28, not started.

Feature: let students attach screenshots (of their robot code, robot behavior, or error messages) to chatbot turns. Currently the chatbot is text-only.

---

## Decisions already made

- **Upload UX:** built into the chat input bar via `st.chat_input(accept_file="multiple", file_type=["png", "jpg", "jpeg", "webp"])`. (Streamlit ≥ 1.42 required; project venv is on 1.55, so fine.)
- **Image lifetime in conversation history:** single turn only. Image is sent on the turn it's uploaded; subsequent turns reference it by a short text marker (e.g. `📎 screenshot.png`) so the LLM does not get re-billed for stale image tokens. Lock-in: model can't "look again" at the screenshot multiple turns later.
- **Persistence:** new Postgres `attachments` table with BYTEA bytes, FK to `interactions.id`. At expected scale (≤ ~500 images × ~500 KB ≈ 250 MB) the DB inflation is fine, and we keep a single backup story.
- **Moderation:** text-only moderation continues to run on the caption text. Image bypasses moderation. Consistent with the existing fail-open stance documented in `readme.md`; image moderation is overkill for a supervised, logged-in classroom.

## Verified facts (don't re-research)

- **Claude Sonnet 4.6 supports vision** via image content blocks. We use base64-inline rather than Anthropic Files API because images are single-turn (no reuse benefit; saves one round trip).
- **Mistral Agents API supports vision** via the Conversations endpoint. Verified from `mistralai` SDK source: `MessageInputContentChunks` is a `Union[TextChunk, ImageURLChunk, DocumentURLChunk, ThinkChunk, ToolFileChunk]`. Library/RAG attachment is unaffected.
- **The BmE Mistral Agent is configured with `mistral-medium-latest`** (= Mistral Medium 3.1), which is vision-capable. No console change needed.
- **Anthropic image token formula:** `tokens ≈ (width × height) / 750`, auto-downscaled above 1.15 MP / 1568 px. Effective upper bound ~1,500 input tokens per image.
- **Cost estimate:** ~$0.0045 per single-turn image at $3 / M input tokens. Full study (24 students × 4 sessions × ~3 images) ≈ $2–5 in image-only cost. Dominated by RAG-doc re-attachment, not images.

## Implementation steps

Work in this order. One feature commit covers 1–7 since the schema is useless without the wrappers and the wrappers are useless without the UI.

### 1. Postgres schema — new `attachments` table

`shared_lib/postgres_logger.py` — add to `_ensure_schema()`:

```sql
CREATE TABLE IF NOT EXISTS attachments (
    id BIGSERIAL PRIMARY KEY,
    interaction_id BIGINT REFERENCES interactions(id) ON DELETE CASCADE,
    filename TEXT,
    mime TEXT,
    bytes BYTEA,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Modify `log_interaction()`:
- `INSERT ... RETURNING id` so we have the row id.
- Add optional parameter `attachments: list[tuple[str, str, bytes]] | None = None` (filename, mime, bytes).
- Insert one row per attachment in the same transaction.

### 2. Image pre-processing helper

New file `agent/image_utils.py`:
- `prepare_uploaded_image(uploaded_file) -> (filename, mime, bytes, base64_str)`.
- Validate: size ≤ 5 MB, mime in `{image/png, image/jpeg, image/webp}`.
- Auto-downscale above 1568 px on either axis using Pillow (transitive dep via Streamlit).
- Return both the raw bytes (for DB) and the base64 string (for the LLM payload).

### 3. Anthropic backend wrapper

`agent/anthropic_lib/conversation_management.py`:
- `_build_messages(history, user_message, images=None)`: when `images` is given, insert image blocks into the new user message's content list, between the doc blocks and the trailing text block. Each block:
  ```python
  {"type": "image",
   "source": {"type": "base64", "media_type": mime, "data": b64}}
  ```
- `send_message(history, user_message, api_key, images=None)`: thread the parameter through.

### 4. Mistral backend wrapper

`agent/mistral_lib/conversation_management.py`:
- `send_message_to_agent(message, ..., images=None)`: when `images` is given, replace string `content` with the typed-chunks list:
  ```python
  inputs = [{
      "role": "user", "type": "message.input", "object": "entry",
      "content": [
          {"type": "text", "text": message},
          *[{"type": "image_url",
             "image_url": {"url": f"data:{mime};base64,{b64}"}}
            for (_, mime, _, b64) in images],
      ],
  }]
  ```

### 5. Chat page wiring

`agent/pages/1_Chat.py`:
- Change `st.chat_input(...)` to accept files (see Decisions).
- Return is now an object with `.text` and `.files`.
- For each uploaded file, call `prepare_uploaded_image()`, then pass `images=[...]` to whichever backend is active.
- **History rule (single-turn):** in `st.session_state[SESSION_MESSAGES]`, store the user turn as plain text plus a marker (`📎 screenshot.png`). Do **not** persist the base64 image blocks in session state — they only exist on the turn they're sent.
- When re-rendering a past user turn that had attachments, show the filename badge. (Cheap version: just the filename. Nicer version: thumbnail by reading bytes back from the `attachments` table — defer this to a follow-up if needed.)
- After backend response, pass `attachments=[(filename, mime, bytes), ...]` to `log_interaction()`.

### 6. Moderation

No code change, but add a one-line comment near the moderation call noting that image content bypasses the text moderator by design (fail-open stance, see `readme.md`).

### 7. Documentation

- `readme.md` chat-page section: one line mentioning screenshot support + 5 MB / png-jpeg-webp limits.
- `HANDOFF.md` "What's in the repo now" → add image-upload support to the chatbot bullet.

## Out of scope (call out before starting if you want them in)

- Image moderation (text bypass is accepted per existing threat model).
- Anthropic Files API path for images (only matters if we change the single-turn rule).
- Multi-turn image recall (locked out by the single-turn decision).
- Pre-flight `client.beta.agents.retrieve()` check for the Mistral agent's model — unnecessary while `mistral-medium-latest` is configured.

## Open question to resolve at pickup

**Both backends in one commit, or Anthropic first?** Plan as written assumes both at once. The asymmetric alternative (Anthropic first, Mistral later) ships faster but introduces a between-backends capability split that's a confound for the study's chatbot effect. Re-read the trade-off discussion before starting; if uncertain, default to both-at-once since the per-backend code is only ~30 lines each.

## References

- [Mistral Conversations vision](https://docs.mistral.ai/studio-api/conversations/vision)
- [Mistral Agents & Conversations API](https://docs.mistral.ai/studio-api/agents/agents-api)
- [Mistral document library connector](https://docs.mistral.ai/agents/tools/built-in/document_library)
- Anthropic vision: image token formula and base64/Files content-block shapes — covered in the Anthropic SDK docs; current repo already uses the same content-block pattern for RAG documents in `agent/anthropic_lib/file_management.py`.
- Mistral SDK schema verified from `mistralai` package source: `messageinputcontentchunks.py`, `imageurlchunk.py`, `conversationinputs.py`.

## Relevant files

| Area | File |
|---|---|
| Chat UI | `agent/pages/1_Chat.py` |
| Anthropic wrapper | `agent/anthropic_lib/conversation_management.py` |
| Anthropic doc-block helper (pattern reference) | `agent/anthropic_lib/file_management.py` |
| Mistral wrapper | `agent/mistral_lib/conversation_management.py` |
| Moderation | `agent/mistral_lib/moderation.py` |
| Postgres logging | `shared_lib/postgres_logger.py` |
| New: image helper | `agent/image_utils.py` |
