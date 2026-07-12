"""Venture Pulse AI modular app package."""

from .components import PREMIMUM_CSS, inject_premium_css
from .core_ai import (
    build_competitor_prompt,
    build_feasibility_prompt,
    build_score_prompt,
    initialize_gemini_api,
    parse_json_response,
    run_gemini_prompt,
)
from .scoring import compute_scorecard, format_inr, get_grade

__all__ = [
    "PREMIMUM_CSS",
    "inject_premium_css",
    "build_competitor_prompt",
    "build_feasibility_prompt",
    "build_score_prompt",
    "initialize_gemini_api",
    "parse_json_response",
    "run_gemini_prompt",
    "compute_scorecard",
    "format_inr",
    "get_grade",
]
