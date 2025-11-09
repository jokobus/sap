"""Utility functions shared across all tabs"""
import streamlit as st
import os
from datetime import datetime
import json


def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'step' not in st.session_state:
        st.session_state.step = 'init'
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'cv_uploaded' not in st.session_state:
        st.session_state.cv_uploaded = False


def save_data():
    """Saves the collected user data to a JSON file."""
    script_dir = os.path.dirname(__file__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(script_dir, "data", "outputs", f"intake_{timestamp}.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(st.session_state.user_data, f, indent=4)
    st.success(f"Your information has been saved.")


def navigation_buttons(back_step=None, next_step=None, next_text="Continue"):
    """Creates standardized back and next buttons."""
    st.write("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if back_step:
            if st.button("⬅️ Back"):
                st.session_state.step = back_step
                st.rerun()
    with col2:
        if next_step:
            if st.button(f"{next_text} ➡️"):
                st.session_state.step = next_step
                st.rerun()
