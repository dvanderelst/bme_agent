import logging
import time

import streamlit as st

from mistral_lib import conversation_management as mistral_conversation
from mistral_lib.moderation import moderate
from anthropic_lib import conversation_management as anthropic_conversation
from anthropic_lib.config import get as anthropic_config
from anthropic_lib.file_management import validate_registry
from anthropic_lib.file_registry import load as load_registry
from image_utils import prepare_uploaded_image, ImageValidationError, UPLOAD_FILE_TYPES
from shared_lib.auth import lookup_student
from shared_lib.postgres_logger import log_interaction, log_feedback
from shared_lib.streamlit_helpers import setup_postgres


@st.cache_resource
def _validate_registry_cached() -> list:
    """Run validate_registry() once per app process (it's ~N API calls).
    The result is cached for the process lifetime; restart the deploy if a
    file is re-uploaded and the cache needs to invalidate."""
    return validate_registry()

# Wait between the failed first moderation call and the retry. Long enough
# for a transient network blip to resolve, short enough that the student
# barely notices.
MODERATION_RETRY_DELAY_SECONDS = 1.0

SESSION_AUTHENTICATED = "authenticated"
SESSION_MESSAGES = "messages"
SESSION_CONVERSATION_ID = "conversation_id"
SESSION_STUDENT = "student"
SESSION_STUDENT_ID = "student_id"
SESSION_FEEDBACK_KEY = "feedback_key"
SESSION_LAST_DIAG = "last_diagnostic"
SESSION_LAST_BACKEND = "last_backend"


def _truthy(value) -> bool:
    """Parse the diagnostics flag from the students table. Extra columns
    are stored as TEXT, so the value arrives as 'true', '1', '' or None."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "yes", "1", "y", "t")


# Read student state early so the CSS block below knows whether to keep
# the sidebar visible. Diagnostic users get the sidebar; everyone else
# stays in the chat-only view.
student = st.session_state.get(SESSION_STUDENT) or {}
diagnostics_enabled = _truthy(student.get("diagnostics"))
_sidebar_hide_rule = "" if diagnostics_enabled else "[data-testid='stSidebar'] {display: none;}"

st.markdown("<style>\n" + _sidebar_hide_rule + """
/* Make chat conversation more compact */
.stChatMessage {margin-bottom: 0 !important; margin-top: 0 !important; padding-bottom: 0 !important; padding-top: 0 !important;}
[data-testid="chatAvatarIcon"] {margin-bottom: 0 !important;}
.block-container {padding-top: 0.1rem !important; padding-bottom: 0.1rem !important;}
.element-container {margin-bottom: 0 !important;}
.stMarkdown {margin-bottom: 0 !important;}

