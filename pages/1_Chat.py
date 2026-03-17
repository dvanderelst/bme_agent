import streamlit as st
import json
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
</style>
""", unsafe_allow_html=True)

# Redirect to login if not authenticated
if not st.session_state.get("authenticated"):
    st.switch_page("main.py")

# Configuration - try Streamlit secrets first, fallback to ConfigManager
try:
    agent_id = st.secrets["bme_agent"]
    moderator_agent_id = st.secrets.get("moderator_agent", "ag_019cfce17e42754b86cf2a3eef28dd2b")  # Use the actual created agent ID
    supabase = get_supabase_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
except (AttributeError, KeyError):
    from library.ConfigManager import config
    agent_id = config.bme_agent
    moderator_agent_id = config.get("moderator_agent", "ag_019cfce17e42754b86cf2a3eef28dd2b")  # Use the actual created agent ID
    supabase = get_supabase_client(config.get("supabase_url"), config.get("supabase_key"))

def moderate_message(message: str) -> tuple[bool, str]:
    """Send message to moderator agent and return (passed, sanitized_message_or_reason)."""
    try:
        moderation_response = ConversationManagement.send_message_to_agent(
            message=message,
            agent_id=moderator_agent_id,
            conversation_id=None,  # Moderator gets fresh context each time
            display=False
        )
        
        # Parse the JSON response
        moderation_result = moderation_response.get('assistant_response', '{}')
        
        # Clean up Markdown code blocks if present
        if moderation_result.startswith('```json'):
            # Remove Markdown code block markers
            moderation_result = moderation_result.replace('```json', '').replace('```', '').strip()
        
        try:
            result_data = json.loads(moderation_result)
            status = result_data.get('status', 'fail')
            reason = result_data.get('reason', 'No reason provided')
            
            if status == 'pass':
                return True, result_data.get('sanitized_message', message)
            else:
                return False, reason
                
        except json.JSONDecodeError:
            return False, "Invalid moderator response format"
            
    except Exception as e:
        return False, f"Moderation error: {str(e)}"

st.title("BME Specialist Chat")

# Get anonymous student ID stored at login
student_id = st.session_state.get("student_id", None)

# Initialize chat history and conversation tracking
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

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
        # Message failed moderation - show specific reason if available
        reason = moderation_result if moderation_result else "content that violates our guidelines or may include personal information"
        agent_response = f"I am sorry, I can't process that request. Reason: {reason}"
        
        # Display the rejection message
        with st.chat_message("assistant"):
            st.markdown(agent_response)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})
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