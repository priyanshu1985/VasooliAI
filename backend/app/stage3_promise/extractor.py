import os
import json
from typing import Any, Dict, Optional

# Schema expected from Gemini LLM for promise extraction
EXPECTED_PROMISE_SCHEMA = {
    "type": "object",
    "properties": {
        "is_promise": {
            "type": "boolean",
            "description": "Whether the text represents an actual commitment to pay"
        },
        "promised_date": {
            "type": "string",
            "format": "date",
            "description": "Target date in ISO format YYYY-MM-DD or null if unspecified"
        },
        "promised_amount": {
            "type": "number",
            "description": "Committed payment amount in INR, or null if entire balance"
        },
        "confidence": {
            "type": "number",
            "description": "Confidence score between 0.0 and 1.0"
        },
        "reasoning": {
            "type": "string",
            "description": "Brief explanation of how the commitment was parsed"
        }
    },
    "required": ["is_promise", "confidence", "reasoning"]
}

PROMPT_TEMPLATE = """You are an AI Revenue Recovery assistant extracting payment commitments from customer messages.
Customer Reply: "{customer_reply}"

Analyze the customer reply and extract any concrete promise to pay.
Return a valid JSON object matching this schema:
{{
    "is_promise": true | false,
    "promised_date": "YYYY-MM-DD" | null,
    "promised_amount": float | null,
    "confidence": float (0.0 to 1.0),
    "reasoning": "brief explanation"
}}
"""


def extract_promise_placeholder(customer_reply: str) -> Dict[str, Any]:
    """
    Placeholder promise extraction function for Stage 3.

    TODO (Day 7-8): Implement live Google Gemini API call via `google-generativeai` package.
    Architecture rationale:
      - Stage 3 uses an LLM (Gemini free tier) because freeform customer replies
        require language understanding without costly custom NLP training.
      - Enforces strict JSON response shape.
      - Follow-up logic incorporates the Yale study insight (AI-solicited promises
        are broken more often than human ones, requiring a tighter, structured escalation ladder).

    Returns placeholder structured extraction matching the expected Gemini schema.
    """
    # Placeholder mock response for testing scaffolding before live Gemini API key integration
    lower_reply = customer_reply.lower()
    has_promise_indicator = any(w in lower_reply for w in ["will pay", "pay by", "transfer", "tomorrow", "next week", "monday", "friday", "promise"])

    return {
        "is_promise": has_promise_indicator,
        "promised_date": "2026-09-05" if has_promise_indicator else None,
        "promised_amount": None,
        "confidence": 0.85 if has_promise_indicator else 0.20,
        "reasoning": "Scaffolded placeholder extraction. Replace with Gemini API call on Day 7.",
        "_is_placeholder": True
    }
