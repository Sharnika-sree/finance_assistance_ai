# services/watson_service.py
import os
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from models.user_profile import UserProfile, UserType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialQuery:
    original_query: str
    intent: str
    entities: List[Dict]
    keywords: List[str]
    sentiment: str
    confidence: float
    category: str  # e.g., 'savings', 'investment'

@dataclass
class PersonalizedResponse:
    content: str
    tone: str = "neutral"
    complexity_level: str = "medium"
    recommendations: List[str] = None
    additional_resources: List[str] = None
    follow_up_questions: List[str] = None

class WatsonFinanceService:
    """Mocked Watson Finance Service for personal finance chatbot"""

    def __init__(self):
        self.mock_mode = True
        self.financial_intents = {
            'savings_advice': ['save', 'saving', 'emergency fund'],
            'investment_advice': ['invest', 'portfolio', 'stocks', 'bonds', 'retirement'],
            'budgeting_help': ['budget', 'expense', 'spending', 'monthly', 'track'],
            'debt_management': ['debt', 'loan', 'credit', 'pay off', 'consolidate'],
            'tax_planning': ['tax', 'deduction', 'filing', 'refund'],
            'financial_education': ['learn', 'explain', 'what is', 'how does']
        }
        logger.info("WatsonFinanceService initialized (mock mode).")

    # ---------------------------
    # Query Analysis
    # ---------------------------
    def analyze_financial_query(self, query: str, user_profile: UserProfile) -> FinancialQuery:
        query_lower = query.lower()
        intent, category = self._classify_financial_intent(query_lower, [query_lower])
        sentiment = 'positive' if 'good' in query_lower or 'great' in query_lower else 'neutral'
        return FinancialQuery(
            original_query=query,
            intent=intent,
            entities=[],
            keywords=query_lower.split()[:5],
            sentiment=sentiment,
            confidence=0.7,
            category=category
        )

    def _classify_financial_intent(self, query: str, keywords: List[str]) -> tuple[str, str]:
        for intent, terms in self.financial_intents.items():
            if any(term in query for term in terms):
                return intent, intent.split('_')[0]
        return 'general_financial_advice', 'general'

    # ---------------------------
    # Responses
    # ---------------------------
    def generate_personalized_response(self, query: FinancialQuery, user_profile: UserProfile) -> PersonalizedResponse:
        recommendations = [
            "Start small and track your progress.",
            "Consider automating savings.",
            "Review goals every 3-6 months."
        ]
        follow_ups = [
            "How much should I save per month?",
            "What investment options are suitable for me?"
        ]
        return PersonalizedResponse(
            content=f"Here's some advice based on your question: '{query.original_query}'",
            tone="friendly",
            complexity_level="basic",
            recommendations=recommendations,
            additional_resources=["https://www.investopedia.com", "https://www.moneycontrol.com"],
            follow_up_questions=follow_ups
        )

    # ---------------------------
    # Budget Summary
    # ---------------------------
    def generate_budget_summary(self, financial_data: Dict[str, Any], user_profile: UserProfile) -> str:
        monthly_expenses = user_profile.monthly_expenses or 0
        current_savings = user_profile.current_savings or 0
        return f"📊 Budget Summary:\nMonthly Expenses: ₹{monthly_expenses}\nCurrent Savings: ₹{current_savings}"

    # ---------------------------
    # Spending Insights
    # ---------------------------
    def get_spending_insights(self, financial_data: Dict[str, Any], user_profile: UserProfile) -> List[str]:
        # Mock insights
        return [
            "You spend 30% of your income on food.",
            "Entertainment costs can be reduced by 10%."
        ]

    # ---------------------------
    # Translation placeholder
    # ---------------------------
    def translate_text(self, text: str, language: str) -> str:
        # Mock translation: simply return original text
        return text

