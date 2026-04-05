# BME Agent — API Library Documentation

This document describes the project's Mistral and Anthropic API wrappers.

---

## Project Structure

```
mistral_lib/        Mistral AI — conversations, agents, libraries, moderation
anthropic_lib/      Anthropic Claude — conversations, file management
shared_lib/         Shared utilities — config, logging, Supabase
```

---

## mistral_lib

### Configuration — `mistral_lib/config.toml`

Non-secret Mistral settings. Edit this file to change moderation behaviour.

| Key | Default | Description |
|-----|---------|-------------|
| `moderation_model` | `mistral-moderation-2411` | Moderation classifier model. Switch to `mistral-moderation-2603` for jailbreaking detection when available. |

---

### `conversation_management.py`

Sends messages to a Mistral agent and manages server-side conversation state.

Unlike Anthropic, Mistral manages conversation history on the server. Only the new message is sent each turn; history is referenced via `conversation_id`.

#### `send_message_to_agent(message, agent_id, conversation_id, display, debug)`

| Argument | Required | Description |
|----------|----------|-------------|
| `message` | yes | The user message to send |
| `agent_id` | yes | Mistral agent ID (from secrets) |
| `conversation_id` | no | Pass `None` to start a new conversation, or an existing ID to continue |
| `display` | no | Print formatted output to console (default: `True`) |
| `debug` | no | Log full request/response detail (default: `False`) |

**Returns** `dict`:
```python
{
    "conversation_id":       str,   # persist this to continue the conversation
    "agent_id":              str,
    "user_message":          str,
    "assistant_response":    str,
    "responding_agent_ids":  list,
    "created_at":            str,
    "updated_at":            str,
}
```

---

### `moderation.py`

Classifies user messages using the Mistral moderation classifier before they reach the main agent.

#### Active categories

Controlled by `active_categories` at the top of the module. Categories not in this set are ignored when computing `passed`. All scores are still returned regardless.

Currently enabled: `sexual`, `hate_and_discrimination`, `violence_and_threats`, `dangerous_and_criminal_content`, `selfharm`, `pii`

Currently disabled (commented out): `health` (too broad for BME education), `financial`, `law`, `jailbreaking` (requires `mistral-moderation-2603`)

#### `moderate(message)`

Runs a single message through the classifier.

**Returns** `ModerationResult`:
```python
ModerationResult(
    passed=True/False,
    flagged_categories=["pii", "violence_and_threats"],  # empty list if passed
    category_scores={"sexual": 0.0001, "pii": 0.96, ...},
    categories={"sexual": False, "pii": True, ...},
)
```

#### `moderate_batch(messages)`

Runs a list of messages in a single API call. Returns a list of `ModerationResult` in the same order.

---

### `agent_management.py`

Manages Mistral agent configuration. Used by `script_configure_mistral.py`.

| Function | Description |
|----------|-------------|
| `agent_instructions(agent_id, new_instructions)` | Get or update agent instructions. Pass a filename to load from `agent_files/instructions/` |
| `set_agent_description(agent_id, description)` | Set the agent's description string |
| `assign_library_to_agent(agent_id, library_id)` | Attach a document library to an agent |
| `unassign_all_libraries_from_agent(agent_id)` | Remove all libraries from an agent |

---

### `library_management.py`

Manages Mistral document libraries. Used by `script_configure_mistral.py` and `script_manage_mistral_libraries.py`.

| Function | Description |
|----------|-------------|
| `create_library(name, description)` | Create a new library |
| `list_libraries()` | List all libraries in the workspace |
| `get_library(library_id)` | Get metadata for a specific library |
| `delete_library(library_id)` | Delete a library and all its contents |
| `upload_document(file_path, library_id)` | Upload a document. Bare filenames look in `agent_files/documents/` |
| `upload_document_and_wait(library_id, file_path)` | Upload and poll until processing completes |
| `list_library_documents(library_id)` | List all documents in a library |
| `remove_all_documents_from_library(library_id)` | Delete all documents from a library |

---

## anthropic_lib

### Configuration — `anthropic_lib/config.toml`

Non-secret Anthropic settings.

