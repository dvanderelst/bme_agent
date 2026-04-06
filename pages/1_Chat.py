import streamlit as st
import logging
from mistral_lib import conversation_management as mistral_conversation
from mistral_lib.moderation import moderate
from anthropic_lib import conversation_management as anthropic_conversation
from shared_lib.postgres_logger import get_postgres_client as get_baserow_client, log_interaction

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
if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

# Configuration - try Streamlit secrets first, fallback to ConfigManager
try:
    agent_id = st.secrets["bme_agent"]
    baserow_config = get_baserow_client(st.secrets["database_url"])
except (AttributeError, KeyError):
    from shared_lib.config_manager import config
    agent_id = config.get("bme_agent")
    baserow_config = get_baserow_client(config.get("database_url"))
except ValueError as ve:
    st.error(f"Database configuration error: {str(ve)}")
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
        st.session_state.moderation_error = message
        return False, []

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "backend" not in st.session_state:
    st.session_state.backend = "mistral"

_title_col, _spacer, _mistral_col, _toggle_col, _anthropic_col = st.columns([6, 1, 2, 1, 2])
with _title_col:
    st.title("BME Specialist Chat")
with _mistral_col:
    st.markdown("<div style='text-align:right; padding-top:18px; font-size:0.9em;'>Mistral</div>", unsafe_allow_html=True)
with _toggle_col:
    st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
    _use_anthropic = st.toggle("backend", value=(st.session_state.backend == "anthropic"), label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
with _anthropic_col:
    st.markdown("<div style='text-align:left; padding-top:18px; font-size:0.9em;'>Anthropic</div>", unsafe_allow_html=True)

_new_backend = "anthropic" if _use_anthropic else "mistral"
if _new_backend != st.session_state.backend:
    st.session_state.backend = _new_backend
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.rerun()

# Get anonymous student ID stored at login
student_id = st.session_state.get("student_id", None)

# Show moderation system error if one occurred
if st.session_state.get("moderation_error"):
    st.warning(
        "Something went wrong processing your message. "
        "Please restart the chat and try again."
    )
    if st.button("Restart Chat"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.moderation_error = None
        st.rerun()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f'**{message["content"]}**')  # Bold for user messages
        else:
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about robots, sensors, or animal sensing..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f'**{prompt}**')  # Bold for user messages
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # First, moderate the user message
    moderation_passed, flagged_categories = run_moderation(prompt)

    if not moderation_passed:
        if not st.session_state.get("moderation_error"):
            # Message was rejected — tell the student which categories were violated
            categories_str = ", ".join(flagged_categories) if flagged_categories else "content policy"
            agent_response = f"I'm sorry, I can't process that request. Violated categories: **{categories_str}**."
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
        # If moderation_error is set, the warning box above handles the messaging
    else:
        # Get response from the configured backend
        try:
            with st.spinner("Thinking..."):
                if st.session_state.backend == "anthropic":
                    response = anthropic_conversation.send_message(
                        history=st.session_state.messages[:-1],
                        user_message=prompt,
                    )
                else:
                    response = mistral_conversation.send_message_to_agent(
                        message=prompt,
                        agent_id=agent_id,
                        conversation_id=st.session_state.conversation_id,
                        display=False,
                    )
                    st.session_state.conversation_id = response.get('conversation_id')
            agent_response = response.get('assistant_response', 'No response from agent')
            
            # Log interaction to Baserow
            try:
                log_success = log_interaction(
                    client_config=baserow_config,
                    conversation_id=st.session_state.conversation_id,
                    user_message=prompt,
                    agent_response=agent_response,
                    user_id=student_id,
                )
                if not log_success:
                    st.warning("Logging to database failed")
            except Exception as log_err:
                st.warning(f"Logging failed: {log_err}")

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
        except Exception as e:
            error_msg = f"Error getting agent response: {str(e)}"
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})