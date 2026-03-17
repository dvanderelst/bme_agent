import streamlit as st
from library import ConversationManagement
from library.SupabaseLogger import get_supabase_client, log_interaction

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# Redirect to login if not authenticated
if not st.session_state.get("authenticated"):
    st.switch_page("main.py")

# Configuration - try Streamlit secrets first, fallback to ConfigManager
try:
    agent_id = st.secrets["bme_agent"]
    supabase = get_supabase_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
except (AttributeError, KeyError):
    from library.ConfigManager import config
    agent_id = config.bme_agent
    supabase = get_supabase_client(config.get("supabase_url"), config.get("supabase_key"))

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
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about robots, sensors, or animal sensing..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from the configured agent
    try:
        with st.spinner("Thinking..."):
            response = ConversationManagement.send_message_to_agent(
                message=prompt,
                agent_id=agent_id,
                conversation_id=st.session_state.conversation_id,
                display=False
            )
        st.session_state.conversation_id = response.get('conversation_id')
        agent_response = response.get('assistant_response', 'No response from agent')

        # Log interaction to Supabase
        try:
            log_interaction(
                client=supabase,
                conversation_id=st.session_state.conversation_id,
                user_message=prompt,
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