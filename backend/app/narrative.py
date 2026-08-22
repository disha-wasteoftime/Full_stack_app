"""
LLM narrative layer.

Takes the deterministic reconciliation + analytics report (ground truth)
and produces a short, WhatsApp-style owner-facing summary, with every
number in the narrative traced back to a specific field in the report.

Uses Groq's free, OpenAI-compatible API.
"""

import json
import os
import re

import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a billing assistant for an Indian clinic. You will be given a \
JSON reconciliation + analytics report for one day. Write a short, warm, WhatsApp-appropriate \
summary for the clinic owner (2-4 short paragraphs, plain language, no jargon).

Rules:
- Every number you mention MUST come directly from the JSON you were given. Never invent, \
estimate, or round in a way that changes the figure.
- Convert paise to rupees for readability (divide by 100), using the ₹ symbol.
- If a metric isn't in the data (e.g. profit, cost price), explicitly say it isn't available \
rather than guessing or approximating it as something else.
- If total_visits is 0, say plainly that there were no visits today.

Respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "narrative": "the summary text",
  "traced_figures": [
    {"display_value": "₹42,850", "source_field": "total_billed_paise"},
    ...
  ]
}
"""


def _extract_numbers(text: str) -> set[str]:
    """
    Pull out numeric tokens that represent real figures (currency, percentages,
    or 2+ digit numbers) for grounding checks. Bare single digits are excluded
    since they're usually incidental (e.g. the "1" in "1 PM"), not report figures.
    Trailing sentence punctuation (periods, commas) is stripped so
    "₹760." at the end of a sentence still matches "760" in the report.
    """
    matches = re.findall(r"₹[\d,]+\.?\d*|[\d,]+\.?\d*%|\b\d{2,}(?:,\d{3})*\.?\d*\b", text)
    cleaned = set()
    for m in matches:
        m = m.replace("₹", "").replace(",", "").replace("%", "")
        m = m.rstrip(".")  # strip trailing sentence-ending periods
        if any(c.isdigit() for c in m):
            cleaned.add(m)
    return cleaned


def _report_numeric_values(report: dict) -> set[str]:
    values = set()

    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, (int, float)):
            values.add(str(obj))
            if isinstance(obj, int):
                rupees = obj / 100
                values.add(str(int(rupees)) if rupees == int(rupees) else str(rupees))
                values.add(f"{int(rupees):,}" if rupees == int(rupees) else f"{rupees:,}")

    walk(report)
    return values


def _fallback_narrative(report: dict) -> dict:
    billed = report.get("total_billed_paise", 0) / 100
    collected = report.get("total_collected_paise", 0) / 100
    outstanding = report.get("total_outstanding_paise", 0) / 100
    visits = report.get("total_visits", 0)

    if visits == 0:
        text = "No visits were recorded today."
    else:
        text = (
            f"Today: ₹{billed:,.0f} billed across {visits} visits, "
            f"₹{collected:,.0f} collected, ₹{outstanding:,.0f} outstanding. "
            f"(Auto-generated fallback summary — AI narrative unavailable.)"
        )

    return {
        "narrative": text,
        "traced_figures": [
            {"display_value": f"₹{billed:,.0f}", "source_field": "total_billed_paise"},
            {"display_value": f"₹{collected:,.0f}", "source_field": "total_collected_paise"},
            {"display_value": f"₹{outstanding:,.0f}", "source_field": "total_outstanding_paise"},
        ],
        "grounded": True,
        "source": "fallback_template",
    }


def generate_narrative(report: dict) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return _fallback_narrative(report)

    try:
        resp = httpx.post(
    GROQ_URL,
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(report)},
        ],
        "temperature": 0.3,
        "max_tokens": 1500,
        "reasoning_effort": "low",
    },
    timeout=30.0,
)
        resp.raise_for_status()
        
        raw_text = resp.json()["choices"][0]["message"]["content"].strip()
        raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())

        parsed = json.loads(raw_text)

        if "narrative" not in parsed or "traced_figures" not in parsed:
            return _fallback_narrative(report)

        narrative_numbers = _extract_numbers(parsed["narrative"])
        report_numbers = _report_numeric_values(report)

        ungrounded = narrative_numbers - report_numbers
        if ungrounded:
            result = _fallback_narrative(report)
            result["grounding_warning"] = f"LLM output rejected, ungrounded numbers: {ungrounded}"
            return result

        parsed["grounded"] = True
        parsed["source"] = "llm"
        return parsed

    except Exception as e:
        print(f"DEBUG - LLM call failed: {type(e).__name__}: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"DEBUG - Response status: {e.response.status_code}")
            print(f"DEBUG - Response body: {e.response.text}")
        result = _fallback_narrative(report)
        result["error_note"] = f"LLM call failed, used fallback: {type(e).__name__}"
        return result