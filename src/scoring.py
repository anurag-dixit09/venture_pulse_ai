"""Scoring and formatting utilities for Venture Pulse AI."""


def format_inr(value: float) -> str:
    if value >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"
    if value >= 100000:
        return f"₹{value / 100000:,.2f} L"
    return f"₹{value:,.0f}"


def get_grade(score: int) -> tuple[str, str]:
    if score >= 90:
        return "A+", "positive"
    if score >= 80:
        return "A-", "positive"
    if score >= 70:
        return "B+", "positive"
    if score >= 60:
        return "B-", "neutral"
    if score >= 50:
        return "C", "neutral"
    return "F", "negative"


def compute_scorecard(
    tam_size: float,
    growth_rate: float,
    sector: str,
    risk_profile: str,
    initial_capital: float,
    burn_rate: float,
    cac: float,
    ltv: float,
) -> dict:
    tam_score = min(100, int((tam_size / 1000000000) * 100))
    growth_score = min(40, int(growth_rate / 12.5))
    market_score = int((tam_score * 0.6) + (growth_score * 0.4))

    sector_complexity = {
        "SaaS/Software": 18,
        "FinTech": 28,
        "HealthTech / BioTech": 32,
        "AI / DeepTech": 22,
        "Web3 / Crypto": 40,
        "Consumer Tech": 14,
    }
    risk_penalty = 0 if risk_profile == "Low / Defensive" else 8 if risk_profile == "Moderate / Balanced" else 15
    legal_score = max(0, min(100, 100 - sector_complexity.get(sector, 20) - risk_penalty))

    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    runway_months = initial_capital / burn_rate if burn_rate > 0 else 0
    ltv_score = min(100, int((ltv_cac_ratio / 3.0) * 100))
    runway_score = min(100, int((runway_months / 18.0) * 100))
    financial_score = int((ltv_score * 0.5) + (runway_score * 0.5))
    overall_score = int((market_score * 0.35) + (legal_score * 0.25) + (financial_score * 0.40))
    grade, color_class = get_grade(overall_score)

    return {
        "market_score": market_score,
        "legal_score": legal_score,
        "financial_score": financial_score,
        "overall_score": overall_score,
        "grade": grade,
        "color_class": color_class,
        "ltv_cac_ratio": ltv_cac_ratio,
        "runway_months": runway_months,
    }
