from enum import Enum
from dataclasses import dataclass


# ---------- Enums ----------
class UserType(Enum):
    STUDENT = "student"
    PROFESSIONAL = "professional"


class AgeRange(Enum):
    AGE_18_25 = "18-25"
    AGE_26_35 = "26-35"
    AGE_36_50 = "36-50"
    AGE_51_ABOVE = "51+"


class IncomeLevel(Enum):
    LEVEL_0_15000 = "0-15000"
    LEVEL_15001_30000 = "15001-30000"
    LEVEL_30001_60000 = "30001-60000"
    LEVEL_60001_100000 = "60001-100000"
    LEVEL_100K_PLUS = "100000+"


class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class CommunicationStyle(Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"


# ---------- Financial Goal ----------
@dataclass
class FinancialGoal:
    goal_type: str
    target_amount: float
    timeline: str
    priority: str


# ---------- User Profile ----------
class UserProfile:
    def __init__(self):
        self.user_id = None
        self.name = None
        self.user_type: UserType | None = None
        self.age_range: AgeRange | None = None
        self.income_level: IncomeLevel | None = None
        self.financial_goals: list[FinancialGoal] = []
        self.risk_tolerance: RiskTolerance | None = None
        self.communication_preference: CommunicationStyle | None = None
        self.location = None
        self.employment_status = None
        self.monthly_expenses = None
        self.current_savings = None
        self.debt_amount = None

    # ---------- Setters with safe normalization ----------
    def set_user_type(self, value):
        if isinstance(value, UserType):
            self.user_type = value
        else:
            self.user_type = UserType(value.lower())

    def set_age_range(self, value):
        if isinstance(value, AgeRange):
            self.age_range = value
        else:
            normalized = value.replace("_", "-")
            self.age_range = AgeRange(normalized)

    def set_income_level(self, value):
        if isinstance(value, IncomeLevel):
            self.income_level = value
        else:
            normalized = value.replace("_", "-")
            self.income_level = IncomeLevel(normalized)

    def set_risk_tolerance(self, value):
        if isinstance(value, RiskTolerance):
            self.risk_tolerance = value
        else:
            self.risk_tolerance = RiskTolerance(value.lower())

    def set_communication_preference(self, value):
        if isinstance(value, CommunicationStyle):
            self.communication_preference = value
        else:
            self.communication_preference = CommunicationStyle(value.lower())

    # ---------- Goals ----------
    def add_financial_goal(self, goal_type, target_amount, timeline, priority):
        goal = FinancialGoal(goal_type, target_amount, timeline, priority)
        self.financial_goals.append(goal)

    # ---------- Profile completion ----------
    @property
    def profile_completion_percentage(self):
        required_fields = [
            "name",
            "user_type",
            "age_range",
            "income_level",
            "risk_tolerance",
            "communication_preference",
        ]
        filled = sum(bool(getattr(self, field)) for field in required_fields)
        return (filled / len(required_fields)) * 100

    def is_profile_complete(self):
        return self.profile_completion_percentage == 100
