"""StartupOS AI — AI Service (Claude + Gemini with Dynamic Mock Fallback)

Supports Claude (Anthropic) and Gemini (Google) as AI providers.
Auto-selects the best available provider based on configured API keys.
Falls back to intelligent mock mode when no keys are available.
"""

import json
import time
import random
import hashlib
import logging
import asyncio
from typing import Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────── Keywords & Mock Helpers ───────────────────────────────

def _extract_keywords(text: str) -> list:
    """Extract meaningful keywords from business idea text."""
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "must", "can", "could", "i", "we", "you",
        "they", "he", "she", "it", "my", "your", "our", "their", "this",
        "that", "these", "those", "and", "or", "but", "if", "in", "on",
        "at", "to", "for", "of", "with", "by", "from", "as", "into",
        "through", "about", "between", "want", "need", "like", "make",
        "create", "build", "app", "platform", "service", "product",
    }
    words = text.lower().split()
    keywords = [w.strip(".,!?:;\"'()[]{}") for w in words if len(w) > 2 and w.lower() not in stop_words]
    return keywords[:10]


def _generate_startup_name(keywords: list) -> str:
    """Generate a plausible startup name from keywords."""
    suffixes = ["ly", "ify", "hub", "stack", "labs", "base", "flow", "sync", "nest", "hive", "spot"]
    if keywords:
        base = keywords[0].capitalize()
        suffix = random.choice(suffixes)
        return f"{base}{suffix}"
    return "LaunchPad"


def _seed_random(text: str):
    """Seed random based on input for consistent but varied results."""
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    random.seed(seed)


