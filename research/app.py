import logging
import time

import streamlit as st

from shared_lib.auth import (
    authenticate,
    check_login_lockout,
    record_login_failure,
)
from shared_lib.postgres_logger import get_postgres_client

from rubric_db import ensure_rubric_table

# Penalty added to every failed login. Equalises timing between unknown-user
# and wrong-password paths and slows brute-force attempts to a crawl.
FAILED_LOGIN_DELAY_SECONDS = 0.5

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# Already logged in — go straight to the intro page
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Intro.py")

# Resolve database URL — Streamlit secrets first, then ConfigManager fallback
try:
    database_url = st.secrets["DATABASE_URL"]
except (AttributeError, KeyError):
    from shared_lib.config_manager import config
    database_url = config.get("database_url")

try:
    db_config = get_postgres_client(database_url)
    ensure_rubric_table(database_url)
except Exception as e:
    logging.error("Database setup failed: %s", e)
    st.error("The survey is temporarily unavailable. Please try again later.")
    st.stop()

st.title("Bme Survey")
st.write("Please log in to continue.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log in")

    if submitted:
        # Throttle: cheap SELECT before bcrypt so a script grinding the same
        # username can't burn cycles past the threshold.
        locked, seconds_until_unlock = check_login_lockout(db_config, username)
        if locked:
            minutes = max(1, (seconds_until_unlock + 59) // 60)
            st.error(
                f"Too many failed attempts. Please wait about {minutes} "
                f"minute(s) and try again."
            )
        else:
            student = authenticate(db_config, username, password)
            if student is None:
                record_login_failure(db_config, username)
                time.sleep(FAILED_LOGIN_DELAY_SECONDS)
                st.error("Incorrect username or password.")
            elif not student.get("enabled", True):
                time.sleep(FAILED_LOGIN_DELAY_SECONDS)
                st.error("Sorry, you don't have access to the survey at this moment.")
            else:
                st.session_state.authenticated = True
                st.session_state.student = student
                st.session_state.student_id = student["username"]
                st.session_state.database_url = database_url
                st.switch_page("pages/1_Intro.py")
