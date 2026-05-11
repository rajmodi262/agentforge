"""StartupOS AI — Claude API Service with Mock Mode

CRITICAL: Mock mode is the #1 most important feature for development.
Without it, $5 API credits will be burned in 2 days of testing.
"""

import json
import time
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================
# MOCK RESPONSES — Generated from 1 real Claude API run
# These are used during development to avoid burning API credits
# ============================================================

MOCK_RESPONSES = {
    "CEO Agent": {
        "startup_name_suggestion": "HostelBites",
        "problem_statement": "College hostel students in India face a critical nutrition gap — canteen food is repetitive and unhealthy, outside food is expensive and inconsistent, and cooking facilities are nonexistent. Students spend ₹3000-5000/month on food with poor nutritional outcomes.",
        "solution_description": "A subscription meal kit service delivering pre-portioned, recipe-ready meal kits to college hostels. Each kit includes fresh ingredients, spice packets, and a 10-minute recipe card — designed for students with access to only a kettle or induction plate.",
        "target_user_primary": "College hostel students aged 18-22 in tier-1 Indian cities (Delhi, Mumbai, Pune, Bangalore)",
        "target_user_secondary": "PG accommodation residents aged 22-28 in urban India",
        "business_model_type": "D2C",
        "revenue_model": "Weekly/monthly subscription with per-meal pricing (₹45-75 per meal)",
        "geographic_focus": "India — starting with Pune university cluster",
        "industry_vertical": "FoodTech / Meal Kit Delivery",
        "stage_assumption": "Pre-seed",
        "key_assumptions": [
            "Students are willing to pay ₹45-75 per meal for convenience",
            "Hostel administration will allow delivery to common areas",
            "Students have access to at least a kettle or induction plate"
        ],
        "top_risks": [
            "Cold chain logistics for fresh ingredients in Indian summers",
            "Student price sensitivity — ₹45/meal may still feel expensive",
            "Competition from Zomato/Swiggy daily subscriptions"
        ],
        "questions_for_research_agent": [
            "What is the current meal kit market size in India and growth rate?",
            "Who are the existing meal kit competitors in India (FreshMenu, EatFit, etc.)?",
            "What do college students currently spend on food monthly?"
        ],
        "questions_for_marketing_agent": [
            "What channels reach college students most effectively?",
            "What viral/referral mechanisms work in college environments?",
            "How should we position against Zomato/Swiggy subscriptions?"
        ],
        "questions_for_developer_agent": [
            "What tech stack handles subscription management + delivery logistics?",
            "Do we need a mobile app or is a PWA sufficient for MVP?",
            "What delivery tracking solution works at lowest cost?"
        ],
        "questions_for_finance_agent": [
            "What is the unit economics at ₹55/meal with 30% food cost?",
            "How many subscribers do we need to break even monthly?",
            "What is the expected CAC for college student acquisition?"
        ],
        "executive_brief": "HostelBites is a D2C subscription meal kit service targeting the 8M+ college hostel students in India who are underserved by existing food delivery platforms. The service delivers pre-portioned, easy-cook meal kits at ₹45-75 per meal — cheaper than Swiggy/Zomato orders but healthier than canteen food. Starting with the Pune university cluster (50K+ hostel students), the company targets a ₹280M addressable market with a land-and-expand strategy to 10 cities in 18 months."
    },

    "Research Agent": {
        "market_size": {
            "tam": "$4.2B — India online food delivery market (2025)",
            "sam": "$280M — College student food subscription segment",
            "som": "$2.8M — Pune university cluster (1% of SAM in Year 1)",
            "source": "RedSeer Consulting, Statista India Food Delivery Report 2024"
        },
        "market_growth_rate": "28% CAGR for Indian meal kit segment (2023-2028), source: IMARC Group",
        "market_trends": [
            "Health-conscious eating among Gen Z driving premium food subscriptions",
            "Cloud kitchen model reducing delivery costs by 40%",
            "Subscription fatigue — users prefer flexibility over rigid plans"
        ],
        "competitors": [
            {"name": "EatFit (by CureFit)", "description": "Health-focused meal subscriptions", "funding": "$180M total (CureFit)", "weakness": "Not targeting college segment, ₹150+ per meal"},
            {"name": "FreshMenu", "description": "Cloud kitchen meal delivery", "funding": "$21M", "weakness": "No subscription model, not in college areas"},
            {"name": "Hostel Kitchen (startup)", "description": "Tiffin service for PG residents", "funding": "Bootstrapped", "weakness": "No tech platform, limited to 2 cities"},
            {"name": "Zomato Daily", "description": "Daily meal subscription by Zomato", "funding": "Part of Zomato ($2.1B)", "weakness": "Expensive (₹100+/meal), not optimized for hostel delivery"}
        ],
        "customer_personas": [
            {"name": "The Busy Engineering Student", "description": "3rd year CS student, 8 AM to 6 PM schedule, eats canteen lunch, skips breakfast", "pain_points": ["No time to cook", "Canteen food is repetitive"], "willingness_to_pay": "₹50-60 per meal"},
            {"name": "The Health-Conscious Hosteler", "description": "1st year student, gym-goer, tracks macros, frustrated by lack of protein-rich options", "pain_points": ["No healthy options nearby", "Supplement costs are high"], "willingness_to_pay": "₹65-80 per meal"}
        ],
        "regulatory_considerations": ["FSSAI license required for food business", "GST registration for annual revenue > ₹20L"],
        "market_opportunities": ["Untapped college hostel segment", "Partnership with university administrations for bulk delivery", "Expansion to corporate PGs"],
        "market_risks": ["Student churn during summer/winter breaks", "Perishable inventory management"],
        "research_gaps": ["Exact hostel student population data for Pune is estimated, not census-verified"],
        "sources_consulted": ["RedSeer Consulting", "Statista", "Inc42 FoodTech Report 2024", "Zomato Annual Report 2024", "YourStory startup database"]
    },

    "Marketing Agent": {
        "brand_name": "HostelBites",
        "brand_tagline": "Real Food. Real Fast. Real Affordable.",
        "brand_personality": "Friendly, reliable, young — like a senior who cooks great food and shares it",
        "positioning_statement": "For college hostel students who are tired of canteen food and can't afford Zomato daily, HostelBites delivers ₹50 meal kits that take 10 minutes to make — healthier than ordering out, cheaper than eating out.",
        "target_channels": [
            {"channel": "Instagram Reels", "strategy": "10-minute recipe videos shot in actual hostel rooms", "expected_cac": "₹25-40"},
            {"channel": "Campus Ambassadors", "strategy": "1 ambassador per hostel building, free meals for 10 referrals", "expected_cac": "₹15-20"},
            {"channel": "WhatsApp Groups", "strategy": "Hostel floor WhatsApp groups — share first-week offer", "expected_cac": "₹5-10"}
        ],
        "launch_strategy": {
            "phase_1": "Stealth launch: 50 students in 1 hostel for 2 weeks (validate operations)",
            "phase_2": "Campus launch: expand to 5 hostels with referral program",
            "phase_3": "City launch: multi-campus Pune rollout with Instagram campaign"
        },
        "pricing_strategy": {
            "starter_plan": "₹999/week — 14 meals (₹71/meal)",
            "popular_plan": "₹1499/week — 21 meals (₹71/meal) + 2 snack boxes free",
            "trial": "₹149 for 3 meals — first week trial"
        },
        "viral_mechanics": [
            "Refer 3 friends → get 1 week free",
            "Instagram story with meal → ₹20 off next order",
            "Hostel floor challenge: if 10 people on your floor subscribe, everyone gets 20% off"
        ],
        "estimated_monthly_budget": "₹15,000 for first 3 months (mostly ambassador perks + Instagram ads)"
    },

    "Developer Agent": {
        "recommended_stack": {
            "frontend": "React Native (Expo) — cross-platform mobile app",
            "backend": "Node.js with Express (with justification)",
            "database": "PostgreSQL for orders/users + Redis for session/cache",
            "hosting": "AWS Free Tier (EC2 t2.micro + RDS)",
            "payments": "Razorpay (lowest fees for Indian startups, ₹0 setup)"
        },
        "mvp_features": [
            {"feature": "User registration + profile", "priority": "P0", "effort_days": 3},
            {"feature": "Meal plan selection + subscription", "priority": "P0", "effort_days": 5},
            {"feature": "Order tracking (simple status updates)", "priority": "P0", "effort_days": 3},
            {"feature": "Payment integration (Razorpay)", "priority": "P0", "effort_days": 4},
            {"feature": "Admin dashboard (order management)", "priority": "P1", "effort_days": 5},
            {"feature": "Referral system", "priority": "P1", "effort_days": 3},
            {"feature": "Push notifications", "priority": "P2", "effort_days": 2}
        ],
        "architecture_diagram": "Client (React Native) → API Gateway (Express) → PostgreSQL + Redis → Razorpay Webhook → Admin Panel (React)",
        "development_roadmap": {
            "month_1": "Core app: auth, meal plans, order placement, payment",
            "month_2": "Delivery tracking, admin dashboard, referral system",
            "month_3": "Analytics, push notifications, A/B testing framework"
        },
        "estimated_monthly_infra_cost": "₹0 for first 12 months (AWS Free Tier + Razorpay pay-per-transaction)"
    },

    "Finance Agent": {
        "revenue_projections": {
            "month_1": {"subscribers": 50, "revenue": 74950, "costs": 89000, "profit": -14050},
            "month_6": {"subscribers": 500, "revenue": 749500, "costs": 612000, "profit": 137500},
            "month_12": {"subscribers": 2000, "revenue": 2998000, "costs": 2150000, "profit": 848000},
            "month_36": {"subscribers": 15000, "revenue": 22485000, "costs": 14500000, "profit": 7985000}
        },
        "unit_economics": {
            "average_revenue_per_user": "₹1499/month",
            "food_cost_per_meal": "₹22 (30% of ₹71)",
            "packaging_cost": "₹8/meal",
            "delivery_cost": "₹15/meal (bulk hostel delivery)",
            "gross_margin": "37%",
            "customer_acquisition_cost": "₹120",
            "lifetime_value": "₹5400 (avg 3.6 months retention)",
            "ltv_cac_ratio": "45:1"
        },
        "break_even_analysis": {
            "monthly_fixed_costs": "₹85,000 (kitchen rent + 2 staff + tech)",
            "contribution_margin_per_subscriber": "₹555/month",
            "break_even_subscribers": 154,
            "expected_break_even_month": "Month 4"
        },
        "funding_recommendation": "Bootstrap for first 6 months, then raise ₹25L angel round for multi-city expansion",
        "key_financial_risks": [
            "Food cost inflation (mitigate: 3-month supplier contracts)",
            "Seasonal churn during college breaks (mitigate: pause subscription feature)",
            "Delivery cost increase with scale (mitigate: hub-and-spoke model)"
        ]
    },

    "Analytics Agent": {
        "core_kpis": [
            {"kpi": "Weekly Active Subscribers (WAS)", "target": "85% of total subscribers", "measurement": "Backend: count users with at least 1 order in 7 days"},
            {"kpi": "Customer Acquisition Cost (CAC)", "target": "< ₹150", "measurement": "Total marketing spend / new subscribers acquired"},
            {"kpi": "Net Promoter Score (NPS)", "target": "> 50", "measurement": "In-app survey after 4th delivery"},
            {"kpi": "Churn Rate", "target": "< 15% monthly", "measurement": "Subscribers who cancel / total subscribers"},
            {"kpi": "Order Fulfillment Rate", "target": "> 98%", "measurement": "Delivered orders / total orders placed"}
        ],
        "tracking_plan": {
            "events": ["app_open", "meal_plan_viewed", "subscription_started", "payment_completed", "meal_rated", "referral_sent"],
            "tools": ["Mixpanel (free tier: 20M events)", "Google Analytics 4", "Custom PostgreSQL event log"]
        },
        "growth_metrics": {
            "north_star_metric": "Meals delivered per week",
            "leading_indicators": ["App installs per week", "Referral conversion rate", "Trial-to-paid conversion"],
            "lagging_indicators": ["Monthly revenue", "Churn rate", "NPS"]
        },
        "dashboard_recommendations": [
            "Real-time subscriber count + daily orders",
            "Cohort retention chart (week 1, 2, 4, 8, 12)",
            "Revenue vs CAC trend line",
            "Top-performing campus ambassador leaderboard"
        ]
    },

    "Operations Agent": {
        "week_1_to_4_checklist": [
            {"week": 1, "tasks": ["Register company (LLP)", "Get FSSAI license application started", "Secure cloud kitchen space near Pune university area"]},
            {"week": 2, "tasks": ["Hire 1 cook + 1 delivery person", "Finalize 14-day rotating menu", "Set up packaging supply chain"]},
            {"week": 3, "tasks": ["Launch beta with 50 students (1 hostel)", "Set up WhatsApp support channel", "Begin daily ops tracking spreadsheet"]},
            {"week": 4, "tasks": ["Collect feedback from beta users", "Iterate menu based on ratings", "Prepare campus ambassador program"]}
        ],
        "hiring_plan": {
            "month_1": ["1 Cook (₹18K/month)", "1 Delivery Person (₹12K/month)"],
            "month_3": ["1 Additional Cook", "2 Delivery Persons", "1 Campus Ops Coordinator (part-time student, ₹5K)"],
            "month_6": ["Kitchen Manager", "3 Delivery Persons", "Marketing Intern"]
        },
        "process_documentation": {
            "daily_ops": "5 AM ingredient prep → 7 AM cooking → 9 AM packaging → 10 AM-1 PM delivery window",
            "quality_control": "Temperature check at packaging, photo of each kit before dispatch, random taste test daily",
            "customer_support": "WhatsApp response < 30 min during 8 AM-10 PM, refund within 24 hours for quality issues"
        },
        "immediate_actions": [
            "Today: Register domain hostelbites.in, create Instagram page",
            "This week: Visit 3 cloud kitchens near Pune university for rental quotes",
            "This week: Draft partnership proposal for hostel administration"
        ],
        "legal_checklist": ["FSSAI registration", "GST registration", "LLP deed", "Trademark application for HostelBites"],
        "tools_stack": [
            {"tool": "Google Sheets", "purpose": "Order tracking + inventory management (Month 1-3)", "cost": "Free"},
            {"tool": "WhatsApp Business", "purpose": "Customer support + order updates", "cost": "Free"},
            {"tool": "Razorpay", "purpose": "Payment collection", "cost": "2% per transaction"}
        ],
        "decision_framework": "When two things compete for attention, prioritize: (1) anything that affects tomorrow's deliveries, (2) anything that affects this week's subscriber count, (3) everything else.",
        "success_criteria_90_days": [
            "500+ active subscribers across 5+ hostels",
            "< 2% order fulfillment failure rate",
            "Positive unit economics (contribution margin > 0)",
            "NPS > 40 from beta cohort",
            "At least 1 hostel admin partnership secured"
        ]
    }
}


