import streamlit as st
import logging
from mistral_lib import conversation_management as mistral_conversation
from mistral_lib.moderation import moderate
from anthropic_lib import conversation_management as anthropic_conversation
from shared_lib.postgres_logger import get_postgres_client, log_interaction, log_feedback

SESSION_AUTHENTICATED = "authenticated"
SESSION_MESSAGES = "messages"
SESSION_CONVERSATION_ID = "conversation_id"
SESSION_MODERATION_ERROR = "moderation_error"
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
    db_config = get_postgres_client(database_url)
except Exception as e:
    logging.error("Database setup failed on chat page: %s", e)
    st.error("The chatbot is temporarily unavailable. Please try again later.")
    st.stop()

# Validate required config
if not agent_id:
    st.error("Missing required configuration: bme_agent. Check your secrets.toml.")
    st.stop()

def run_moderation(message: str) -> tuple[bool, list]:
    """Run message through the Mistral moderation classifier.

    Returns (passed, flagged_categories).
    Fails closed on API error — blocks the message and logs the incident.
    """
    try:
        result = moderate(message)
        return result.passed, result.flagged_categories
    except Exception as e:
        logging.error(f"Moderation API call failed: {e}")
        st.session_state[SESSION_MODERATION_ERROR] = message
        return False, []

# Initialize session state
if SESSION_MESSAGES not in st.session_state:
    st.session_state[SESSION_MESSAGES] = []
if SESSION_CONVERSATION_ID not in st.session_state:
    st.session_state[SESSION_CONVERSATION_ID] = None
if SESSION_FEEDBACK_KEY not in st.session_state:
    st.session_state[SESSION_FEEDBACK_KEY] = 0
if SESSION_LAST_DIAG not in st.session_state:
    st.session_state[SESSION_LAST_DIAG] = None

st.title("Bme Chat")

# Student identity (set at login). `student` was already pulled near the
# top of the file to drive sidebar visibility; just resolve the rest.
student_id = st.session_state.get(SESSION_STUDENT_ID, None)
backend = student.get("backend")

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

# Show moderation system error if one occurred
if st.session_state.get(SESSION_MODERATION_ERROR):
    st.warning(
        "Something went wrong processing your message. "
        "Please restart the chat and try again."
    )
    if st.button("Restart Chat"):
        st.session_state[SESSION_MESSAGES] = []
        st.session_state[SESSION_CONVERSATION_ID] = None
        st.session_state[SESSION_MODERATION_ERROR] = None
        st.rerun()

# Display chat messages from history on app rerun
for message in st.session_state[SESSION_MESSAGES]:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            # Render as plain text so student-typed Markdown (links, images,
            # headings) is not interpreted.
            st.text(message["content"])
        else:
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about robots, sensors, or animal sensing..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        # Plain text — see note above on Markdown interpretation.
        st.text(prompt)
    # Add user message to chat history
    st.session_state[SESSION_MESSAGES].append({"role": "user", "content": prompt})

    # First, moderate the user message
    moderation_passed, flagged_categories = run_moderation(prompt)

    if not moderation_passed:
        if not st.session_state.get(SESSION_MODERATION_ERROR):
            # Message was rejected — tell the student which categories were violated
            categories_str = ", ".join(flagged_categories) if flagged_categories else "content policy"
            agent_response = f"I'm sorry, I can't process that request. Violated categories: **{categories_str}**."
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": agent_response})
        # If SESSION_MODERATION_ERROR is set, the warning box above handles the messaging
    else:
        # Get response from the configured backend
        try:
            with st.spinner("Thinking..."):
                if backend == "anthropic":
                    response = anthropic_conversation.send_message(
                        history=st.session_state[SESSION_MESSAGES][:-1],
                        user_message=prompt,
                    )
                elif backend == "mistral":
                    response = mistral_conversation.send_message_to_agent(
                        message=prompt,
                        agent_id=agent_id,
                        conversation_id=st.session_state[SESSION_CONVERSATION_ID],
                        display=False,
                    )
                    st.session_state[SESSION_CONVERSATION_ID] = response.get('conversation_id')
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
                        from anthropic_lib.config import get as anthropic_config
                        msgs = _build_messages(
                            history=st.session_state[SESSION_MESSAGES][:-1],
                            user_message=prompt,
                        )
                        blocks = msgs[-1]["content"]
                        diag["model"] = anthropic_config("model")
                        diag["block_order"] = blocks[0].get("type") if blocks else None
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
                    user_message=prompt,
                    agent_response=agent_response,
                    user_id=student_id,
                    llm=backend,
                    student_settings=student_settings,
                )
                if not log_success:
                    st.warning("Logging to database failed")
            except Exception as log_err:
                st.warning(f"Logging failed: {log_err}")

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            # Add assistant response to chat history
            st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": agent_response})
        except Exception as e:
            error_msg = f"Error getting agent response: {str(e)}"
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": error_msg})

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
        if st.button("Submit feedback"):
            try:
                log_success = log_feedback(
                    client_config=db_config,
                    conversation_id=st.session_state[SESSION_CONVERSATION_ID],
                    sentiment=sentiment,
                    note=note,
                    user_id=student_id,
                    student_settings=student_settings,
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