# BME Agent

Streamlit chatbot for the Biology Meets Engineering course. Students log in with credentials from a roster you manage locally; the app forwards their questions to either Mistral or Anthropic and logs every interaction to Postgres.

```
streamlit run app.py
```
---

## FAQ

### How are documents handled by Mistral vs Anthropic?

Both backends are fed from the same source folder (`agent_files/documents/`) by the same script (`script_configure_agents.py`), which wipes the existing state on each run and re-uploads everything. Per-document metadata (title + description) lives in **`agent_files/documents/manifest.toml`** — a single source of truth that both backends consume. What happens at chat time differs:

- **Mistral** stores documents in a server-side *library* (`bme_agent_library`). The library is attached to the agent via a `document_library` tool. On each turn, the agent searches the library (RAG) and only pulls in relevant snippets — you don't pay tokens for documents the model doesn't consult. The manifest's per-doc descriptions are rolled up into a single library description (Mistral's SDK has no per-doc description hook), and each doc's title becomes its `document_name` on upload.
- **Anthropic** stores documents in the workspace-level Files API as individual `file_id`s. `anthropic_lib/file_registry.json` (tracked in git so production picks it up) maps filenames to `{file_id, title, description}`. `conversation_management._build_document_blocks()` attaches **every** registered file as a content block to **every** new user message, with title and context pulled from the manifest — the model sees the whole document set on each turn, with each doc clearly labelled. No search step, but token cost grows with the library.
  - Document blocks are placed **before** the user's text per Anthropic's guidance, so the model treats the docs as primary source material rather than appendices to skim after answering.
  - Only the file IDs go over the wire (a few hundred bytes); Anthropic resolves them server-side. But the model processes each file's full contents on every turn, so token cost scales with `document size × turn count` — the small request body does not reflect the actual cost.
  - Historical turns are sent as plain text only — document blocks are attached to the latest user message, not duplicated across history.

Practical implication: Anthropic is simpler (no relevance issues, model always has full context) but more expensive per turn as the document set grows. Mistral is cheaper at scale but answer quality depends on its search picking the right documents — which is why the rolled-up library description is important: it tells the agent what's in the library so it knows when to consult it.

### How do I change the model used by each backend?

The two backends work very differently:

- **Mistral**: We talk to a server-side *Agent* resource (the `bme_agent` ID in secrets). The agent owns its own model, instructions, libraries, tools, and description — all stored on Mistral's side. Change the model in Mistral's web console; it takes effect immediately, no redeploy. `script_configure_agents.py` only touches instructions and the library; the model selection lives entirely on the console.
- **Anthropic**: No agent abstraction in our usage — we call `client.beta.messages.create()` directly with `model` as a parameter. The model name comes from `anthropic_lib/config.toml` (currently `claude-sonnet-4-6`); the system prompt is loaded each call from `agent_files/instructions/bme_agent_instructions.md`. To swap models (e.g. Sonnet → Opus), edit `anthropic_lib/config.toml` and redeploy on Railway.

Anthropic does have a *Managed Agents* API that mirrors Mistral's server-side-agent setup, but we're not using it.

### How is API usage billed, and do my subscriptions cover it?

**No — the consumer subscriptions don't cover API usage.** Both Le Chat Pro (incl. student) and Claude Max are for the chat products (claude.ai, le chat, and Claude Code CLI when authenticated against Max). The API calls our app makes (`anthropic.Anthropic(...)`, `Mistral(...)`) are billed on **entirely separate developer-console accounts**. Per Mistral's help center: *"Le Chat Pro does not include API credits."* Same applies to Claude Max.

- **Anthropic API**: prepaid credits model (for accounts created on/after 2024-02-13). Buy in the Claude Console → Billing → "Buy credits". Credits expire 1 year from purchase, non-refundable. Optional auto-reload (minimum balance + top-up amount).
- **Mistral API**: pay-as-you-go per token by default; you can also pre-buy credits in la Plateforme console.
- **Mistral document library**: no monthly storage fee. You pay tokens at query time (when the agent retrieves snippets) plus a one-time upload/embedding cost.