class ClaudeService:
    """Wrapper around Anthropic Claude API with mock mode support."""

    def __init__(self):
        self.mock_mode = settings.mock_mode
        self.model = settings.claude_model
        self.client = None

        if not self.mock_mode and settings.anthropic_api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Claude API client initialized (REAL mode)")
            except ImportError:
                logger.warning("anthropic package not installed, falling back to mock mode")
                self.mock_mode = True
        else:
            logger.info("Claude API client initialized (MOCK mode — saving API credits)")

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        agent_name: str,
        max_tokens: int = 4096,
    ) -> dict:
        """Generate a response from Claude (or mock).

        Returns:
            dict with keys: content (str), tokens_used (int), cost (float)
        """
        if self.mock_mode:
            return await self._mock_generate(agent_name)
        else:
            return await self._real_generate(system_prompt, user_message, max_tokens)

    async def _mock_generate(self, agent_name: str) -> dict:
        """Return pre-built mock response for the given agent."""
        # Simulate processing time (0.5-1.5s instead of 10-30s)
        import asyncio
        await asyncio.sleep(0.8)

        mock_data = MOCK_RESPONSES.get(agent_name, {"error": f"No mock data for {agent_name}"})

        return {
            "content": json.dumps(mock_data),
            "tokens_used": 1500,  # Simulated
            "cost": 0.0,  # Free in mock mode
        }

    async def _real_generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
    ) -> dict:
        """Make a real Claude API call."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Claude 3.5 Sonnet pricing: $3/1M input, $15/1M output
            cost = (input_tokens * 3.0 / 1_000_000) + (output_tokens * 15.0 / 1_000_000)

            logger.info(f"Claude API call: {total_tokens} tokens, ${cost:.4f}")

            return {
                "content": content,
                "tokens_used": total_tokens,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
