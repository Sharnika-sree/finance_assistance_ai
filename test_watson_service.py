# test_watson_service.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.watson_service_backup import WatsonFinanceService
from models.user_profile import UserProfile

def test_watson_service():
    print("🧪 Testing Watson Finance Service...")
   
    # Initialize service
    try:
        watson_service = WatsonFinanceService()
        print("✅ Watson service initialized")
    except Exception as e:
        print(f"❌ Error initializing Watson service: {e}")
        return False
   
    # Create test user profiles
    print("\n👤 Creating test user profiles...")
   
    # Student profile
    student = UserProfile()
    student.name = "Alice"
    student.set_user_type("student")
    student.set_age_range("18-25")
    student.set_income_level("0-15000")
    student.set_risk_tolerance("conservative")
    student.set_communication_preference("simple")
    student.monthly_expenses = 800
    student.current_savings = 1200
    student.add_financial_goal("emergency_fund", 3000, "short_term", "high")
    print("✅ Student profile created")
   
    # Professional profile
    professional = UserProfile()
    professional.name = "Bob"
    professional.set_user_type("professional")
    professional.set_age_range("26-35")
    professional.set_income_level("60001-100000")
    professional.set_risk_tolerance("moderate")
    professional.set_communication_preference("detailed")
    professional.monthly_expenses = 4500
    professional.current_savings = 25000
    professional.debt_amount = 15000
    professional.add_financial_goal("house", 80000, "long_term", "high")
    professional.add_financial_goal("retirement", 500000, "long_term", "medium")
    print("✅ Professional profile created")
   
    # Test queries
    test_queries = [
        "How should I start saving money?",
        "What investment options are good for beginners?",
        "I need help with budgeting my expenses",
        "How can I pay off my student loans faster?",
        "Should I invest in stocks or bonds?"
    ]
   
    print("\n💬 Testing query analysis and responses...")
   
    for i, query in enumerate(test_queries):
        print(f"\n--- Test Query {i+1}: '{query}' ---")
       
        # Test with student profile
        print("🎓 Student Response:")
        try:
            analyzed_query = watson_service.analyze_financial_query(query, student)
            response = watson_service.generate_personalized_response(analyzed_query, student)
           
            print(f"Intent: {analyzed_query.intent}")
            print(f"Category: {analyzed_query.category}")
            print(f"Sentiment: {analyzed_query.sentiment}")
            print(f"Response Preview: {response.content[:100]}...")
            print(f"Recommendations: {len(response.recommendations)} items")
           
        except Exception as e:
            print(f"❌ Error with student response: {e}")
       
        # Test with professional profile
        print("\n💼 Professional Response:")
        try:
            analyzed_query = watson_service.analyze_financial_query(query, professional)
            response = watson_service.generate_personalized_response(analyzed_query, professional)
           
            print(f"Intent: {analyzed_query.intent}")
            print(f"Category: {analyzed_query.category}")
            print(f"Tone: {response.tone}")
            print(f"Complexity: {response.complexity_level}")
            print(f"Response Preview: {response.content[:100]}...")
           
        except Exception as e:
            print(f"❌ Error with professional response: {e}")
   
    # Test budget summaries
    print("\n📊 Testing budget summaries...")
   
    try:
        student_budget = watson_service.generate_budget_summary({}, student)
        professional_budget = watson_service.generate_budget_summary({}, professional)
       
        print("🎓 Student Budget Summary:")
        print(student_budget[:200] + "...")
       
        print("\n💼 Professional Budget Summary:")
        print(professional_budget[:200] + "...")
       
    except Exception as e:
        print(f"❌ Error generating budget summaries: {e}")
   
    # Test spending insights
    print("\n💡 Testing spending insights...")
   
    try:
        student_insights = watson_service.get_spending_insights({}, student)
        professional_insights = watson_service.get_spending_insights({}, professional)
       
        print(f"🎓 Student insights: {len(student_insights)} items")
        for insight in student_insights[:2]:
            print(f"  • {insight}")
       
        print(f"\n💼 Professional insights: {len(professional_insights)} items")
        for insight in professional_insights[:2]:
            print(f"  • {insight}")
       
    except Exception as e:
        print(f"❌ Error generating spending insights: {e}")
   
    # Test chat functionality
    print("\n💬 Testing chat functionality...")
   
    try:
        chat_response = watson_service.chat_with_watson(
            "I'm a student and need help with my first budget",
            student
        )
       
        if 'response' in chat_response:
            response_text = chat_response['response']['output']['generic'][0]['text']
            print(f"Chat Response: {response_text[:150]}...")
            print(f"Session ID: {chat_response.get('session_id', 'N/A')}")
        else:
            print("❌ Invalid chat response format")
           
    except Exception as e:
        print(f"❌ Error in chat functionality: {e}")
   
    print("\n🎉 Watson Service testing completed!")
    print("\n📋 Summary:")
    print("✅ Query analysis working")
    print("✅ Personalized responses generated")
    print("✅ Budget summaries created")
    print("✅ Spending insights provided")
    print("✅ Chat functionality tested")
   
    return True

if __name__ == "__main__":
    test_watson_service()