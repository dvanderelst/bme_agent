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

st.markdown("""
<style>
[data-testid='stSidebar'] {display: none;}
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

st.title("Bme Chat")

# Student identity (set at login). Full row is in st.session_state["student"].
student = st.session_state.get(SESSION_STUDENT) or {}
student_id = st.session_state.get(SESSION_STUDENT_ID, None)
backend = student.get("backend")

# Snapshot of the student row stored alongside each log entry. Excludes
# username (already in user_id) and created_at (datetime, not JSON-native
# and not a "setting"). The snapshot guards against later student-table
# resyncs, which TRUNCATE the table.
student_settings = {
    k: v for k, v in student.items() if k not in ("username", "created_at")
} or None

# Refuse to route to a backend if the student row doesn't pin one. The
# configure script forbids this, but a hand-edited DB row could land here —
# and clearing the backend column can also serve as an intentional kill-switch.
if backend not in ("mistral", "anthropic"):
    logging.error("Student %s has invalid backend: %r", student_id, backend)
    st.error("Sorry, you can't use the chatbot at this moment.")
    st.stop()

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