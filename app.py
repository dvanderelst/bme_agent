import streamlit as st

from shared_lib.auth import authenticate
from shared_lib.postgres_logger import get_postgres_client

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# Already logged in — go straight to chat
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Chat.py")

# Resolve database URL — Streamlit secrets first, then ConfigManager fallback
try:
    database_url = st.secrets["DATABASE_URL"]
except (AttributeError, KeyError):
    from shared_lib.config_manager import config
    database_url = config.get("database_url")

try:
    db_config = get_postgres_client(database_url)
except (ValueError, Exception) as e:
    st.error(f"Database configuration error: {e}")
    st.stop()

st.title("BME Specialist Chat")
st.write("Please log in to continue.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log in")

    if submitted:
        student = authenticate(db_config, username, password)
        if student is None:
            st.error("Incorrect username or password.")
        elif not student.get("enabled", True):
            st.error("Sorry, you don't have access to the chatbot at this moment.")
        else:
            st.session_state.authenticated = True
            st.session_state.student = student
            st.session_state.student_id = student["username"]
            st.switch_page("pages/1_Chat.py")
