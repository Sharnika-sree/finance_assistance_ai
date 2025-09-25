# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from services.huggingface_service import HuggingFaceFinanceService

# Load environment variables
load_dotenv()

# Import page modules
from pages.profile_setup import show_profile_setup
from pages.chat import show_chat_interface

# Page configuration
st.set_page_config(
    page_title="Personal Finance Chatbot",
    page_icon="💰",
    layout="wide"
)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ------------------------------
# Custom CSS
# ------------------------------
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}
.button-container {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Header
# ------------------------------
def show_main_header():
    st.markdown("""
    <div class="main-header">
        <h1>💰 Personal Finance Chatbot</h1>
        <p>Your AI-powered financial advisor, tailored to your needs</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Main Page Buttons
# ------------------------------
def show_main_buttons():
    st.subheader("Navigate")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👤 Profile Setup"):
            st.session_state.page = 'profile_setup'
            st.rerun()  # Updated for new Streamlit versions

    with col2:
        if st.button("💬 Chat Assistant"):
            st.session_state.page = 'chat'
            st.rerun()  # Updated for new Streamlit versions

# ------------------------------
# Main Application
# ------------------------------
def main():
    show_main_header()
    show_main_buttons()

    current_page = st.session_state.get('page', 'home')

    if current_page == 'profile_setup':
        show_profile_setup()
    elif current_page == 'chat':
        show_chat_interface()
    elif current_page == 'home':
        st.write("Welcome! Click a button above to get started.")
    else:
        st.error("Page not found!")
        st.session_state.page = 'home'

# ------------------------------
# Initialize App
# ------------------------------
def initialize_app():
    if not os.getenv("HUGGINGFACE_API_KEY"):
        os.environ["HUGGINGFACE_API_KEY"] = "api key"

# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    initialize_app()
    main()
