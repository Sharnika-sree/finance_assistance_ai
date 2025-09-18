import streamlit as st
from models.user_profile import UserProfile, UserType, AgeRange, IncomeLevel, RiskTolerance, CommunicationStyle


def show_profile_setup():
    """Main profile setup form"""
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = UserProfile()

    user = st.session_state.user_profile

    st.header("👤 Profile Setup")
    st.info("Fill out your basic information so the chatbot can provide personalized financial advice.")

    # ---------- Basic Information ----------
    st.subheader("📌 Basic Information")

    user.name = st.text_input("Your Name", value=user.name or "")

    # User Type
    user_type = st.selectbox(
        "Select User Type",
        options=[UserType.STUDENT, UserType.PROFESSIONAL],
        format_func=lambda x: x.value.title(),
        index=[UserType.STUDENT, UserType.PROFESSIONAL].index(user.user_type) if user.user_type else 0
    )
    user.set_user_type(user_type)

    # Age Range
    age_range = st.selectbox(
        "Select Age Range",
        options=list(AgeRange),
        format_func=lambda x: x.value,
        index=list(AgeRange).index(user.age_range) if user.age_range else 0
    )
    user.set_age_range(age_range)

    # Income Level
    income_level = st.selectbox(
        "Select Income Level (per month in ₹)",
        options=list(IncomeLevel),
        format_func=lambda x: x.value,
        index=list(IncomeLevel).index(user.income_level) if user.income_level else 0
    )
    user.set_income_level(income_level)

    # Risk Tolerance
    risk_tolerance = st.radio(
        "Risk Tolerance",
        options=list(RiskTolerance),
        format_func=lambda x: x.value.title(),
        index=list(RiskTolerance).index(user.risk_tolerance) if user.risk_tolerance else 0
    )
    user.set_risk_tolerance(risk_tolerance)

    # Communication Style
    comm_pref = st.radio(
        "Communication Preference",
        options=list(CommunicationStyle),
        format_func=lambda x: x.value.title(),
        index=list(CommunicationStyle).index(user.communication_preference) if user.communication_preference else 0
    )
    user.set_communication_preference(comm_pref)

    # ---------- Financial Info ----------
    st.subheader("💰 Financial Information")

    user.monthly_expenses = st.number_input("Monthly Expenses (₹)", min_value=0, value=user.monthly_expenses or 0)
    user.current_savings = st.number_input("Current Savings (₹)", min_value=0, value=user.current_savings or 0)
    user.debt_amount = st.number_input("Debt Amount (₹)", min_value=0, value=user.debt_amount or 0)

    # ---------- Goals ----------
    st.subheader("🎯 Financial Goals")

    with st.expander("Add New Goal"):
        goal_type = st.text_input("Goal Type (e.g., Buy a Car, Retirement)")
        target_amount = st.number_input("Target Amount (₹)", min_value=0)
        timeline = st.text_input("Timeline (e.g., 5 years)")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])

        if st.button("➕ Add Goal"):
            if goal_type and target_amount > 0:
                user.add_financial_goal(goal_type, target_amount, timeline, priority)
                st.success(f"Goal '{goal_type}' added!")
            else:
                st.error("⚠️ Please enter a valid goal type and amount.")

    # Show existing goals
    if user.financial_goals:
        st.write("### Your Goals")
        for goal in user.financial_goals:
            st.markdown(
                f"- **{goal.goal_type}**: ₹{goal.target_amount:,.0f} | {goal.timeline} | Priority: {goal.priority}"
            )

    # ---------- Save Button ----------
    if st.button("💾 Save Profile"):
        st.session_state.user_profile = user
        st.success("✅ Profile saved successfully!")