Practical implication: every student message that hits either backend is real money out of the developer-console balance, independent of any subscription. The moderation step (cheap) up front is what keeps junk from hitting a billed agent call.

> *Last verified: 2026-05-02. Pricing and billing models change — re-check the linked help pages before assuming this is still current.*
>
> Sources: [Anthropic — How do I pay for my Claude API usage?](https://support.claude.com/en/articles/8977456-how-do-i-pay-for-my-claude-api-usage) · [Mistral pricing](https://mistral.ai/pricing) · [Mistral — Le Chat Pro vs API](https://help.mistral.ai/en/articles/347532-what-is-the-difference-between-le-chat-free-pro-team-and-enterprise) · [Mistral — Student discount](https://help.mistral.ai/en/articles/347553-as-a-student-am-i-eligible-for-a-discount-on-le-chat-pro)

---

## Project structure

```
app.py                                    Streamlit login page
pages/1_Chat.py                           Chat UI (post-login)
mistral_lib/                              Mistral — conversations, agents, libraries, moderation
anthropic_lib/                            Anthropic Claude — conversations, file management
shared_lib/                               Shared utilities — config, auth, logging, Postgres
agent_files/                              Documents and instructions uploaded to the agents
agent_files/documents/manifest.toml       Per-doc title + description; consumed by both backends
script_configure_students.py              Sync local students.ods → Railway Postgres
script_configure_agents.py                Configure both Mistral and Anthropic agents
script_chat.py                            Interactive REPL for probing either backend with diagnostics
students.ods                              Local student roster (gitignored — contains plaintext passwords)
```

---

## Authentication & students

### How login works

1. The student opens the app and sees a username + password form (`app.py`).
2. `shared_lib.auth.authenticate()` looks up the row in the `students` Postgres table and verifies the password with `bcrypt`.
3. On success the full row (minus `password_hash`) is stored in `st.session_state["student"]`. The chat page (`pages/1_Chat.py`) reads that dict to determine which backend to use and to tag every logged interaction with the student's username.
4. If the student exists but `enabled = false`, login is refused with a generic "no access" message.

Username matching is case-insensitive — usernames are lowercased on both write and lookup.

### Managing students

`students.ods` is the source of truth. To add, remove, or change students, edit the spreadsheet and run:

```
python script_configure_students.py            # syncs ./students.ods
python script_configure_students.py list       # show what's currently in the DB
```

Before destroying anything, the script prints the target host + database, the current row count, and the new row count, then prompts `Proceed? [y/N]`. Type anything other than `y` / `yes` to abort with no changes made — cheap insurance against ever pointing the script at the wrong database. The sync itself runs as a single transaction: if any step fails, the old data is unchanged.

(Running from PyCharm: make sure your run configuration uses an "emulated terminal" / interactive console so the prompt actually accepts input.)

### Spreadsheet schema

First row is headers. **Required columns** (the script refuses to run if any are missing):

| Column     | Type / values                          | Notes |
|------------|----------------------------------------|-------|
| `username` | text                                   | Lowercased on insert; PK |
| `password` | text                                   | Plaintext in the spreadsheet → bcrypt-hashed on insert |
| `enabled`  | `true/yes/1/y/t`, `false/no/0/n/f`, blank | Blank means enabled |
| `backend`  | `mistral` or `anthropic`               | Required, must be non-empty |

Any other columns you add (e.g. `full_name`, `challenge`, `cohort`) become `TEXT` columns on the table automatically. Columns present on the table but missing from the spreadsheet are dropped on the next sync (except the reserved system columns: `username`, `password_hash`, `enabled`, `backend`, `created_at`).

The full `student` dict is available in `st.session_state["student"]`, so any extra column you add becomes accessible app-wide without code changes.

### Backend selection

For regular students, there is no UI toggle. Each student is pinned to either `mistral` or `anthropic` via the spreadsheet's `backend` column. To change a student's backend, edit the cell and re-sync.

If a row in the `students` table ever ends up with a `backend` value outside `{"mistral", "anthropic"}` (e.g. via a hand-edited row, or as an intentional kill-switch), the chat page hard-stops with a generic *"Sorry, you can't use the chatbot at this moment"* message — it never silently routes to a default backend. The error cause is logged server-side for debugging.

Diagnostic users (see below) get a session-only backend override radio in the sidebar — useful for comparing the two backends on the same prompt without changing the DB.

### Diagnostic users

A student row with `diagnostics` set to `true` (or `yes` / `1` / `y` / `t`) gets an extra Streamlit sidebar on the chat page exposing:

- a **session-only backend override** (radio; defaults to the row's pinned `backend`, not persisted to the DB),
- the **last turn's request shape** — model, conversation_id, doc-block titles + file_ids + block order on Anthropic; agent_id and responding-agent ids on Mistral,
- the **full student row**.

The diagnostics flag is itself a regular spreadsheet column — not in `RESERVED_COLUMNS`, so it's added as a `TEXT` column the first time the configure script runs after you add it to `students.ods`. Set `true` for the test/staff accounts; leave blank for everyone else.

Logs of diagnostic sessions record the **effective** backend (i.e. whatever the radio was set to) in both the `interactions.llm` column and the `student_settings.backend` field of the JSONB snapshot, so a later analyst can tell what was actually used. The presence of `diagnostics: true` in the same snapshot signals that the row could have been overridden mid-session.

---

## Database tables (Postgres on Railway)

All three tables are auto-created / migrated on app startup by `shared_lib.postgres_logger.get_postgres_client()`.

### `students`
```
username       TEXT PRIMARY KEY
password_hash  TEXT NOT NULL
enabled        BOOLEAN NOT NULL DEFAULT TRUE
backend        TEXT
full_name      TEXT
challenge      TEXT
created_at     TIMESTAMPTZ DEFAULT NOW()
```

### `interactions`
One row per user/agent message exchange.
```
id               SERIAL PRIMARY KEY
timestamp        TIMESTAMPTZ DEFAULT NOW()
conversation_id  TEXT      -- "Not Applicable" for Anthropic (stateless)
user_id          TEXT      -- the student's username
user_message     TEXT
agent_response   TEXT
llm              TEXT      -- 'mistral' or 'anthropic' (effective backend)
student_settings JSONB     -- snapshot of the student row at log time
```

`student_settings` is a JSONB snapshot of the student row at the moment of the interaction — every column from the `students` table except `username` (already in `user_id`) and `created_at`. It guards against later student-table re-syncs (which `TRUNCATE` and rewrite) erasing the context of historical log entries: e.g., what `challenge` the student was on, whether `diagnostics` was enabled, etc.

### `feedback`
One row per thumbs-up / thumbs-down submission.
```
id               SERIAL PRIMARY KEY
timestamp        TIMESTAMPTZ DEFAULT NOW()
conversation_id  TEXT
user_id          TEXT
sentiment        SMALLINT  -- 1 = up, 0 = down
note             TEXT
student_settings JSONB     -- snapshot of the student row at log time
```

---

## mistral_lib

### Configuration — `mistral_lib/config.toml`

Non-secret Mistral settings.

| Key | Default | Description |
|-----|---------|-------------|
| `moderation_model` | `mistral-moderation-2411` | Moderation classifier model. Switch to `mistral-moderation-2603` for jailbreaking detection when available. |

### `conversation_management.py`

Sends messages to a Mistral agent and manages server-side conversation state. Unlike Anthropic, Mistral keeps history on the server — only the new message is sent each turn, referenced via `conversation_id`.

#### `send_message_to_agent(message, agent_id, conversation_id, display, debug)`

| Argument | Required | Description |
|----------|----------|-------------|
| `message` | yes | The user message to send |
| `agent_id` | yes | Mistral agent ID (from secrets) |
| `conversation_id` | no | `None` to start a new conversation, or an existing ID to continue |
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

### `moderation.py`

Classifies user messages using the Mistral moderation classifier before they reach the main agent. Fails closed: API errors block the message and surface a warning in the chat UI.

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

### `agent_management.py`

Manages Mistral agent configuration. Used by `script_configure_agents.py`.

| Function | Description |
|----------|-------------|
| `agent_instructions(agent_id, new_instructions)` | Get or update agent instructions. Pass a filename to load from `agent_files/instructions/` |
| `set_agent_description(agent_id, description)` | Set the agent's description string |
| `assign_library_to_agent(agent_id, library_id)` | Attach a document library to an agent |
| `unassign_all_libraries_from_agent(agent_id)` | Remove all libraries from an agent |

### `library_management.py`

Manages Mistral document libraries. Used by `script_configure_agents.py` and `script_manage_mistral_libraries.py`.

| Function | Description |
|----------|-------------|
| `create_library(name, description)` | Create a new library |
| `list_libraries()` | List all libraries in the workspace |
| `get_library(library_id)` | Get metadata for a specific library |
| `update_library_description(library_id, description)` | Update an existing library's description (used to push the rolled-up manifest overview) |
| `delete_library(library_id)` | Delete a library and all its contents |
| `upload_document(file_path, library_id, document_name)` | Upload a document. Bare filenames look in `agent_files/documents/` |
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

### `conversation_management.py`

Sends messages to Claude with full conversation history and BME document context.

**Key difference from Mistral:** Anthropic's API is stateless. The full conversation history must be sent with every request. History is stored in `st.session_state.messages` and passed in by the caller.

BME reference documents (from the file registry) are attached as content blocks to each new user message, giving the model access to the knowledge base on every turn. Each block carries the `title` and `context` from the manifest so the model can tell the documents apart and pick the right one. Blocks are placed **before** the user's text (per Anthropic's guidance for grounding), not after.

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

No `conversation_id` is returned since Anthropic does not maintain server-side state.

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

### `file_registry.py`

Maps document filenames to their current Anthropic `file_id` plus the title and description from `agent_files/documents/manifest.toml`. Generated by `script_configure_agents.py` — do not edit by hand. Stored in `anthropic_lib/file_registry.json` (tracked in git so production deploys carry the same file_ids the configure script wrote locally; commit and push the regenerated registry whenever you re-run the configure script).

Shape:
```json
{
  "robot_details.md": {
    "file_id":     "file_011...",
    "title":       "mBot Robot — Hardware, Setup, ...",
    "description": "Hardware specs (ports, sensors, motors), ..."
  },
  ...
}
```

| Function | Description |
|----------|-------------|
| `save(file_map)` | Write the document → metadata mapping to the registry |
| `load()` | Return the registry as a dict |

---

## shared_lib

| Module | Description |
|--------|-------------|
| `auth.py` | Students table DDL, bcrypt hashing, `authenticate(url, username, password)` |
| `postgres_logger.py` | Connection setup + `log_interaction()` / `log_feedback()`. Creates and migrates all three tables on startup |
| `config_manager.py` | Loads `secrets.toml` and environment variables. Use `config.get("key")` |
| `lib_config.py` | TOML config loader used by `mistral_lib` / `anthropic_lib` |
| `logger.py` | Centralised logging wrapper around Python's `logging` module |
| `output_logging.py` | Logs script output to markdown files in `logs/` |

---

## Secrets — `.streamlit/secrets.toml`

| Key | Description |
|-----|-------------|
| `mistral_key` | Mistral API key |
| `anthropic_key` | Anthropic API key |
| `bme_agent` | Mistral agent ID for the BME specialist |
| `bme_agent_library` | Mistral library ID for BME documents |
| `database_url` | Postgres connection URL (Railway-provided) |

The same keys can also be supplied as environment variables (Railway injects `DATABASE_URL` automatically).

---

## Scripts

| Script | Description |
|--------|-------------|
| `script_configure_students.py` | Sync the local `students.ods` roster to the Postgres `students` table |
| `script_configure_agents.py` | Configure both Mistral and Anthropic agents — read `manifest.toml`, set instructions, upload documents, write `file_registry.json`, and push the rolled-up library description to Mistral |
| `script_chat.py` | Interactive REPL for probing either backend with diagnostic output (doc blocks, file_ids, conversation_id, etc). Pick backend at startup with `a`/`m` aliases |
| `script_manage_mistral_libraries.py` | Utility for managing Mistral document libraries |
| `script_moderation_testing.py` | Test the moderation classifier against a set of sample prompts |
| `script_test_anthropic.py` | Non-interactive regression suite for the Anthropic conversation flow — API reachability, document grounding, multi-turn history |
