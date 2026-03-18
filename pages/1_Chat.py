import streamlit as st
import json
import logging
import re
from library import ConversationManagement
from library.SupabaseLogger import get_supabase_client, log_interaction

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
    st.switch_page("main.py")

# Configuration - try Streamlit secrets first, fallback to ConfigManager
try:
    agent_id = st.secrets["bme_agent"]
    moderator_agent_id = st.secrets["moderator_agent"]
    supabase = get_supabase_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
except (AttributeError, KeyError):
    from library.ConfigManager import config
    agent_id = config.bme_agent
    moderator_agent_id = config.get("moderator_agent")
    supabase = get_supabase_client(config.get("supabase_url"), config.get("supabase_key"))

def _parse_moderation_response(raw: str) -> dict | None:
    """Extract and parse a JSON object from the moderator's response.

    Handles markdown code fences and falls back to regex extraction
    if direct parsing fails.
    """
    # Strip markdown code fences
    text = re.sub(r'```(?:json)?\s*', '', raw).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back to extracting the first {...} block
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _call_moderator(message: str) -> dict | None:
    """Call the moderator agent and return parsed JSON, or None on failure."""
    try:
        response = ConversationManagement.send_message_to_agent(
            message=message,
            agent_id=moderator_agent_id,
            conversation_id=None,
            display=False
        )
        raw = response.get('assistant_response', '')
        return _parse_moderation_response(raw)
    except Exception as e:
        logging.warning(f"Moderator API call failed: {e}")
        return None


def moderate_message(message: str) -> tuple[bool, str]:
    """Send message to moderator and return (passed, sanitized_message_or_reason).

    Retries once on parse failure. Fails open if both attempts fail,
    logging the incident for review.
    """
    result = _call_moderator(message)

    if result is None:
        logging.warning("Moderator returned unparseable response, retrying...")
        result = _call_moderator(message)

    if result is None:
        logging.error(f"Moderator failed twice for message: {message[:100]!r}")
        st.session_state.moderation_error = message
        return False, "moderation_system_failure"

    if result.get('status') == 'pass':
        sanitized = result.get('sanitized_message') or message
        return True, sanitized
    else:
        reason = result.get('reason') or 'Content moderation failed'
        return False, reason

st.title("BME Specialist Chat")

# Get anonymous student ID stored at login
student_id = st.session_state.get("student_id", None)

# Initialize chat history and conversation tracking
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

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
    moderation_passed, moderation_result = moderate_message(prompt)
    
    if not moderation_passed:
        if moderation_result != "moderation_system_failure":
            # Message was rejected by the moderator — tell the student why
            reason = moderation_result or "content that violates our guidelines or may include personal information"
            agent_response = f"I am sorry, I can't process that request. Reason: {reason}"
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
        # If moderation_system_failure, the warning box above handles the messaging
    else:
        # Message passed moderation - use sanitized version
        sanitized_prompt = moderation_result
        
        # Get response from the configured agent
        try:
            with st.spinner("Thinking..."):
                response = ConversationManagement.send_message_to_agent(
                    message=sanitized_prompt,
                    agent_id=agent_id,
                    conversation_id=st.session_state.conversation_id,
                    display=False
                )
            st.session_state.conversation_id = response.get('conversation_id')
            agent_response = response.get('assistant_response', 'No response from agent')
            
            # Log interaction to Supabase (use sanitized message, not original)
            try:
                log_interaction(
                    client=supabase,
                    conversation_id=st.session_state.conversation_id,
                    user_message=sanitized_prompt,  # Use sanitized version
                    agent_response=agent_response,
                    user_id=student_id
                )
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