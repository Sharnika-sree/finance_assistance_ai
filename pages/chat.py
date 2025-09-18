# pages/chat.py
import streamlit as st
from datetime import datetime
from typing import Dict
from models.user_profile import UserProfile
from services.huggingface_service import HuggingFaceFinanceService  # ✅ Correct import

def show_chat_interface():
    st.title("💬 Personal Finance Assistant")

    # Initialize Hugging Face AI
    if "hf_service" not in st.session_state:  # updated variable name
        with st.spinner("Connecting to AI assistant..."):
            st.session_state.hf_service = HuggingFaceFinanceService()

    # Check if user profile exists
    if "user_profile" not in st.session_state or not st.session_state.user_profile.is_profile_complete():
        st.warning("⚠️ Please complete your profile first for personalized advice!")
        if st.button("Go to Profile Setup"):
            st.session_state.page = "profile_setup"
            st.rerun()
        return

    user_profile = st.session_state.user_profile
    hf_service = st.session_state.hf_service  # updated variable name

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        welcome_msg = get_welcome_message(user_profile)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome_msg,
            "timestamp": datetime.now()
        })

    # Sidebar with user info and quick actions
    show_chat_sidebar(user_profile, hf_service)

    # Main chat interface
    show_chat_messages()

    # Chat input
    handle_chat_input(hf_service, user_profile)

def get_welcome_message(user_profile: UserProfile) -> str:
    """Generate personalized welcome message"""
    name = user_profile.name or "there"

    if user_profile.user_type.value == "student":
        return f"""
        Hi {name}! 👋 Welcome to your personal finance assistant!

        As a student, I can help you with:
        🎯 Building your first budget
        💰 Smart saving strategies
        📚 Managing student loans
        🍕 Cutting expenses without losing fun
        📈 Basic investing concepts

        What financial question can I help you with today?
        """
    else:
        return f"""
        Hello {name}! 👋 Welcome to your personal finance assistant!

        As a professional, I can help you with:
        💼 Investment strategies
        🏠 Home buying & mortgage planning
        📊 Tax optimization
        🎯 Retirement planning
        💳 Debt management

        What financial topic would you like to explore today?
        """

def show_chat_sidebar(user_profile: UserProfile, hf_service: HuggingFaceFinanceService):
    """Sidebar with quick actions & suggestions"""
    st.sidebar.header(f"👤 {user_profile.name or 'User'}")
    st.sidebar.write(f"**Type:** {user_profile.user_type.value.title() if user_profile.user_type else 'Unknown'}")
    st.sidebar.write(f"**Profile:** {user_profile.profile_completion_percentage:.0f}% complete")

    # Quick actions
    st.sidebar.subheader("🚀 Quick Actions")
    if st.sidebar.button("📊 Budgeting Tips"):
        add_message_to_chat("assistant", "A good budgeting rule is 50/30/20: 50% needs, 30% wants, 20% savings.")
        st.rerun()
    if st.sidebar.button("💡 Saving Strategies"):
        add_message_to_chat("assistant", "Start by saving 20% of your income, and build an emergency fund.")
        st.rerun()

    # Suggested questions
    st.sidebar.subheader("💭 Suggested Questions")
    suggestions = [
        "How much should I save each month?",
        "What is a good way to reduce expenses?",
        "Should I invest in mutual funds or stocks?",
        "How can I plan for retirement early?"
    ]
    for idx, suggestion in enumerate(suggestions):
        if st.sidebar.button(f"💬 {suggestion}", key=f"suggestion_{idx}"):
            add_message_to_chat("user", suggestion)
            answer = hf_service.analyze_financial_query(suggestion, user_profile)  # updated method call
            personalized_response = hf_service.generate_personalized_response(answer, user_profile)
            add_message_to_chat("assistant", personalized_response.content)
            st.rerun()

    # Clear chat
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

def show_chat_messages():
    """Display chat history"""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
                st.caption(f"_{message['timestamp'].strftime('%H:%M')}_")
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                st.caption(f"_{message['timestamp'].strftime('%H:%M')}_")

def handle_chat_input(hf_service: HuggingFaceFinanceService, user_profile: UserProfile):
    """Process user input"""
    if user_input := st.chat_input("Ask me anything about personal finance..."):
        add_message_to_chat("user", user_input)
        with st.spinner("Thinking..."):
            query_analysis = hf_service.analyze_financial_query(user_input, user_profile)
            response = hf_service.generate_personalized_response(query_analysis, user_profile)
        add_message_to_chat("assistant", response.content)
        st.rerun()

def add_message_to_chat(role: str, content: str, extras: Dict = None):
    """Save chat message in history"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    if extras:
        message.update(extras)
    st.session_state.chat_history.append(message)
