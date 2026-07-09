import streamlit as st

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="KinderCare",
    layout="wide"
)

# Import your actual app logic AFTER Streamlit starts
import app

# If app.py has a render() or main() function, call it
if hasattr(app, "render"):
    app.render()
