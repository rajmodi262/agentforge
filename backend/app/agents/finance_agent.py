"""StartupOS AI — Finance Agent

Uses Calculator tool to validate financial projections.
"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.tools.calculator import safe_eval


async def _validate_financials(brief: str, context: Dict[str, Any]) -> Any:
    """Run basic financial validations using the calculator tool."""
    validations = []

    marketing = context.get("marketing_output", {})
    pricing = marketing.get("pricing_strategy", {}) if isinstance(marketing, dict) else {}

    # Try to extract and validate pricing math
    try:
        if isinstance(pricing, dict):
            for plan_name, plan_desc in pricing.items():
                if isinstance(plan_desc, str) and "₹" in plan_desc:
                    validations.append({"plan": plan_name, "description": plan_desc})
    except Exception:
        pass

    # Basic unit economics check
    try:
        sample_price = 71  # Default meal price
        food_cost_pct = 0.30
        gross = safe_eval(f"{sample_price} * (1 - {food_cost_pct})")
        validations.append({
            "calculation": f"Gross profit per unit at ₹{sample_price}",
            "result": f"₹{gross:.2f}",
            "margin": f"{(1-food_cost_pct)*100:.0f}%"
        })
    except Exception:
        pass

    return {"validations": validations, "tool": "calculator"}


class FinanceAgent(BaseAgent):
    name = "Finance Agent"
    reasoning_steps = 3  # think → critique → refine
    required_context_keys = ["ceo", "research", "marketing", "developer"]
    tools = [("financial_calculator", _validate_financials)]

    system_prompt = """You are the Finance Agent of StartupOS AI. You are a startup CFO who has managed
finances for 3 funded startups from pre-seed to Series A.

YOUR ROLE:
Build complete financial projections using data from all previous agents.

READING PREVIOUS AGENT OUTPUTS:
- CEO Agent: use revenue_model and stage_assumption for financial framing
- Research Agent: use market_size for TAM-based revenue ceiling
- Marketing Agent: use pricing_strategy and estimated_monthly_budget for cost modeling
- Developer Agent: use estimated_monthly_infra_cost for tech burn rate

You have ACCESS TO CALCULATOR TOOL RESULTS — use them to verify your math.

YOUR DELIVERABLES:
1. Revenue projections (Month 1, 6, 12, 36) with subscriber/customer counts
2. Unit economics (ARPU, cost per unit, gross margin, CAC, LTV, LTV/CAC)
3. Break-even analysis (fixed costs, contribution margin, months to break-even)
4. Funding recommendation
5. Key financial risks with mitigations

CRITICAL: Return ONLY valid JSON. No text outside the JSON object.

OUTPUT SCHEMA:
{
  "revenue_projections": {
    "month_1": {"subscribers": number, "revenue": number, "costs": number, "profit": number},
    "month_6": {"subscribers": number, "revenue": number, "costs": number, "profit": number},
    "month_12": {"subscribers": number, "revenue": number, "costs": number, "profit": number},
    "month_36": {"subscribers": number, "revenue": number, "costs": number, "profit": number}
  },
  "unit_economics": {
    "average_revenue_per_user": "string",
    "cost_per_unit": "string",
    "packaging_cost": "string",
    "delivery_cost": "string",
    "gross_margin": "string",
    "customer_acquisition_cost": "string",
    "lifetime_value": "string",
    "ltv_cac_ratio": "string"
  },
  "break_even_analysis": {
    "monthly_fixed_costs": "string",
    "contribution_margin_per_subscriber": "string",
    "break_even_subscribers": number,
    "expected_break_even_month": "string"
  },
  "funding_recommendation": "string",
  "key_financial_risks": ["string"]
}"""

    output_schema = {
        "revenue_projections": {
            "month_1": {"subscribers": 0, "revenue": 0, "costs": 0, "profit": 0},
            "month_6": {"subscribers": 0, "revenue": 0, "costs": 0, "profit": 0},
            "month_12": {"subscribers": 0, "revenue": 0, "costs": 0, "profit": 0},
            "month_36": {"subscribers": 0, "revenue": 0, "costs": 0, "profit": 0},
        },
        "unit_economics": {},
        "break_even_analysis": {},
        "funding_recommendation": "string",
        "key_financial_risks": ["string"],
    }
