#!/usr/bin/env python3
"""MEOK AI Labs — feedback-analyzer-ai-mcp MCP Server. Analyze customer feedback for sentiment and themes."""

import json
import re
from datetime import datetime, timezone
from collections import defaultdict, Counter

from mcp.server.fastmcp import FastMCP
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

POSITIVE_WORDS = ["good", "great", "love", "excellent", "amazing", "fantastic", "wonderful", "best", "happy", "pleased", "satisfied", "recommend"]
NEGATIVE_WORDS = ["bad", "poor", "hate", "terrible", "awful", "worst", "disappointed", "frustrated", "broken", "useless", "annoying", "slow"]
NEUTRAL_WORDS = ["okay", "fine", "average", "decent", "normal", "standard", "acceptable"]

THEME_KEYWORDS = {
    "pricing": ["price", "cost", "expensive", "cheap", "affordable", "value", "money", "fee"],
    "quality": ["quality", "durable", "broken", "defect", "reliable", "sturdy", "flimsy"],
    "support": ["support", "help", "service", "response", "staff", "agent", "customer service"],
    "usability": ["easy", "difficult", "intuitive", "confusing", "user-friendly", "complex", "simple"],
    "delivery": ["shipping", "delivery", "late", "fast", "arrived", "package", "tracking"],
    "features": ["feature", "functionality", "missing", "update", "upgrade", "option", "capability"],
}

mcp = FastMCP("feedback-analyzer-ai", instructions="Analyze customer feedback for sentiment, themes, and actionable insights.")


def _score_sentiment(text: str) -> dict:
    """Score a single piece of feedback."""
    lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lower)
    neu = sum(1 for w in NEUTRAL_WORDS if w in lower)
    total = pos + neg + neu or 1
    score = (pos - neg) / total
    label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
    return {"text": text[:120], "score": round(score, 3), "label": label, "positive_hits": pos, "negative_hits": neg}


@mcp.tool()
def analyze_feedback(feedback: list[str], api_key: str = "") -> str:
    """Analyze customer feedback for sentiment breakdown with per-item scores."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    results = [_score_sentiment(f) for f in feedback]
    positive = sum(1 for r in results if r["label"] == "positive")
    negative = sum(1 for r in results if r["label"] == "negative")
    neutral = sum(1 for r in results if r["label"] == "neutral")
    avg_score = round(sum(r["score"] for r in results) / max(len(results), 1), 3)

    return json.dumps({
        "total": len(feedback),
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "average_score": avg_score,
        "items": results,
    }, indent=2)


@mcp.tool()
def extract_themes(feedback: list[str], api_key: str = "") -> str:
    """Extract recurring themes from feedback using keyword matching."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    theme_counts = Counter()
    theme_examples = defaultdict(list)
    for text in feedback:
        lower = text.lower()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                theme_counts[theme] += 1
                if len(theme_examples[theme]) < 2:
                    theme_examples[theme].append(text[:100])

    themes = []
    for theme, count in theme_counts.most_common():
        themes.append({
            "theme": theme,
            "mentions": count,
            "percentage": round(count / max(len(feedback), 1) * 100, 1),
            "examples": theme_examples[theme],
        })

    return json.dumps({"total_feedback": len(feedback), "themes": themes}, indent=2)


@mcp.tool()
def sentiment_trend(feedback_with_dates: list[dict], api_key: str = "") -> str:
    """Compute sentiment trend over time. Each item needs 'text' and 'date' (YYYY-MM-DD) keys."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    by_date = defaultdict(list)
    for item in feedback_with_dates:
        date = item.get("date", "unknown")
        score = _score_sentiment(item.get("text", ""))["score"]
        by_date[date].append(score)

    trend = []
    for date in sorted(by_date.keys()):
        scores = by_date[date]
        trend.append({
            "date": date,
            "count": len(scores),
            "avg_sentiment": round(sum(scores) / len(scores), 3),
            "min": round(min(scores), 3),
            "max": round(max(scores), 3),
        })

    direction = "improving" if len(trend) >= 2 and trend[-1]["avg_sentiment"] > trend[0]["avg_sentiment"] else \
                "declining" if len(trend) >= 2 and trend[-1]["avg_sentiment"] < trend[0]["avg_sentiment"] else "stable"

    return json.dumps({"trend": trend, "direction": direction, "periods": len(trend)}, indent=2)


@mcp.tool()
def generate_summary(feedback: list[str], max_points: int = 5, api_key: str = "") -> str:
    """Generate an executive summary of feedback with key takeaways and recommendations."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    results = [_score_sentiment(f) for f in feedback]
    positive = [r for r in results if r["label"] == "positive"]
    negative = [r for r in results if r["label"] == "negative"]

    # Extract theme counts for recommendations
    theme_counts = Counter()
    for text in feedback:
        lower = text.lower()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                theme_counts[theme] += 1

    top_issues = [t for t, _ in theme_counts.most_common(max_points)]
    recommendations = []
    if "pricing" in top_issues:
        recommendations.append("Review pricing strategy - frequently mentioned by customers")
    if "support" in top_issues:
        recommendations.append("Invest in customer support training and response times")
    if "quality" in top_issues:
        recommendations.append("Conduct quality audit on products/services")
    if "usability" in top_issues:
        recommendations.append("Run UX review to address usability concerns")
    if "delivery" in top_issues:
        recommendations.append("Optimize logistics and shipping processes")

    satisfaction_pct = round(len(positive) / max(len(results), 1) * 100, 1)

    return json.dumps({
        "total_responses": len(feedback),
        "satisfaction_rate": satisfaction_pct,
        "positive_count": len(positive),
        "negative_count": len(negative),
        "top_themes": top_issues[:max_points],
        "top_positive": [r["text"] for r in sorted(positive, key=lambda x: -x["score"])[:3]],
        "top_negative": [r["text"] for r in sorted(negative, key=lambda x: x["score"])[:3]],
        "recommendations": recommendations[:max_points],
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
