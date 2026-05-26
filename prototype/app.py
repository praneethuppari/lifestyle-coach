"""
Lifestyle Coach — prototype UI.

This is a throwaway prototype for testing API flows.
It is not the final UI. Replace or delete it once real frontend development begins.

Run with:
    streamlit run prototype/app.py

The backend must be running at http://localhost:8000.
"""

import requests
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000/api/v1"

# ── Session defaults ──────────────────────────────────────────────────────────

if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ── Helpers ───────────────────────────────────────────────────────────────────


def is_logged_in() -> bool:
    return st.session_state.token is not None


def logout() -> None:
    st.session_state.token = None
    st.session_state.user_email = None
    st.rerun()


# ── Pages ─────────────────────────────────────────────────────────────────────


def page_login() -> None:
    st.title("Lifestyle Coach")

    tab_login, tab_register = st.tabs(["Sign in", "Create account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
            else:
                resp = requests.post(
                    f"{API_BASE}/auth/login",
                    data={"username": email, "password": password},
                )
                if resp.status_code == 200:
                    st.session_state.token = resp.json()["access_token"]
                    st.session_state.user_email = email
                    st.rerun()
                elif resp.status_code == 401:
                    st.error("Invalid email or password.")
                else:
                    st.error(f"Unexpected error ({resp.status_code}).")

    with tab_register:
        with st.form("register_form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_display = st.text_input("Display name (optional)", key="reg_display")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_submitted = st.form_submit_button("Create account", use_container_width=True)

        if reg_submitted:
            if not reg_email or not reg_password:
                st.error("Email and password are required.")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                payload = {"email": reg_email, "password": reg_password}
                if reg_display:
                    payload["display_name"] = reg_display
                resp = requests.post(f"{API_BASE}/auth/register", json=payload)
                if resp.status_code == 201:
                    st.session_state.token = resp.json()["access_token"]
                    st.session_state.user_email = reg_email
                    st.rerun()
                elif resp.status_code == 409:
                    st.error("An account with that email already exists.")
                elif resp.status_code == 422:
                    st.error("Invalid input. Check your email and password.")
                else:
                    st.error(f"Unexpected error ({resp.status_code}).")


def page_home() -> None:
    st.title("Lifestyle Coach")
    st.write(f"Signed in as **{st.session_state.user_email}**")

    st.info(
        "This prototype is a placeholder. "
        "Add pages here as backend features are completed."
    )

    st.subheader("What's available")
    st.markdown(
        """
        - [x] Auth — register, login, JWT
        - [ ] Recipes — endpoints ready, UI pending
        - [ ] Ingredients — endpoints ready, UI pending
        - [ ] Meal planning — not started
        """
    )

    if st.button("Sign out"):
        logout()


# ── Router ────────────────────────────────────────────────────────────────────

if not is_logged_in():
    page_login()
else:
    page_home()