def _generate_dynamic_mock(agent_name: str, user_message: str) -> dict:
    """Generate input-aware mock responses based on the user's business idea."""
    _seed_random(user_message + agent_name)
    keywords = _extract_keywords(user_message)
    industry = keywords[0].capitalize() if keywords else "Technology"
    industry2 = keywords[1].capitalize() if len(keywords) > 1 else "Digital"
    startup_name = _generate_startup_name(keywords)
    
    target_market = "India"
    for market_kw in ["india", "us", "global", "europe", "asia", "africa", "usa", "uk"]:
        if market_kw in user_message.lower():
            target_market = market_kw.capitalize()
            break

    tam = random.randint(2, 15)
    sam = round(tam * random.uniform(0.05, 0.15), 1)
    som = round(sam * random.uniform(0.005, 0.02), 2)
    cagr = random.randint(18, 35)
    price_low = random.choice([29, 49, 79, 99, 149, 199])
    price_high = price_low * random.choice([2, 3, 4])
    break_even_month = random.randint(8, 18)

    responses = {
        "CEO Agent": {
            "startup_name_suggestion": startup_name,
            "problem_statement": f"The {industry.lower()} space faces critical inefficiencies — existing solutions are fragmented, overpriced, and fail to serve the core user need.",
            "solution_description": f"{startup_name} is an AI-powered {industry.lower()} platform that automates key workflows and delivers 10x better outcomes at a fraction of the cost.",
            "target_user_primary": f"Professionals and small businesses in {target_market} working in the {industry.lower()} sector, ages 25-45",
            "target_user_secondary": "Enterprise clients",
            "business_model_type": random.choice(["B2B SaaS", "B2C", "B2B2C", "Marketplace", "D2C"]),
            "revenue_model": f"Monthly subscription with tiered pricing (₹{price_low}-₹{price_high}/month)",
            "geographic_focus": f"{target_market} — starting with tier-1 cities",
            "industry_vertical": f"{industry} / {industry2}",
            "stage_assumption": "Pre-seed",
            "key_assumptions": ["Market is ready for AI", "Users will pay for efficiency", "CAC can be kept low"],
            "top_risks": ["Competition from incumbents", "Regulatory changes", "High initial churn"],
            "questions_for_research_agent": ["What is the exact TAM in tier-1 cities?", "Who are the direct competitors?"],
            "questions_for_marketing_agent": ["What is the most effective acquisition channel?", "How do we position against legacy players?"],
            "questions_for_developer_agent": ["Can we build this in 8 weeks?", "What is the optimal tech stack?"],
            "questions_for_finance_agent": ["When will we break even?", "How much funding do we need?"],
            "executive_brief": f"{startup_name} targets the ${tam}B {industry.lower()} market in {target_market}."
        },
        "Research Agent": {
            "market_size": {"tam": f"${tam}B", "sam": f"${sam}B", "som": f"${som}B", "source": "Industry Reports 2024"},
            "market_growth_rate": f"{cagr}% CAGR (2023-2028)",
            "market_trends": [f"AI adoption in {industry.lower()}", f"Shift to cloud-native {industry.lower()} platforms"],
            "competitors": [{"name": f"LegacyCorp {industry}", "description": "Incumbent player", "funding": "Series C, $50M", "weakness": "Outdated UI, expensive"}],
            "customer_personas": [{"name": "Tech-savvy Manager", "description": "Mid-level manager looking for efficiency", "pain_points": ["Manual workflows", "Data silos"], "willingness_to_pay": f"₹{price_high}/month"}],
            "regulatory_considerations": ["Data privacy laws (DPDP Act)", "Industry-specific compliance"],
            "market_opportunities": ["Underserved tier-2 markets", "AI-driven personalization"],
            "market_risks": ["Price sensitivity", "Low switching costs"],
            "research_gaps": ["Detailed churn data of competitors", "Exact LTV across different cohorts"],
            "sources_consulted": ["Gartner Reports", "Industry Whitepapers", "Public Financials"],
        },
        "Marketing Agent": {
            "brand_name": startup_name,
            "brand_tagline": f"Smart {industry}. Simplified.",
            "brand_personality": "Modern, trustworthy, innovative",
            "positioning_statement": f"For {industry.lower()} professionals, {startup_name} delivers AI-powered automation at ₹{price_low}/month.",
            "target_channels": [{"channel": "LinkedIn Ads", "strategy": "Target mid-level managers", "expected_cac": "₹1500"}, {"channel": "Content SEO", "strategy": "Industry specific guides", "expected_cac": "₹300"}],
            "launch_strategy": {"phase_1": "Waitlist & Beta", "phase_2": "Public Launch", "phase_3": "Growth & Scale"},
            "pricing_strategy": {"starter_plan": f"₹{price_low}/mo", "popular_plan": f"₹{price_high}/mo", "trial": "14-day free trial"},
            "viral_mechanics": ["Referral discounts", "Watermarked free tier"],
            "estimated_monthly_budget": f"₹{random.randint(50000, 200000)}/month"
        },
        "Developer Agent": {
            "recommended_stack": {"frontend": "React/Next.js", "backend": "Python FastAPI", "database": "PostgreSQL + Redis", "hosting": "AWS / Vercel", "payments": "Stripe / Razorpay"},
            "mvp_features": [{"feature": f"Core {industry.lower()} workflow", "priority": "P0", "effort_days": 8}],
            "architecture_diagram": f"Client -> Load Balancer -> {startup_name} API -> Database",
            "development_roadmap": {"month_1": "Core API and Auth", "month_2": "Frontend Integration", "month_3": "Beta testing and bug fixes"},
            "estimated_monthly_infra_cost": f"₹{random.choice([2000, 5000])}/month",
            "generated_code": {"backend_entrypoint": "from fastapi import FastAPI...", "database_schema": "CREATE TABLE users...", "api_routes": "@app.get('/api')...", "docker_compose": "version: '3'...", "env_template": "DB_URL=..."}
        },
        "Finance Agent": {
            "revenue_projections": {
                "month_1": {"subscribers": random.randint(10, 50), "revenue": random.randint(10000, 50000), "costs": 40000, "profit": -30000},
                "month_6": {"subscribers": random.randint(300, 800), "revenue": random.randint(300000, 800000), "costs": 200000, "profit": 100000},
                "month_12": {"subscribers": random.randint(1000, 2000), "revenue": random.randint(1000000, 2000000), "costs": 500000, "profit": 500000},
                "month_36": {"subscribers": random.randint(5000, 10000), "revenue": random.randint(5000000, 10000000), "costs": 1500000, "profit": 3500000}
            },
            "unit_economics": {"gross_margin": f"{random.randint(60, 80)}%", "ltv_cac_ratio": f"{random.randint(8, 25)}:1", "average_revenue_per_user": f"₹{price_low}", "cost_per_unit": "₹50"},
            "break_even_analysis": {"expected_break_even_month": f"Month {break_even_month}", "monthly_fixed_costs": "₹200000", "break_even_subscribers": 500},
            "funding_recommendation": f"Raise ${random.choice(['500k', '1M'])} Pre-seed",
            "key_financial_risks": ["Higher CAC than expected", "Delayed monetization"]
        },
        "Analytics Agent": {
            "core_kpis": [{"kpi": "MAU", "target": "85% of subscribers", "measurement": "Mixpanel"}],
            "tracking_plan": {"events": ["Sign Up", "Core Action", "Upgrade"], "tools": ["Mixpanel", "Google Analytics", "Sentry"]},
            "growth_metrics": {"north_star_metric": f"Weekly active {industry.lower()} workflows completed", "leading_indicators": ["Daily logins", "Feature usage"], "lagging_indicators": ["Churn rate", "MRR"]},
            "dashboard_recommendations": ["User retention cohort analysis", "Real-time funnel conversion"]
        },
        "Operations Agent": {
            "week_1_to_4_checklist": [{"week": 1, "tasks": [f"Register domain {startup_name.lower()}.com", "Set up cloud infrastructure"]}, {"week": 2, "tasks": ["Launch landing page"]}, {"week": 3, "tasks": ["Beta testing"]}, {"week": 4, "tasks": ["Public launch"]}],
            "hiring_plan": {"month_1": ["1 Full-stack Developer", "1 Designer (part-time)"], "month_3": ["1 Marketing Lead", "1 Customer Success Agent"], "month_6": ["2 Sales Reps", "1 Data Analyst"]},
            "process_documentation": {"daily_ops": "Daily standups, weekly sprint planning", "quality_control": "Code reviews, automated testing", "customer_support": "ZenDesk SLA within 2 hours"},
            "immediate_actions": [f"Register domain {startup_name.lower()}.com", "Set up cloud infrastructure"],
            "legal_checklist": ["Incorporate company", "Draft Terms of Service", "File for trademarks"],
            "tools_stack": [{"tool": "Notion", "purpose": "Documentation", "cost": "$10/mo"}, {"tool": "Slack", "purpose": "Communication", "cost": "$8/mo"}],
            "decision_framework": "Data-driven, customer-centric",
            "success_criteria_90_days": [f"{random.randint(300, 800)}+ active subscribers", "< 10% monthly churn"]
        },
        "Board Meeting": {
            "debate_points": [
                {"challenger": "Finance Agent", "target": "Marketing Agent", "challenge": "CAC expectation is too low for this B2B segment.", "rebuttal": "We will leverage organic SEO to offset paid CAC.", "resolution": "Agreed to blend paid and organic channels to maintain target CAC."}
            ],
            "consensus_score": random.randint(75, 95),
            "key_risks_after_debate": ["Execution speed against incumbents", "Regulatory compliance in data handling"],
            "revised_recommendations": ["Prioritize SOC2 compliance early", "Focus on a niche tier-2 market before expanding"],
            "board_decision": f"The board approves the strategic direction for {startup_name} with a focus on sustainable growth and early monetization."
        }
    }

    return responses.get(agent_name, {"status": "analysis_complete", "agent": agent_name})


