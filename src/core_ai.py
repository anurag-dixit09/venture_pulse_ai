"""Gemini API helpers, configuration checks, and prompt builders."""

import json
import subprocess
import sys
from typing import Any

try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai


def initialize_gemini_api(secrets_dict: dict) -> bool:
    api_key = secrets_dict.get("GEMINI_API_KEY", "")
    if not isinstance(api_key, str):
        return False

    api_key = api_key.strip()
    if not api_key:
        return False

    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False


def build_feasibility_prompt(startup_name: str, industry: str, budget: int, idea_description: str) -> str:
    return f"""
    You are an elite Venture Capitalist and institutional auditor specializing in the Indian startup landscape.
    Evaluate the feasibility and risk vector profiles of the following startup project:
    - Project Name: {startup_name}
    - Sector: {industry}
    - Target Funding/Budget: ₹{budget:,}
    - Product Blueprint: {idea_description}

    You MUST return your analysis strictly organized under three key parts:
    PART 1: MARKET DYNAMICS
    Detail the market saturation level, adoption barriers, consumer skepticism risk, and overall sector growth potential in India.

    PART 2: LEGAL & COMPLIANCE
    Analyze RBI/SEBI regulatory exposure, GST tax compliance, and modern DPDP Act (Data Protection) operational hurdles.

    PART 3: FINANCIAL SUSTAINABILITY
    Analyze capital allocation strategy, burn rate dangers, monetization feasibility, and estimated runway duration.
    """


def build_score_prompt(
    p_name: str,
    grade: str,
    total_weighted_score: int,
    tam_size: int,
    runway_months: float,
    initial_capital: int,
    burn_rate: int,
    ltv_cac_ratio: float,
    ltv: int,
    cac: int,
    growth_rate: int,
    risk_profile: str,
) -> str:
    return f"""
    Provide a concise, highly strategic 3-bullet-point execution guide to improve the score of the following startup:
    - Startup: {p_name}
    - Current Grade: {grade} (Score: {total_weighted_score}/100)
    - TAM: ₹{tam_size:,}
    - Runway: {runway_months:.1f} Months (Capital: ₹{initial_capital:,}, Burn: ₹{burn_rate:,})
    - LTV/CAC: {ltv_cac_ratio:.2f}x (LTV: ₹{ltv}, CAC: ₹{cac})

    Focus strictly on practical runway extension, CAC optimization, and TAM capture in India.
    """


def build_competitor_prompt(venture_definition: str, target_keywords: str, comp_limit: int) -> str:
    return f"""
    You are a strategic Indian market research analyst and startup growth advisor.
    Based on the following venture concept and keywords:
    Venture: {venture_definition}
    Keywords / Sub-sector: {target_keywords}

    Produce a concise but actionable competitive intelligence report for the Indian market.
    Return STRICT JSON in this shape:
    {{
      "direct_competitors": [
        {{"name": "", "market_context": "", "value_prop": "", "vulnerability": ""}}
      ],
      "indirect_competitors": [
        {{"name": "", "market_context": "", "value_prop": "", "vulnerability": ""}}
      ],
      "competitive_edge_strategy": [
        {{"move": "", "why_it_matters": ""}}
      ]
    }}

    Focus on active Indian ecosystem players, legacy alternatives, and practical strategic moves a founder can take to stand out.
    Use a maximum of {comp_limit} entries for each competitor list.
    """


def run_gemini_prompt(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()


def parse_json_response(response_text: str) -> dict[str, Any]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)
