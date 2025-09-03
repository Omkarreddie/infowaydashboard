import base64
import hashlib
import streamlit as st

# -------------------------- Image Helper --------------------------
def image_to_base64(image_path):
    """Convert image to base64 for embedding in HTML."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
def load_login_css(css="css/loginstyle.css"):
    try:
        with open(css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css}")



def load_main_css(css="css/main.css"):
    try:
        with open(css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Css file not found:{css}")

def hyper_link(css="css/hyperlink.css"):
    try:
        with open(css,'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"css file not found:{css}")