# ─────────────────────────────── AI Service Class ───────────────────────────────

class ClaudeService:
    """Multi-provider AI service: Claude, Gemini, or dynamic mock.
    
    Provider selection (when ai_provider="auto"):
      1. If gemini_api_key is set → use Gemini (free/cheap)
      2. If anthropic_api_key is set → use Claude
      3. Otherwise → use mock mode
    """

    def __init__(self):
        self.mock_mode = settings.mock_mode
        self.provider = self._resolve_provider()
        self.client = None
        self.gemini_model = None
        self.groq_model = None

        if self.mock_mode:
            logger.info("AI Service initialized (MOCK mode — saving API credits)")
            return

        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "claude":
            self._init_claude()
        else:
            logger.warning("No AI provider available, falling back to mock mode")
            self.mock_mode = True

    def _resolve_provider(self) -> str:
        """Determine which AI provider to use."""
        if self.mock_mode:
            return "mock"

        pref = settings.ai_provider.lower()
        if pref == "groq" and settings.groq_api_key:
            return "groq"
        if pref == "claude" and settings.anthropic_api_key:
            return "claude"
        if pref == "gemini" and settings.gemini_api_key:
            return "gemini"
        if pref == "auto":
            # Prefer Groq (fast + generous free tier), then Gemini, then Claude
            if settings.groq_api_key:
                return "groq"
            if settings.gemini_api_key:
                return "gemini"
            if settings.anthropic_api_key:
                return "claude"
        return "mock"

    def _init_groq(self):
        """Initialize Groq client (fast Llama inference)."""
        try:
            from groq import Groq
            self.client = Groq(api_key=settings.groq_api_key)
            self.groq_model = settings.groq_model
            logger.info(f"Groq AI client initialized (model={self.groq_model})")
        except ImportError:
            logger.warning("groq package not installed. Install with: pip install groq")
            logger.warning("Falling back to mock mode")
            self.mock_mode = True
        except Exception as e:
            logger.error(f"Groq init error: {e}")
            self.mock_mode = True

    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.gemini_model = settings.gemini_model
            logger.info(f"Gemini AI client initialized (model={self.gemini_model})")
        except ImportError:
            logger.warning("google-genai package not installed. Install with: pip install google-genai")
            logger.warning("Falling back to mock mode")
            self.mock_mode = True
        except Exception as e:
            logger.error(f"Gemini init error: {e}")
            self.mock_mode = True

    def _init_claude(self):
        """Initialize Anthropic Claude client."""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            logger.info(f"Claude AI client initialized (model={settings.claude_model})")
        except ImportError:
            logger.warning("anthropic package not installed, falling back to mock mode")
            self.mock_mode = True
        except Exception as e:
            logger.error(f"Claude init error: {e}")
            self.mock_mode = True

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        agent_name: str,
        max_tokens: int = 4096,
    ) -> dict:
        """Generate a response using the configured AI provider.

        Returns:
            dict with keys: content (str), tokens_used (int), cost (float)
        """
        if self.mock_mode:
            return await self._mock_generate(agent_name, user_message)

        try:
            if self.provider == "groq":
                return await self._groq_generate(system_prompt, user_message, max_tokens)
            elif self.provider == "gemini":
                return await self._gemini_generate(system_prompt, user_message, max_tokens)
            else:
                return await self._claude_generate(system_prompt, user_message, max_tokens)
        except Exception as e:
            logger.error(f"AI generation error ({self.provider}): {e}")
            logger.warning("Falling back to mock mode for this request")
            return await self._mock_generate(agent_name, user_message)

    async def generate_structured(
        self,
        system_prompt: str,
        user_message: str,
        output_model,
        agent_name: str = "unknown",
        max_tokens: int = 4096,
    ) -> dict:
        """Generate with guaranteed structured output via Claude's tool_use.

        Defines the output Pydantic model as a Claude tool, forces Claude to
        respond via tool_use, then extracts and validates the structured output.
        Falls back to regular generate() + parse for non-Claude providers.

        Returns:
            dict with keys: content (dict — validated), tokens_used (int), cost (float)
        """
        if self.mock_mode:
            return await self._mock_generate(agent_name, user_message)

        # Only Claude supports tool_use natively; Gemini uses response_mime_type
        if self.provider != "claude" or not self.client:
            # Fallback: regular generate + JSON parse
            result = await self.generate(system_prompt, user_message, agent_name, max_tokens)
            return result

        try:
            import json as _json
            tool_schema = output_model.model_json_schema()
            # Remove pydantic-specific keys that Claude doesn't need
            tool_schema.pop("title", None)

            tool_def = {
                "name": "submit_analysis",
                "description": f"Submit the {agent_name} structured analysis output",
                "input_schema": tool_schema,
            }

            response = await asyncio.to_thread(
                self.client.messages.create,
                model=settings.claude_model,
                max_tokens=max_tokens,
                system=system_prompt,
                tools=[tool_def],
                tool_choice={"type": "tool", "name": "submit_analysis"},
                messages=[{"role": "user", "content": user_message}],
            )

            # Extract the tool_use block and any text blocks (thinking)
            tool_output = None
            thought_text = ""
            for block in response.content:
                if block.type == "text":
                    thought_text += block.text + "\n"
                elif block.type == "tool_use":
                    tool_output = block.input
                    break

            if tool_output is None:
                # Fallback: try text content
                for block in response.content:
                    if hasattr(block, "text"):
                        try:
                            tool_output = _json.loads(block.text)
                            break
                        except Exception:
                            pass

            if tool_output is None:
                raise ValueError("No tool_use or text block found in Claude response")

            # Validate via Pydantic
            validated = output_model(**tool_output)

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            cost = (input_tokens * 3.0 / 1_000_000) + (output_tokens * 15.0 / 1_000_000)

            return {
                "content": _json.dumps(validated.model_dump()),
                "thought": thought_text.strip(),
                "tokens_used": total_tokens,
                "cost": cost,
            }

        except Exception as e:
            logger.warning(f"Structured generation failed for {agent_name}: {e}, falling back to regular")
            return await self.generate(system_prompt, user_message, agent_name, max_tokens)

    async def generate_critique(
        self,
        original_output: str,
        critique_prompt: str,
        agent_name: str = "unknown",
        max_tokens: int = 2048,
    ) -> dict:
        """Generate a self-critique of a previous agent output.

        Used in multi-step reasoning: step 2 (critique) and step 3 (refinement).
        """
        if self.mock_mode:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            return {
                "content": json.dumps({
                    "weaknesses": [
                        "Market size assumptions may be optimistic — needs primary data validation",
                        "Competitor moat analysis is surface-level — deeper differentiation needed",
                        "Timeline assumes ideal hiring velocity which rarely materializes"
                    ],
                    "improvements": [
                        "Add sensitivity analysis for TAM/SAM figures",
                        "Include detailed competitive positioning matrix",
                        "Build contingency buffer of 30% into all timelines"
                    ],
                    "confidence_before": 65,
                    "confidence_after": 82
                }),
                "tokens_used": random.randint(400, 1200),
                "cost": 0.0,
            }

        system = f"You are the self-critique module for {agent_name}. Be brutally honest."
        user_msg = f"{critique_prompt}\n\nPREVIOUS OUTPUT:\n{original_output}"

        return await self.generate(system, user_msg, agent_name, max_tokens)

    async def _mock_generate(self, agent_name: str, user_message: str) -> dict:
        """Return dynamic, input-aware mock response."""
        await asyncio.sleep(random.uniform(0.5, 1.5))
        mock_data = _generate_dynamic_mock(agent_name, user_message)
        return {
            "content": json.dumps(mock_data),
            "thought": f"Analyzing the brief to formulate {agent_name} strategy. Identifying key market parameters and aligning with the CEO's vision. Extracting insights...",
            "tokens_used": random.randint(800, 2500),
            "cost": 0.0,
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def _groq_generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
    ) -> dict:
        """Make a real Groq (Llama) API call with JSON output enforced.

        The agent prompts already instruct the model to return JSON, so we use
        Groq's native JSON mode for reliable, parseable structured output.
        """
        # Groq's JSON mode requires the word "json" to appear in the messages.
        system_with_json = (
            f"{system_prompt}\n\nIMPORTANT: Respond ONLY with a single valid JSON object."
        )

        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.groq_model,
            max_tokens=max_tokens,
            temperature=0.4,  # Lower temp for reliable structured JSON output
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_with_json},
                {"role": "user", "content": user_message},
            ],
        )

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("Groq returned empty response")

        usage = response.usage
        input_tokens = getattr(usage, "prompt_tokens", 0) or 0
        output_tokens = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = input_tokens + output_tokens

        # Llama 3.3 70B on Groq pricing: ~$0.59/1M input, ~$0.79/1M output
        cost = (input_tokens * 0.59 / 1_000_000) + (output_tokens * 0.79 / 1_000_000)

        logger.info(f"Groq API call: {total_tokens} tokens, ${cost:.6f}")

        return {
            "content": content,
            "thought": "",
            "tokens_used": total_tokens,
            "cost": cost,
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def _gemini_generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
    ) -> dict:
        """Make a real Google Gemini API call with production-grade error handling."""
        from google.genai import types

        combined_prompt = f"{system_prompt}\n\n---\n\n{user_message}"

        # Run sync Gemini call in a thread to keep async
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.gemini_model,
                contents=combined_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.4,  # Lower temp for reliable structured JSON output
                    response_mime_type="application/json",
                ),
            )
        )

        content = response.text
        if not content or not content.strip():
            raise ValueError("Gemini returned empty response")

        # Extract thinking/reasoning if present
        thought = ""
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'thought') and part.thought:
                        thought = part.text if hasattr(part, 'text') else ""
        except Exception:
            pass

        # Gemini token counting
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) or 0
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) or 0
        total_tokens = input_tokens + output_tokens

        # Gemini 2.5 Flash pricing: $0.15/1M input, $0.60/1M output (very cheap)
        cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)

        logger.info(f"Gemini API call: {total_tokens} tokens, ${cost:.6f}")

        return {
            "content": content,
            "thought": thought,
            "tokens_used": total_tokens,
            "cost": cost,
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def _claude_generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
    ) -> dict:
        """Make a real Anthropic Claude API call (non-blocking)."""
        # Run sync Anthropic SDK call in a thread to avoid blocking the event loop
        response = await asyncio.to_thread(
            self.client.messages.create,
            model=settings.claude_model,
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


# ─────────────────────────────── Singleton ───────────────────────────────

_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