/* Dark theme styling */
body {background-color: #1e1e1e; color: #f0f0f0;}
.stApp {background-color: #1e1e1e;}
.stChatMessage {background-color: #2d2d2d;}
.stChatMessage[data-testid="user"] {background-color: #3a3a3a;}
.stChatMessage[data-testid="assistant"] {background-color: #2d2d2d;}
[data-testid="stChatInput"] {background-color: #2d2d2d; border: 1px solid #444;}
[data-testid="stChatInput"] textarea {color: #f0f0f0;}

/* Add spacing for title to account for header */
.stTitle {margin-top: 4rem !important;}
.block-container {margin-top: 2rem !important;}
</style>
""", unsafe_allow_html=True)

# Redirect to login if not authenticated
if not st.session_state.get(SESSION_AUTHENTICATED):
    st.switch_page("app.py")

# Configuration - try Streamlit secrets first, fallback to ConfigManager
try:
    agent_id = st.secrets["BME_AGENT"]
    database_url = st.secrets["DATABASE_URL"]
except (AttributeError, KeyError):
    from shared_lib.config_manager import config
    agent_id = config.get("bme_agent")
    database_url = config.get("database_url")

try:
    db_config = setup_postgres(database_url)
except Exception as e:
    logging.error("Database setup failed on chat page: %s", e)
    st.error("The chatbot is temporarily unavailable. Please try again later.")
    st.stop()

# Re-verify the student is still active. session_state.authenticated is set
# at login and otherwise never re-checked, so an instructor disabling a
# student mid-session would only take effect on their next login without
# this guard. Also picks up other column changes (e.g. backend, diagnostics)
# so they propagate immediately.
fresh_student = lookup_student(db_config, st.session_state.get(SESSION_STUDENT_ID))
if fresh_student is None or not fresh_student.get("enabled", True):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.error("Your account is no longer active. Please contact an instructor.")
    st.stop()
st.session_state[SESSION_STUDENT] = fresh_student
# Refresh locals derived from the early read at the top of the file. The
# CSS up there used possibly-stale values for one render; from here on we
# work with the fresh row.
student = fresh_student
diagnostics_enabled = _truthy(student.get("diagnostics"))

# Validate required config
if not agent_id:
    st.error("Missing required configuration: bme_agent. Check your secrets.toml.")
    st.stop()

def _trim_history_for_anthropic(messages: list, max_count: int) -> list:
    """Keep at most max_count messages from the tail of the list, then drop
    any leading assistant messages so the first one is a user role.

    Anthropic requires the conversation to start with a user message and
    alternate from there; a naive tail-slice could land on an assistant
    message if the list length is even.
    """
    if len(messages) <= max_count:
        return messages
    trimmed = messages[-max_count:]
    while trimmed and trimmed[0].get("role") != "user":
        trimmed = trimmed[1:]
    return trimmed


def run_moderation(message: str) -> tuple[bool, list]:
    """Run message through the Mistral moderation classifier.

    Returns (passed, flagged_categories). Retries once on API error; if the
    retry also fails, fails open (returns passed=True) so a transient blip
    doesn't dead-end a student's conversation. The LLM has its own
    training-level guardrails as a second line of defense — see readme.md.
    """
    for attempt in (1, 2):
        try:
            result = moderate(message)
            return result.passed, result.flagged_categories
        except Exception as e:
            if attempt == 1:
                logging.warning("Moderation API call failed (retrying once): %s", e)
                time.sleep(MODERATION_RETRY_DELAY_SECONDS)
            else:
                logging.warning(
                    "Moderation API call failed after retry; failing open: %s", e
                )
    return True, []


def _log_dropped_turn(student_id, content: str, prepared: list) -> None:
    """Durably record a turn that failed to log to the database.

    The interaction write is atomic (text + image rows commit together or not
    at all), so a logging failure drops the *whole* turn — leaving only an
    ephemeral st.warning the student sees and the researcher never does. The
    LLM has already answered by this point, so the exchange happened but would
    otherwise vanish from the record. Emit the message text (which already
    carries the 📎 attachment markers) and the attachment filenames at error
    level so the turn is reconstructable from the server logs.
    """
    filenames = [fname for (fname, _, _, _) in prepared]
    logging.error(
        "Dropped turn (DB logging failed) for student %s: message=%r attachments=%r",
        student_id, content, filenames,
    )

# Initialize session state
if SESSION_MESSAGES not in st.session_state:
    st.session_state[SESSION_MESSAGES] = []
if SESSION_CONVERSATION_ID not in st.session_state:
    st.session_state[SESSION_CONVERSATION_ID] = None
if SESSION_FEEDBACK_KEY not in st.session_state:
    st.session_state[SESSION_FEEDBACK_KEY] = 0
if SESSION_LAST_DIAG not in st.session_state:
    st.session_state[SESSION_LAST_DIAG] = None

st.title("ChatBmE")

# Student identity (set at login). `student` was already pulled near the
# top of the file to drive sidebar visibility; just resolve the rest.
student_id = st.session_state.get(SESSION_STUDENT_ID, None)
backend = student.get("backend")

# Surface the logged-in username so instructors can eyeball student screens
# during sessions and confirm everyone is on the right account. Doubles as
# a data-quality check for the research logs.
if student_id:
    st.caption(f"Logged in as: **{student_id}**")

# Diagnostic users get a session-only backend override in the sidebar.
# Not persisted to the DB — purely for probing live behavior side-by-side.
if diagnostics_enabled:
    backend_options = ["anthropic", "mistral"]
    with st.sidebar:
        st.markdown("### Diagnostics")
        idx = backend_options.index(backend) if backend in backend_options else 0
        backend = st.radio(
            "Backend (session override)",
            backend_options,
            index=idx,
            help="Diagnostics-only override; not saved to the DB.",
        )

# Snapshot of the student row stored alongside each log entry. Excludes
# username (already in user_id) and created_at (datetime, not JSON-native
# and not a "setting"). The snapshot guards against later student-table
# resyncs, which TRUNCATE the table. We replace `backend` with the
# effective backend so logs reflect what was actually used (the
# diagnostics flag in the same dict signals a possible override).
student_settings = {
    k: v for k, v in student.items() if k not in ("username", "created_at")
} or None
if student_settings is not None:
    student_settings["backend"] = backend

# Refuse to route to a backend if the student row doesn't pin one. The
# configure script forbids this, but a hand-edited DB row could land here —
# and clearing the backend column can also serve as an intentional kill-switch.
if backend not in ("mistral", "anthropic"):
    logging.error("Student %s has invalid backend: %r", student_id, backend)
    st.error("Sorry, you can't use the chatbot at this moment.")
    st.stop()

# Anthropic relies on the local file registry — populated by
# script_configure_agents.py — to attach the BME knowledge base to every
# turn. An empty registry means the model would silently degrade to a
# generic Claude with no docs, and neither the student nor the instructor
# would see a signal. Fail closed instead, with an instructor-actionable
# message. (Mistral keeps its docs server-side in a library, so this
# check doesn't apply.)
if backend == "anthropic":
    if not load_registry():
        logging.error(
            "Anthropic file registry is empty for student %s; aborting chat",
            student_id,
        )
        st.error(
            "The chatbot's knowledge base is currently unavailable. "
            "Please contact an instructor."
        )
        st.stop()

    # Make sure every registered file_id still exists in the Anthropic
    # workspace. A file deleted out from under us would otherwise 400 on
    # every turn — the user would just see "something went wrong" with
    # no actionable signal. Validation is cached (one batch of API calls
    # per process); a re-upload requires a deploy restart to invalidate.
    missing = _validate_registry_cached()
    if missing:
        names = ", ".join(m["filename"] for m in missing)
        logging.error(
            "Anthropic registry has stale file_ids for student %s: %s",
            student_id, names,
        )
        st.error(
            f"Some knowledge-base documents are no longer available "
            f"({names}). Please ask an instructor to re-run the configure "
            f"script."
        )
        st.stop()

# Diagnostic users can flip backends mid-session via the sidebar radio.
# A conversation id from one backend has no meaning in the other (Mistral
# would 404 on the Anthropic "Not Applicable" placeholder, and vice
# versa), so reset whenever the effective backend changes.
if st.session_state.get(SESSION_LAST_BACKEND) != backend:
    st.session_state[SESSION_CONVERSATION_ID] = None
    st.session_state[SESSION_LAST_BACKEND] = backend

# Anthropic is stateless — there's no server-issued conversation id. Use a
# literal placeholder so the logs distinguish "Anthropic, no id" from a
# Mistral row where the id never came back. Restart Chat resets to None
# (see below), and this branch re-stamps it on rerun.
if backend == "anthropic" and st.session_state[SESSION_CONVERSATION_ID] is None:
    st.session_state[SESSION_CONVERSATION_ID] = "Not Applicable"

# Display chat messages from history on app rerun
for message in st.session_state[SESSION_MESSAGES]:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            # Render as plain text so student-typed Markdown (links, images,
            # headings) is not interpreted.
            st.text(message["content"])
        else:
            st.markdown(message["content"])
            if message.get("truncated"):
                st.caption(
                    "_Response was cut off — ask me to continue if you'd like more._"
                )

# React to user input. accept_file lets students attach screenshots (robot
# code, behaviour, or error messages); the returned value carries .text and
# .files instead of a plain string. file_type pre-filters the picker, but
# prepare_uploaded_image re-validates size and MIME server-side.
if user_input := st.chat_input(
    "Ask about robots, sensors, or animal sensing...",
    accept_file="multiple",
    file_type=UPLOAD_FILE_TYPES,
):
    caption = (user_input.text or "").strip()

    # Validate + normalise each uploaded image. Rejected files (too big /
    # wrong type) are reported but don't block a valid caption from sending.
    # prepared entries are (filename, mime, raw_bytes, b64).
    prepared = []
    for uploaded in (user_input.files or []):
        try:
            prepared.append(prepare_uploaded_image(uploaded))
        except ImageValidationError as exc:
            st.warning(str(exc))

    # The stored/sent text carries a 📎 marker per attachment. This doubles as
    # the badge when the turn re-renders, and — since images are single-turn —
    # gives the model a textual trace on later turns without re-billing image
    # tokens. An image with no caption becomes just the marker (never empty).
    markers = "".join(f"\n📎 {fname}" for (fname, _, _, _) in prepared)
    content = (caption + markers).strip()

    # Nothing usable to send (e.g. every upload was rejected and no
    # caption). Warnings are already shown; fall through to the widgets
    # below (feedback, diagnostics) instead of st.stop(), which would halt
    # the whole rerun and blank them out for that pass.
    if content:
        # Display user message in chat message container
        with st.chat_message("user"):
            # Plain text — see note above on Markdown interpretation.
            st.text(content)
        # Add user message to chat history. Only the text/marker is stored — the
        # base64 image blocks live for exactly this turn (single-turn rule), so
        # history replay never re-sends them.
        st.session_state[SESSION_MESSAGES].append({"role": "user", "content": content})

        # First, moderate the user message. Moderation is text-only by design:
        # only the caption is classified — image content and the 📎 filename
        # markers bypass the moderator. Filenames often contain dates (e.g.
        # phone screenshots) that get false-flagged as PII, and image content
        # moderation is overkill for a supervised, logged-in classroom (see
        # the fail-open stance documented in readme.md).
        moderation_passed, flagged_categories = run_moderation(caption)

        if not moderation_passed:
            # Message was rejected — tell the student which categories were violated.
            # (run_moderation fails open on API errors, so reaching this branch
            # means the classifier really did flag the message.)
            categories_str = ", ".join(flagged_categories) if flagged_categories else "content policy"
            agent_response = f"I'm sorry, I can't process that request. Violated categories: **{categories_str}**."
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": agent_response})
        else:
            # Get response from the configured backend
            try:
                # Anthropic is stateless — every call sends the full history. Cap it
                # so input cost and request size don't grow unboundedly with long
                # sessions. The chat panel still shows the full transcript to the
                # student; only what goes to the model is trimmed. Cap lives in
                # agent/anthropic_lib/config.toml as `max_history_messages`. The
                # -1 leaves room for the new user message that's passed separately.
                anthropic_history = _trim_history_for_anthropic(
                    st.session_state[SESSION_MESSAGES][:-1],
                    anthropic_config("max_history_messages") - 1,
                )
                with st.spinner("Thinking..."):
                    if backend == "anthropic":
                        response = anthropic_conversation.send_message(
                            history=anthropic_history,
                            user_message=content,
                            images=prepared,
                        )
                    elif backend == "mistral":
                        response = mistral_conversation.send_message_to_agent(
                            message=content,
                            agent_id=agent_id,
                            conversation_id=st.session_state[SESSION_CONVERSATION_ID],
                            display=False,
                            images=prepared,
                        )
                        # Only update on a non-None id. If the response shape ever
                        # changes and conversation_id is missing, overwriting with
                        # None would silently start a fresh server-side
                        # conversation on the next turn.
                        new_conv_id = response.get('conversation_id')
                        if new_conv_id is not None:
                            st.session_state[SESSION_CONVERSATION_ID] = new_conv_id
                        else:
                            logging.warning(
                                "Mistral response missing conversation_id for student %s; "
                                "keeping previous value", student_id
                            )
                agent_response = response.get('assistant_response', 'No response from agent')

                # Capture a diagnostic snapshot of what was just sent/received,
                # for rendering in the sidebar. Mirrors the shape script_chat.py
                # prints, so the two views stay comparable.
                if diagnostics_enabled:
                    diag = {
                        "backend":         backend,
                        "conversation_id": st.session_state[SESSION_CONVERSATION_ID],
                    }
                    if backend == "anthropic":
                        try:
                            from anthropic_lib.conversation_management import _build_messages
                            msgs = _build_messages(
                                history=anthropic_history,
                                user_message=content,
                                images=prepared,
                            )
                            blocks = msgs[-1]["content"]
                            diag["model"] = anthropic_config("model")
                            diag["block_order"] = blocks[0].get("type") if blocks else None
                            diag["images"] = sum(
                                1 for b in blocks if b.get("type") == "image"
                            )
                            diag["docs"] = [
                                {
                                    "title":   b.get("title", "(untitled)"),
                                    "file_id": b.get("source", {}).get("file_id"),
                                }
                                for b in blocks if b.get("type") == "document"
                            ]
                        except Exception as e:
                            diag["error"] = f"diagnostic capture failed: {e}"
                    elif backend == "mistral":
                        diag["agent_id"] = agent_id
                        diag["responding_agents"] = response.get("responding_agent_ids", [])
                    st.session_state[SESSION_LAST_DIAG] = diag

                # Log interaction to database
                try:
                    log_success = log_interaction(
                        client_config=db_config,
                        conversation_id=st.session_state[SESSION_CONVERSATION_ID],
                        user_message=content,
                        agent_response=agent_response,
                        user_id=student_id,
                        llm=backend,
                        # Defensive copy — student_settings is the same dict
                        # passed to every log_* call; copying keeps a later
                        # in-place mutation from leaking into earlier writes.
                        student_settings=dict(student_settings) if student_settings else None,
                        # Persist the raw image bytes (sans base64) alongside the
                        # turn. Single-turn images aren't kept in session state, so
                        # this DB row is the only durable record of the screenshot.
                        attachments=[
                            (fname, mime, raw) for (fname, mime, raw, _) in prepared
                        ] or None,
                    )
                    if not log_success:
                        st.warning("Logging to database failed")
                        _log_dropped_turn(student_id, content, prepared)
                except Exception as log_err:
                    st.warning(f"Logging failed: {log_err}")
                    _log_dropped_turn(student_id, content, prepared)

                # Display assistant response in chat message container
                truncated = response.get("stop_reason") == "max_tokens"
                with st.chat_message("assistant"):
                    st.markdown(agent_response)
                    if truncated:
                        st.caption(
                            "_Response was cut off — ask me to continue if you'd like more._"
                        )
                # Add assistant response to chat history. The truncated flag is
                # presentation-only (the history-render loop reads it) and is
                # not sent back to the model.
                message_entry = {"role": "assistant", "content": agent_response}
                if truncated:
                    message_entry["truncated"] = True
                st.session_state[SESSION_MESSAGES].append(message_entry)
            except Exception:
                # Log the real exception with traceback for debugging; show the
                # student a generic message so SDK errors (which can carry stack
                # traces, internal IDs, or keys) don't leak to the chat.
                logging.exception(
                    "Backend %s failed for student %s", backend, student_id
                )
                # Drop the user message that was queued for this turn. The API
                # call didn't succeed so the model never saw it, and persisting
                # it (or an error placeholder) into SESSION_MESSAGES would re-send
                # it as part of history on the next turn — bad for Anthropic
                # especially, where every replay re-renders the failed turn.
                if (
                    st.session_state[SESSION_MESSAGES]
                    and st.session_state[SESSION_MESSAGES][-1].get("role") == "user"
                ):
                    st.session_state[SESSION_MESSAGES].pop()
                st.error(
                    "Sorry, something went wrong on my end. Please try sending "
                    "your message again."
                )

# Feedback widget — only shown once there is something to rate
if st.session_state[SESSION_MESSAGES]:
    st.markdown("**How is the chatbot doing?**")
    sentiment = st.feedback(
        "thumbs",
        key=f"feedback_{st.session_state[SESSION_FEEDBACK_KEY]}",
    )
    if sentiment is not None:
        # Versioned key so the field resets after each submission, matching
        # the thumbs widget above. A fixed key would carry the previous
        # note into the next feedback round.
        note = st.text_input(
            "Add a note (optional)",
            key=f"feedback_note_{st.session_state[SESSION_FEEDBACK_KEY]}",
        )
        # Dedup marker keyed by the current feedback_key. A double-click on
        # the submit button can fire two reruns before the first completes;
        # the marker makes the second one a no-op so we don't log twice.
        # The marker is per-feedback_key, so a fresh feedback session (with
        # the incremented key) is unaffected.
        submitted_marker = f"_submitted_fb_{st.session_state[SESSION_FEEDBACK_KEY]}"
        if st.button("Submit feedback") and not st.session_state.get(submitted_marker):
            st.session_state[submitted_marker] = True
            try:
                log_success = log_feedback(
                    client_config=db_config,
                    conversation_id=st.session_state[SESSION_CONVERSATION_ID],
                    sentiment=sentiment,
                    note=note,
                    user_id=student_id,
                    student_settings=dict(student_settings) if student_settings else None,
                )
                if not log_success:
                    st.warning("Saving your feedback failed — please try again.")
            except Exception as log_err:
                st.warning(f"Saving your feedback failed: {log_err}")
            st.session_state[SESSION_FEEDBACK_KEY] += 1
            st.toast("Thanks for your feedback!")
            st.rerun()

# Read-only diagnostic views — render after the chat loop so "Last turn"
# reflects the message that was just processed, not the previous one.
if diagnostics_enabled:
    with st.sidebar:
        with st.expander("Last turn", expanded=True):
            last = st.session_state.get(SESSION_LAST_DIAG)
            if last:
                st.json(last)
            else:
                st.write("(no turns yet)")
        with st.expander("Student row"):
            st.json(student)
        # Anthropic-only — Mistral keeps documents server-side in its
        # library and we can't introspect that from here.
        if backend == "anthropic":
            registry = load_registry()
            with st.expander(f"Anthropic registry ({len(registry)} docs)"):
                if registry:
                    st.json({k: v.get("title") for k, v in registry.items()})
                else:
                    st.write("(empty — chat is blocked above)")