| Key | Default | Description |
|-----|---------|-------------|
| `model` | `claude-sonnet-4-6` | Claude model to use |
| `max_tokens` | `1024` | Maximum tokens in the response |
| `instructions` | `bme_agent_instructions.md` | Instructions filename, loaded from `agent_files/instructions/` |

---

### `conversation_management.py`

Sends messages to Claude with full conversation history and BME document context.

**Key difference from Mistral:** Anthropic's API is stateless. The full conversation history must be sent with every request. History is stored in `st.session_state.messages` and passed in by the caller.

BME reference documents (from the file registry) are attached as content blocks to each new user message, giving the model access to the knowledge base on every turn.

#### `send_message(history, user_message)`

| Argument | Description |
|----------|-------------|
| `history` | Previous conversation turns as `[{"role": ..., "content": ...}, ...]`. Pass `st.session_state.messages` directly. |
| `user_message` | The new message from the user |

**Returns** `dict`:
```python
{
    "assistant_response": str,
    "user_message":       str,
}
```

Note: no `conversation_id` is returned since Anthropic does not maintain server-side state.

---

### `file_management.py`

Manages files in the Anthropic Files API workspace. Uses beta: `files-api-2025-04-14`.

#### Supported file types

| Extension | MIME type | Content block |
|-----------|-----------|---------------|
| `.pdf` | `application/pdf` | `document` |
| `.txt`, `.md` | `text/plain` | `document` |
| `.jpg`, `.jpeg` | `image/jpeg` | `image` |
| `.png` | `image/png` | `image` |
| `.gif` | `image/gif` | `image` |
| `.webp` | `image/webp` | `image` |

Limits: 500 MB per file, 500 GB per organisation. File operations are free; tokens are charged when files are used in messages.

#### CRUD functions

| Function | Description |
|----------|-------------|
| `upload_file(file_path)` | Upload a file, returns `file_id`. Bare filenames look in `agent_files/documents/` |
| `list_files()` | List all files in the workspace |
| `get_file(file_id)` | Get metadata for a specific file |
| `delete_file(file_id)` | Delete a file, returns `True` |

#### Content block helpers

Used when building message payloads manually.

| Function | Description |
|----------|-------------|
| `document_block(file_id, title, context, citations)` | Build a `document` content block for PDFs and text files |
| `image_block(file_id)` | Build an `image` content block |

---

### `file_registry.py`

Maps document filenames to their current Anthropic `file_id`s. Generated by `script_configure_anthropic.py` — do not edit by hand. Stored in `anthropic_lib/file_registry.json` (git-ignored).

| Function | Description |
|----------|-------------|
| `save(file_map)` | Write a `{filename: file_id}` dict to the registry |
| `load()` | Return the full registry as a dict |
| `get_file_id(document_name)` | Look up a file_id by document name |
| `all_file_ids()` | Return all registered file_ids as a list |

---

## shared_lib

| Module | Description |
|--------|-------------|
| `config_manager.py` | Loads `secrets.toml` and environment variables. Use `config.get("key")` |
| `logger.py` | Centralised logging wrapper around Python's `logging` module |
| `output_logging.py` | Logs script output to markdown files in `logs/` |
| `baserow_logger.py` | Logs conversation turns to the Baserow database table |

---

## Secrets — `.streamlit/secrets.toml`

| Key | Description |
|-----|-------------|
| `mistral_key` | Mistral API key |
| `anthropic_key` | Anthropic API key |
| `bme_agent` | Mistral agent ID for the BME specialist |
| `bme_agent_library` | Mistral library ID for BME documents |
| `app_password` | Password students enter to access the chat |
| `baserow_api_url` | Baserow API URL with table ID |
| `baserow_api_token` | Baserow database token |

---

## Scripts

| Script | Description |
|--------|-------------|
| `script_configure_mistral.py` | Configure the Mistral BME agent — set instructions, upload documents to library |
| `script_configure_anthropic.py` | Upload BME documents to Anthropic Files API, write `file_registry.json` |
| `script_manage_mistral_libraries.py` | Utility for managing Mistral document libraries |
| `script_moderation_testing.py` | Test the moderation classifier against a set of sample prompts |
