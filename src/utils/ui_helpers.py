import streamlit as st

def hyperlink_button(label: str, on_click=None, key=None, tooltip=None):
    """
    Display a Streamlit button styled as a hyperlink.

    Args:
        label (str): The text to display (e.g., username or group name)
        on_click (function, optional): Function to call when clicked
        key (str, optional): Unique key for Streamlit button
        tooltip (str, optional): Hover tooltip
    """
    # Add CSS only once
    if "hyperlink_css_added" not in st.session_state:
        st.markdown("""
        <style>
        div.user-link button {
            all: unset;               /* Remove background, border, padding, margin */
            cursor: pointer;
            font-size: 16px;
            font-family: inherit;
        }
        div.user-link button span.group-name {
            color: #0645AD;          /* Blue color */
            text-decoration: underline;
        }
        div.user-link button:hover span.group-name {
            color: #0B0080;          /* Darker blue on hover */
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.hyperlink_css_added = True

    # Display the button
    if st.button(f"<span class='group-name'>{label}</span>", 
                 key=key, help=tooltip, on_click=on_click):
        if on_click:
            on_click()
        st.rerun()
