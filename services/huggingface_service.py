# services/huggingface_service.py - CORRECTED VERSION
import os
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass



# Standard library imports
import re

# Hugging Face imports (with fallback handling)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from transformers import AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Transformers not fully available: {e}")
    TRANSFORMERS_AVAILABLE = False

# Local imports - CORRECTED
from models.user_profile import UserProfile, UserType, RiskTolerance, CommunicationStyle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialQuery:
    """Structure for processed financial queries"""
    original_query: str
    intent: str
    entities: List[Dict]
    keywords: List[str]
    sentiment: str
    confidence: float
    category: str

@dataclass
class PersonalizedResponse:
    """Structure for AI-generated responses"""
    content: str
    tone: str
    complexity_level: str
    recommendations: List[str]
    additional_resources: List[str]
    follow_up_questions: List[str]

class HuggingFaceFinanceService:
    """
    Hugging Face-powered financial advice service with demographic awareness
    """
   
    def __init__(self):
        """Initialize Hugging Face models and services"""
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.api_url = "https://api-inference.huggingface.co/models"
       
        # Set lightweight mode for initial setup
        self.lightweight_mode = True
       
        # Model configurations
        self.models = {
            'sentiment': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'classification': 'microsoft/DialoGPT-medium',
            'generation': 'microsoft/DialoGPT-medium',
            'financial_qa': 'deepset/roberta-base-squad2'
        }
       
        # Financial knowledge base
        self.financial_intents = {
            'savings_advice': ['save', 'saving', 'savings', 'emergency fund', 'rainy day'],
            'investment_advice': ['invest', 'investment', 'portfolio', 'stocks', 'bonds', 'retirement', '401k'],
            'budgeting_help': ['budget', 'expense', 'spending', 'monthly', 'track', 'money'],
            'debt_management': ['debt', 'loan', 'credit', 'pay off', 'consolidate', 'student loan'],
            'tax_planning': ['tax', 'deduction', 'IRS', 'filing', 'refund', 'tax return'],
            'financial_education': ['learn', 'explain', 'what is', 'how does', 'understand']
        }
       
        # Response templates by user type
        self.response_templates = {
            UserType.STUDENT: {
                'tone': 'friendly and educational',
                'complexity': 'simple',
                'focus_areas': ['budgeting basics', 'student loans', 'part-time income', 'saving tips']
            },
            UserType.PROFESSIONAL: {
                'tone': 'professional and detailed',
                'complexity': 'advanced',
                'focus_areas': ['investment strategies', 'tax optimization', 'retirement planning', 'portfolio management']
            }
        }
       
        # Initialize models
        self._initialize_models()
   
    def _initialize_models(self):
        """Initialize Hugging Face models with fallback for connectivity issues"""
        try:
            logger.info("Initializing Hugging Face models...")
           
            if self.lightweight_mode or not TRANSFORMERS_AVAILABLE:
                logger.info("Running in lightweight mode - using fallback methods")
                self.sentiment_analyzer = None
                self.text_classifier = None
                self.conversation_model = None
                self.qa_model = None
                return
           
            # Only try to load models if not in lightweight mode
            logger.info("Attempting to load full AI models...")
           
            # Initialize sentiment analysis with timeout
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                logger.info("Sentiment analyzer initialized")
            except Exception as e:
                logger.warning(f"Sentiment analyzer failed: {e}, using fallback")
                self.sentiment_analyzer = None
           
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            self._initialize_fallback_models()
   
    def _initialize_fallback_models(self):
        """Initialize simpler models if main models fail"""
        logger.warning("Using fallback models - all AI features will use rule-based approaches")
        self.sentiment_analyzer = None
        self.text_classifier = None
        self.conversation_model = None
        self.qa_model = None
   
    def analyze_financial_query(self, query: str, user_profile: UserProfile) -> FinancialQuery:
        """
        Analyze user's financial query using Hugging Face models or fallback methods
        """
        try:
            # Sentiment analysis
            sentiment_result = self._analyze_sentiment(query)
           
            # Intent classification
            intent, category = self._classify_intent(query)
           
            # Keyword extraction
            keywords = self._extract_keywords(query)
           
            # Entity extraction (simplified)
            entities = self._extract_entities(query)
           
            return FinancialQuery(
                original_query=query,
                intent=intent,
                entities=entities,
                keywords=keywords,
                sentiment=sentiment_result['label'].lower(),
                confidence=sentiment_result['score'],
                category=category
            )
           
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return self._fallback_query_analysis(query)
   
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using Hugging Face model or fallback"""
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(text)[0]
                # Convert labels to standard format
                label_mapping = {
                    'LABEL_0': 'negative',
                    'LABEL_1': 'neutral',
                    'LABEL_2': 'positive',
                    'NEGATIVE': 'negative',
                    'NEUTRAL': 'neutral',
                    'POSITIVE': 'positive'
                }
                result['label'] = label_mapping.get(result['label'], result['label'].lower())
                return result
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
       
        # Fallback sentiment analysis using simple keywords
        return self._fallback_sentiment_analysis(text)
   
    def _fallback_sentiment_analysis(self, text: str) -> Dict:
        """Simple rule-based sentiment analysis"""
        text_lower = text.lower()
       
        positive_words = ['good', 'great', 'excited', 'happy', 'awesome', 'excellent', 'love', 'like', 'want', 'help']
        negative_words = ['bad', 'terrible', 'worried', 'concerned', 'problem', 'debt', 'struggling', 'confused', 'lost']
       
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
       
        if positive_count > negative_count:
            return {'label': 'positive', 'score': 0.7}
        elif negative_count > positive_count:
            return {'label': 'negative', 'score': 0.7}
        else:
            return {'label': 'neutral', 'score': 0.6}
   
    def _classify_intent(self, query: str) -> tuple:
        """Classify financial intent using keyword matching"""
        query_lower = query.lower()
       
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.financial_intents.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
       
        if intent_scores:
            # Get the intent with highest score
            best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            category = best_intent.split('_')[0]
            return best_intent, category
       
        return 'general_financial_advice', 'general'
   
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using simple NLP techniques"""
        try:
            # Simple keyword extraction using word frequency and financial terms
            words = re.findall(r'\b\w+\b', text.lower())
           
            # Financial keywords
            financial_terms = [
                'save', 'saving', 'savings', 'invest', 'investment', 'budget', 'money',
                'debt', 'loan', 'credit', 'tax', 'retirement', 'emergency', 'fund',
                'stock', 'bond', 'portfolio', 'income', 'expense', 'financial',
                'dollar', 'cash', 'bank', 'account', '401k', 'ira'
            ]
           
            keywords = [word for word in words if word in financial_terms]
            return keywords[:5]  # Return top 5 keywords
           
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return text.split()[:3]  # Fallback to first 3 words
   
    def _extract_entities(self, text: str) -> List[Dict]:
        """Simple entity extraction for financial terms"""
        entities = []
        text_lower = text.lower()
       
        # Define entity patterns
        entity_patterns = {
            'MONEY': ['$', 'dollar', 'money', 'income', 'salary'],
            'PERCENTAGE': ['%', 'percent', 'rate'],
            'TIME': ['month', 'year', 'monthly', 'annual', 'weekly'],
            'FINANCIAL_PRODUCT': ['401k', 'ira', 'savings account', 'credit card', 'loan']
        }
       
        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    entities.append({
                        'entity': entity_type,
                        'value': pattern,
                        'confidence': 0.8
                    })
       
        return entities
   
    def _fallback_query_analysis(self, query: str) -> FinancialQuery:
        """Fallback analysis when models fail"""
        intent, category = self._classify_intent(query)
        sentiment = self._fallback_sentiment_analysis(query)
       
        return FinancialQuery(
            original_query=query,
            intent=intent,
            entities=[],
            keywords=self._extract_keywords(query),
            sentiment=sentiment['label'],
            confidence=sentiment['score'],
            category=category
        )
   
    def generate_personalized_response(self, query: FinancialQuery, user_profile: UserProfile) -> PersonalizedResponse:
        """
        Generate demographic-aware financial advice
        """
        try:
            # Generate response based on user type
            if user_profile.user_type == UserType.STUDENT:
                response = self._generate_student_response(query, user_profile)
            elif user_profile.user_type == UserType.PROFESSIONAL:
                response = self._generate_professional_response(query, user_profile)
            else:
                response = self._generate_general_response(query, user_profile)
           
            return response
           
        except Exception as e:
            logger.error(f"Error generating personalized response: {e}")
            return self._generate_fallback_response(query)
   
    def _generate_student_response(self, query: FinancialQuery, user_profile: UserProfile) -> PersonalizedResponse:
        """Generate student-focused financial advice"""
       
        base_responses = {
            'savings': {
                'content': f"""
                Hey {user_profile.name or 'there'}! 🎓 Great question about saving money as a student!

                Here's my advice tailored for students:

                💡 **Start Small**: Even $25-50 per month makes a huge difference over time!
                🎯 **Emergency Fund First**: Try to build a small emergency fund of $500-1000
                📱 **Use Student Discounts**: Take advantage of student pricing everywhere
                💰 **Part-time Job**: Consider a campus job or paid internship

                **Quick Student Tips:**
                • Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings
                • Try apps like Mint or YNAB (free for students!)
                • Look for high-yield savings accounts with no minimums
                • Avoid lifestyle inflation when you get financial aid refunds
                """,
                'recommendations': [
                    "Open a high-yield savings account with no minimum balance",
                    "Set up automatic transfers of $25-50 per month",
                    "Track spending for one month to identify money leaks",
                    "Apply for student discounts on subscriptions and services"
                ],
                'resources': [
                    "Student Budget Template",
                    "Campus Financial Counseling Services",
                    "Free Financial Literacy Apps"
                ],
                'follow_ups': [
                    "What's your biggest monthly expense besides tuition?",
                    "Do you have any income from part-time work?",
                    "Would you like help setting up your first budget?"
                ]
            },
            'investment': {
                'content': f"""
                Awesome that you're thinking about investing as a student! 📈

                **Why Starting Early is Your Superpower:**
                🚀 Time is your biggest advantage - compound interest is magical!
                💰 Even $10-50/month can grow to thousands over time
                📚 Learning about investing now sets you up for life

                **Student-Friendly Investment Options:**
                • **Roth IRA**: Perfect for students - tax-free growth!
                • **Target-Date Funds**: Simple, diversified, hands-off
                • **Index Funds**: Low fees, broad market exposure
                • **Micro-investing Apps**: Start with spare change (Acorns, Stash)

                **Simple Strategy:**
                1. Build $500 emergency fund first
                2. Open a Roth IRA with Fidelity/Vanguard (no minimums!)
                3. Invest in a target-date fund matching your graduation + 40 years
                4. Invest any financial aid refunds or gift money
                """,
                'recommendations': [
                    "Open a Roth IRA - perfect for students with low income",
                    "Start with a target-date fund for simplicity",
                    "Use micro-investing apps to begin with small amounts",
                    "Take a free online investing course"
                ],
                'resources': [
                    "Student Investment Guide",
                    "Roth IRA Comparison Chart",
                    "Free Investment Courses"
                ],
                'follow_ups': [
                    "Do you have any earned income this year?",
                    "What's your investment timeline?",
                    "Are you interested in learning about index funds?"
                ]
            },
            'budgeting': {
                'content': f"""
                Perfect time to learn budgeting as a student! 📊

                **Student Budget Basics:**
                🏫 **Fixed Costs**: Tuition, rent, meal plan, textbooks
                🎯 **Variable Costs**: Food, entertainment, transportation, personal items
                💰 **Income Sources**: Part-time job, financial aid, family support

                **Simple Student Budget Method:**
                1. List all monthly income sources
                2. List all fixed expenses (things you must pay)
                3. Set aside $50-100 for savings/emergency fund
                4. Divide remaining money: 70% needs, 30% wants

                **Money-Saving Student Hacks:**
                • Buy used textbooks or rent them
                • Use student discounts everywhere
                • Cook simple meals instead of eating out
                • Take advantage of free campus activities
                """,
                'recommendations': [
                    "Use a budgeting app designed for students",
                    "Track every expense for one week to see patterns",
                    "Set up a separate savings account",
                    "Look for student discounts on everything you buy"
                ]
            }
        }
       
        category = query.category
        response_data = base_responses.get(category, base_responses.get('savings', base_responses['savings']))
       
        return PersonalizedResponse(
            content=response_data['content'].strip(),
            tone="friendly and educational",
            complexity_level="simple",
            recommendations=response_data.get('recommendations', []),
            additional_resources=response_data.get('resources', []),
            follow_up_questions=response_data.get('follow_ups', [])
        )
   
    def _generate_professional_response(self, query: FinancialQuery, user_profile: UserProfile) -> PersonalizedResponse:
        """Generate professional-focused financial advice"""
       
        base_responses = {
            'investment': {
                'content': f"""
                Excellent question about investment strategy! 💼

                Based on your profile as a working professional, here's a comprehensive approach:

                **Portfolio Allocation Strategy:**
                🎯 **Age-Based Rule**: Consider 100 - your age = stock percentage
                ⚖️ **Risk Tolerance**: Your {user_profile.risk_tolerance.value if user_profile.risk_tolerance else 'moderate'} profile suggests balanced growth
                🌍 **Diversification**: Mix of domestic/international, large/small cap

                **Tax-Advantaged Account Priority:**
                1. **401(k) Match**: Contribute enough for full employer match (free money!)
                2. **Roth IRA**: $6,000/year if income allows
                3. **Additional 401(k)**: Up to $22,500/year limit
                4. **Taxable Account**: For additional investments

                **Advanced Strategies:**
                • **Tax-Loss Harvesting**: Offset gains with strategic losses
                • **Asset Location**: Hold tax-inefficient investments in tax-advantaged accounts
                • **Rebalancing**: Quarterly review and rebalance to target allocation
                """,
                'recommendations': [
                    "Maximize 401(k) employer match immediately",
                    "Open and fund Roth IRA if income eligible",
                    "Consider low-cost index funds (VTSAX, FXNAX)",
                    "Implement tax-loss harvesting strategy",
                    "Review and rebalance portfolio quarterly"
                ],
                'resources': [
                    "Advanced Portfolio Management Tools",
                    "Tax-Loss Harvesting Guide",
                    "Professional Financial Planning Resources"
                ]
            },
            'savings': {
                'content': f"""
                Strategic savings approach for professionals: 💰

                **Savings Rate Targets:**
                🎯 **Emergency Fund**: 3-6 months expenses in high-yield savings
                📈 **Savings Rate**: Aim for 20% of gross income
                🏠 **Goal-Based Saving**: Separate accounts for different objectives

                **High-Yield Account Strategy:**
                • Online banks typically offer 4-5% APY
                • Consider CD ladders for portion of emergency fund
                • Money market accounts for easy access

                **Advanced Savings Techniques:**
                • **Automated Transfers**: Set up automatic savings on payday
                • **Pay Yourself First**: Save before discretionary spending
                • **Bonus Strategy**: Save 50% of bonuses, raises, tax refunds
                """
            }
        }
       
        category = query.category
        response_data = base_responses.get(category, base_responses.get('investment', base_responses['investment']))
       
        return PersonalizedResponse(
            content=response_data['content'].strip(),
            tone="professional and detailed",
            complexity_level="advanced",
            recommendations=response_data.get('recommendations', []),
            additional_resources=response_data.get('resources', []),
            follow_up_questions=response_data.get('follow_ups', [
                "What's your current asset allocation?",
                "Are you maximizing all tax-advantaged accounts?",
                "Would you like specific fund recommendations?"
            ])
        )
   
    def _generate_general_response(self, query: FinancialQuery, user_profile: UserProfile) -> PersonalizedResponse:
        """Generate general financial advice"""
        return PersonalizedResponse(
            content="Thanks for your question! I'd be happy to provide personalized advice once you complete your profile setup. This helps me tailor recommendations to your specific situation and goals.",
            tone="helpful",
            complexity_level="medium",
            recommendations=["Complete your user profile for personalized advice"],
            additional_resources=["Financial Planning Basics"],
            follow_up_questions=["Would you like to complete your profile setup?"]
        )
   
    def _generate_fallback_response(self, query: FinancialQuery) -> PersonalizedResponse:
        """Generate fallback response when other methods fail"""
        return PersonalizedResponse(
            content="I'm here to help with your financial questions! Could you please rephrase your question or be more specific about what you'd like to know?",
            tone="helpful",
            complexity_level="simple",
            recommendations=["Try asking about savings, investments, budgeting, or debt management"],
            additional_resources=["Financial FAQ"],
            follow_up_questions=["What specific financial topic would you like help with?"]
        )
   
    def generate_budget_summary(self, financial_data: Dict[str, Any], user_profile: UserProfile) -> str:
        """Generate budget summary with demographic awareness"""
        try:
            user_type = user_profile.user_type
           
            if user_type == UserType.STUDENT:
                return self._generate_student_budget_summary(financial_data, user_profile)
            elif user_type == UserType.PROFESSIONAL:
                return self._generate_professional_budget_summary(financial_data, user_profile)
            else:
                return self._generate_general_budget_summary(financial_data)
       
        except Exception as e:
            logger.error(f"Error generating budget summary: {e}")
            return "Unable to generate budget summary at this time. Please try again later."
   
    def _generate_student_budget_summary(self, financial_data: Dict, user_profile: UserProfile) -> str:
        """Generate student-friendly budget summary"""
        monthly_expenses = user_profile.monthly_expenses or 0
        current_savings = user_profile.current_savings or 0
       
        savings_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
       
        summary = f"""
📊 **Your Student Budget Overview**

Hey {user_profile.name or 'there'}! Here's your financial snapshot:

💰 **Monthly Expenses**: ${monthly_expenses:,.0f}
🏦 **Current Savings**: ${current_savings:,.0f}
{"🎯 **Emergency Coverage**: {:.1f} months".format(savings_months) if savings_months > 0 else "🎯 **Emergency Fund**: Not yet established"}

**🎓 Student-Specific Tips:**
• Use student discounts everywhere (Spotify, Adobe, Amazon Prime)
• Consider meal prep to reduce food costs
• Look for free campus activities for entertainment
• Apply for scholarships and grants to reduce loan burden

**🎯 Goal Tracking:**"""
       
        for goal in user_profile.financial_goals:
            if monthly_expenses > 0:
                monthly_saving_potential = max(monthly_expenses * 0.1, 25)
                months_to_goal = goal.target_amount / monthly_saving_potential
                summary += f"\n• {goal.goal_type.title()}: ${goal.target_amount:,.0f} (~{months_to_goal:.0f} months)"
       
        return summary.strip()
   
    def _generate_professional_budget_summary(self, financial_data: Dict, user_profile: UserProfile) -> str:
        """Generate professional-level budget summary"""
        monthly_expenses = user_profile.monthly_expenses or 0
        current_savings = user_profile.current_savings or 0
        debt_amount = user_profile.debt_amount or 0
       
        emergency_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
       
        summary = f"""
📈 **Professional Financial Dashboard**

**💼 Financial Health Metrics:**
• Monthly Expenses: ${monthly_expenses:,.0f}
• Current Savings: ${current_savings:,.0f}
• Total Debt: ${debt_amount:,.0f}
• Emergency Fund: {emergency_months:.1f} months coverage

**🎯 Strategic Recommendations:**
• Review and maximize tax-advantaged account contributions
• Consider meeting with a fee-only financial planner
• Implement automated savings and investment strategies"""
       
        return summary.strip()
   
    def _generate_general_budget_summary(self, financial_data: Dict) -> str:
        """Generate basic budget summary"""
        return """
📊 **Budget Summary**

Complete your profile to get personalized budget insights and recommendations!
"""
   
    def get_spending_insights(self, spending_data: Dict, user_profile: UserProfile) -> List[str]:
        """Generate spending insights and recommendations"""
        insights = []
       
        try:
            if user_profile.user_type == UserType.STUDENT:
                insights = [
                    "🍕 Consider meal prepping to reduce food costs by 30-40%",
                    "📚 Use library resources and digital textbooks to save on books",
                    "🚌 Look into student transit passes for transportation savings",
                    "🎮 Take advantage of free campus activities for entertainment",
                    "📱 Bundle student discounts for streaming services",
                    "☕ Limit coffee shop visits - make coffee at home/dorm"
                ]
            elif user_profile.user_type == UserType.PROFESSIONAL:
                insights = [
                    "🏠 Housing should be under 28% of gross income for optimal health",
                    "🚗 Consider car-sharing or public transit to reduce costs",
                    "📱 Review and cancel unused subscription services monthly",
                    "🍽️ Meal planning can save $200-400/month vs eating out",
                    "💼 Maximize tax-deductible professional development expenses",
                    "⚡ Energy-efficient upgrades can reduce utility costs"
                ]
            else:
                insights = [
                    "💰 Track your spending for one month to identify patterns",
                    "🎯 Set up automatic savings transfers on payday",
                    "📊 Use the 50/30/20 budgeting rule as a starting point",
                    "💳 Pay off high-interest debt before investing"
                ]
       
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights = ["Complete your profile for personalized spending insights!"]
       
        return insights[:6]

# Example usage and testing
if __name__ == "__main__":
    # Test the service
    print("Testing HuggingFace Finance Service...")
   
    try:
        service = HuggingFaceFinanceService()
        print("✅ Service created successfully")
       
        # Create test user
        user = UserProfile()
        user.name = "Test User"
        user.set_user_type("student")
       
        # Test query
        query = service.analyze_financial_query("How should I save money?", user)
        print(f"✅ Query analyzed: {query.intent}")
       
        # Test response
        response = service.generate_personalized_response(query, user)
        print(f"✅ Response generated: {len(response.content)} chars")
       
    except Exception as e:
        print(f"❌ Test failed: {e}")