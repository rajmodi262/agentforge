"""AgentForge AI — Agent Output Models (Pydantic v2)

Strict Pydantic models for each agent's output.
Used for:
1. Claude tool_use structured output enforcement
2. Output validation after LLM calls
3. API response typing
4. Documentation / schema export

Each model maps 1:1 to an agent's expected output.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ─────────── CEO Agent ───────────

class CEOOutput(BaseModel):
    startup_name_suggestion: str = Field(..., description="Suggested name for the startup")
    problem_statement: str = Field(..., description="2-3 sentence problem statement")
    solution_description: str = Field(..., description="2-3 sentence solution description")
    target_user_primary: str = Field(..., description="Primary target user demographic")
    target_user_secondary: Optional[str] = Field(None, description="Secondary target user")
    business_model_type: str = Field(..., description="B2C | B2B | B2B2C | Marketplace | SaaS | D2C | Other")
    revenue_model: str = Field(..., description="Primary revenue model")
    geographic_focus: str = Field(..., description="Target geography")
    industry_vertical: str = Field(..., description="Industry vertical")
    stage_assumption: str = Field("Pre-seed", description="Pre-seed | Seed | Series A")
    key_assumptions: List[str] = Field(default_factory=list, description="Top 3 key assumptions")
    top_risks: List[str] = Field(default_factory=list, description="Top 3 risks identified")
    questions_for_research_agent: List[str] = Field(default_factory=list)
    questions_for_marketing_agent: List[str] = Field(default_factory=list)
    questions_for_developer_agent: List[str] = Field(default_factory=list)
    questions_for_finance_agent: List[str] = Field(default_factory=list)
    executive_brief: str = Field("", description="4-5 sentence master brief for all agents")


# ─────────── Research Agent ───────────

class CompetitorInfo(BaseModel):
    name: str = Field(..., description="Competitor name")
    description: str = Field(..., description="Competitor description")
    funding: str = Field(..., description="Competitor funding")
    weakness: str = Field(..., description="Competitor weakness")

class MarketSize(BaseModel):
    tam: str = Field(..., description="Total addressable market with source")
    sam: str = Field(..., description="Serviceable addressable market")
    som: str = Field(..., description="Serviceable obtainable market")
    source: str = Field(..., description="Source of the data")

class CustomerPersona(BaseModel):
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    pain_points: List[str] = Field(default_factory=list, description="Pain points")
    willingness_to_pay: str = Field(..., description="Willingness to pay")

class ResearchOutput(BaseModel):
    market_size: MarketSize = Field(..., description="TAM/SAM/SOM breakdown")
    market_growth_rate: str = Field(..., description="CAGR with source")
    market_trends: List[str] = Field(default_factory=list, description="Market trends")
    competitors: List[CompetitorInfo] = Field(default_factory=list, description="Competitors")
    customer_personas: List[CustomerPersona] = Field(default_factory=list, description="Customer personas")
    regulatory_considerations: List[str] = Field(default_factory=list, description="Regulatory landscape")
    market_opportunities: List[str] = Field(default_factory=list, description="Market opportunities")
    market_risks: List[str] = Field(default_factory=list, description="Market risks")
    research_gaps: List[str] = Field(default_factory=list, description="Research gaps")
    sources_consulted: List[str] = Field(default_factory=list, description="Sources consulted")


# ─────────── Marketing Agent ───────────

class TargetChannel(BaseModel):
    channel: str = Field(..., description="Channel name")
    strategy: str = Field(..., description="Strategy for channel")
    expected_cac: str = Field(..., description="Expected CAC")

class LaunchStrategy(BaseModel):
    phase_1: str = Field(..., description="Phase 1")
    phase_2: str = Field(..., description="Phase 2")
    phase_3: str = Field(..., description="Phase 3")

class PricingStrategy(BaseModel):
    starter_plan: str = Field(..., description="Starter plan")
    popular_plan: str = Field(..., description="Popular plan")
    trial: str = Field(..., description="Trial details")

class MarketingOutput(BaseModel):
    brand_name: str = Field(..., description="Brand name")
    brand_tagline: str = Field(..., description="Brand tagline")
    brand_personality: str = Field(..., description="Brand personality")
    positioning_statement: str = Field(..., description="Positioning statement")
    target_channels: List[TargetChannel] = Field(default_factory=list, description="Target channels")
    launch_strategy: LaunchStrategy = Field(..., description="Launch strategy")
    pricing_strategy: PricingStrategy = Field(..., description="Pricing strategy")
    viral_mechanics: List[str] = Field(default_factory=list, description="Viral mechanics")
    estimated_monthly_budget: str = Field(..., description="Estimated monthly budget")


# ─────────── Developer Agent ───────────

class RecommendedStack(BaseModel):
    frontend: str = Field(..., description="Frontend stack with justification")
    backend: str = Field(..., description="Backend stack with justification")
    database: str = Field(..., description="Database stack with justification")
    hosting: str = Field(..., description="Hosting stack with justification")
    payments: str = Field(..., description="Payments stack with justification")

class MVPFeature(BaseModel):
    feature: str = Field(..., description="Feature description")
    priority: str = Field(..., description="Priority (P0/P1/P2)")
    effort_days: int = Field(..., description="Effort in days")

class DevelopmentRoadmap(BaseModel):
    month_1: str = Field(..., description="Month 1")
    month_2: str = Field(..., description="Month 2")
    month_3: str = Field(..., description="Month 3")

class GeneratedCode(BaseModel):
    backend_entrypoint: str = Field(..., description="Backend entrypoint code")
    database_schema: str = Field(..., description="Database schema code")
    api_routes: str = Field(..., description="API routes code")
    docker_compose: str = Field(..., description="Docker compose YAML")
    env_template: str = Field(..., description="Env template")

class DeveloperOutput(BaseModel):
    recommended_stack: RecommendedStack = Field(..., description="Recommended stack")
    mvp_features: List[MVPFeature] = Field(default_factory=list, description="MVP features")
    architecture_diagram: str = Field(..., description="Architecture diagram")
    development_roadmap: DevelopmentRoadmap = Field(..., description="Development roadmap")
    estimated_monthly_infra_cost: str = Field(..., description="Estimated monthly infra cost")
    generated_code: GeneratedCode = Field(..., description="Generated code")


# ─────────── Finance Agent ───────────

class RevenueMonth(BaseModel):
    subscribers: int = Field(0, description="Subscribers count")
    revenue: float = Field(0.0, description="Revenue")
    costs: float = Field(0.0, description="Costs")
    profit: float = Field(0.0, description="Profit")

class RevenueProjections(BaseModel):
    month_1: RevenueMonth = Field(default_factory=RevenueMonth)
    month_6: RevenueMonth = Field(default_factory=RevenueMonth)
    month_12: RevenueMonth = Field(default_factory=RevenueMonth)
    month_36: RevenueMonth = Field(default_factory=RevenueMonth)

class FinanceOutput(BaseModel):
    revenue_projections: RevenueProjections = Field(default_factory=RevenueProjections, description="Monthly revenue projections")
    unit_economics: Dict[str, str] = Field(default_factory=dict, description="LTV, CAC, LTV:CAC ratio")
    break_even_analysis: Dict[str, Any] = Field(default_factory=dict, description="Break-even analysis")
    funding_recommendation: str = Field("", description="Funding stage and amount recommendation")
    key_financial_risks: List[str] = Field(default_factory=list, description="Financial risk factors")


# ─────────── Analytics Agent ───────────

class CoreKPI(BaseModel):
    kpi: str = Field(..., description="KPI name")
    target: str = Field(..., description="KPI target")
    measurement: str = Field(..., description="Measurement method")

class TrackingPlan(BaseModel):
    events: List[str] = Field(default_factory=list, description="Events to track")
    tools: List[str] = Field(default_factory=list, description="Tools to use")

class GrowthMetrics(BaseModel):
    north_star_metric: str = Field(..., description="North star metric")
    leading_indicators: List[str] = Field(default_factory=list, description="Leading indicators")
    lagging_indicators: List[str] = Field(default_factory=list, description="Lagging indicators")

class AnalyticsOutput(BaseModel):
    core_kpis: List[CoreKPI] = Field(default_factory=list, description="Core KPIs")
    tracking_plan: TrackingPlan = Field(..., description="Tracking plan")
    growth_metrics: GrowthMetrics = Field(..., description="Growth metrics")
    dashboard_recommendations: List[str] = Field(default_factory=list, description="Dashboard recommendations")


# ─────────── Operations Agent ───────────

class WeekTasks(BaseModel):
    week: int = Field(..., description="Week number")
    tasks: List[str] = Field(default_factory=list, description="Tasks for the week")

class HiringPlan(BaseModel):
    month_1: List[str] = Field(default_factory=list, description="Hires for month 1")
    month_3: List[str] = Field(default_factory=list, description="Hires for month 3")
    month_6: List[str] = Field(default_factory=list, description="Hires for month 6")

class ProcessDocumentation(BaseModel):
    daily_ops: str = Field(..., description="Daily ops processes")
    quality_control: str = Field(..., description="Quality control processes")
    customer_support: str = Field(..., description="Customer support processes")

class ToolStack(BaseModel):
    tool: str = Field(..., description="Tool name")
    purpose: str = Field(..., description="Tool purpose")
    cost: str = Field(..., description="Tool cost")

class OperationsOutput(BaseModel):
    week_1_to_4_checklist: List[WeekTasks] = Field(default_factory=list, description="Week 1 to 4 checklist")
    hiring_plan: HiringPlan = Field(..., description="Hiring plan")
    process_documentation: ProcessDocumentation = Field(..., description="Process documentation")
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate actions")
    legal_checklist: List[str] = Field(default_factory=list, description="Legal checklist")
    tools_stack: List[ToolStack] = Field(default_factory=list, description="Tools stack")
    decision_framework: str = Field(..., description="Decision framework")
    success_criteria_90_days: List[str] = Field(default_factory=list, description="Success criteria for 90 days")


# ─────────── Board Meeting ───────────

class DebatePoint(BaseModel):
    challenger: str = Field(..., description="Agent raising the challenge")
    target: str = Field(..., description="Agent being challenged")
    challenge: str = Field(..., description="The specific challenge raised")
    rebuttal: str = Field(..., description="Response to the challenge")
    resolution: str = Field(..., description="How it was resolved")

class BoardMeetingOutput(BaseModel):
    debate_points: List[DebatePoint] = Field(default_factory=list, description="Key debate points")
    consensus_score: int = Field(70, ge=0, le=100, description="Overall confidence 0-100")
    key_risks_after_debate: List[str] = Field(default_factory=list, description="Remaining risks")
    revised_recommendations: List[str] = Field(default_factory=list, description="Updated recommendations")
    board_decision: str = Field("", description="Final board meeting summary")


# ─────────── Registry ───────────

AGENT_OUTPUT_MODELS = {
    "CEO Agent": CEOOutput,
    "Research Agent": ResearchOutput,
    "Marketing Agent": MarketingOutput,
    "Developer Agent": DeveloperOutput,
    "Finance Agent": FinanceOutput,
    "Analytics Agent": AnalyticsOutput,
    "Operations Agent": OperationsOutput,
    "Board Meeting": BoardMeetingOutput,
}
