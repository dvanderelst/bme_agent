import streamlit as st

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# Already logged in — go straight to chat
if st.session_state.get("authenticated"):
    st.switch_page("pages/1_Chat.py")

st.title("BME Specialist Chat")
st.write("Please enter the class password to continue.")

password = st.text_input("Password", type="password")

if st.button("Enter"):
    if password == st.secrets["app_password"]:
        st.session_state.authenticated = True
        st.session_state.student_id = st.query_params.get("student", None)
        st.switch_page("pages/1_Chat.py")
    else:
        st.error("Incorrect password. Please try again.")
