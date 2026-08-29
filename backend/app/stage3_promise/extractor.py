import os
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

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
Return ONLY a valid JSON object matching this schema:
{{
    "is_promise": true | false,
    "promised_date": "YYYY-MM-DD" | null,
    "promised_amount": float | null,
    "confidence": float (0.0 to 1.0),
    "reasoning": "brief explanation"
}}
"""

_gemini_configured = False


def _get_gemini_client():
    global _gemini_configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    if not _gemini_configured:
        try:
            genai.configure(api_key=api_key)
            _gemini_configured = True
        except Exception:
            return None
    return genai


def extract_promise_rule_fallback(customer_reply: str) -> Dict[str, Any]:
    """Fallback rule-based extractor when LLM is offline or quota exhausted."""
    lower = customer_reply.lower()
    has_promise = any(w in lower for w in [
        "will pay", "pay by", "transfer", "tomorrow", "next week",
        "monday", "friday", "promise", "clear the balance", "by the end of this week", "2nd", "5th", "10th"
    ])
    
    # Extract date heuristic
    promised_date = None
    if has_promise:
        today = datetime.utcnow()
        if "tomorrow" in lower:
            promised_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in lower or "friday" in lower:
            promised_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        else:
            promised_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")

    # Extract amount if present (e.g. INR 4500, Rs 5000, 1500)
    amount_match = re.search(r'(?:inr|rs\.?|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)', lower)
    promised_amount = None
    if amount_match:
        try:
            promised_amount = float(amount_match.group(1).replace(",", ""))
        except ValueError:
            pass

    return {
        "is_promise": has_promise,
        "promised_date": promised_date,
        "promised_amount": promised_amount,
        "confidence": 0.85 if has_promise else 0.20,
        "reasoning": "Heuristic fallback rule parsed commitment terms from customer reply.",
        "_is_fallback": True
    }


def extract_promise(customer_reply: str) -> Dict[str, Any]:
    """
    Extracts structured payment promise commitment from freeform customer text.
    Uses Google Gemini LLM API (gemini-3.6-flash / gemini-flash-latest) with automated fallback.
    """
    client = _get_gemini_client()
    if client is None:
        return extract_promise_rule_fallback(customer_reply)

    # Try compatible models in order of priority
    candidate_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-pro-latest"]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = PROMPT_TEMPLATE.format(customer_reply=customer_reply)
            response = model.generate_content(prompt)
            
            raw_text = response.text.strip()
            # Clean markdown codeblocks if returned
            cleaned = re.sub(r'^```(?:json)?', '', raw_text, flags=re.MULTILINE)
            cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
            
            data = json.loads(cleaned)
            return {
                "is_promise": bool(data.get("is_promise", False)),
                "promised_date": data.get("promised_date"),
                "promised_amount": float(data["promised_amount"]) if data.get("promised_amount") is not None else None,
                "confidence": round(float(data.get("confidence", 0.90)), 2),
                "reasoning": str(data.get("reasoning", f"Extracted via {model_name}")),
                "model_used": model_name
            }
        except Exception:
            continue

    # Fallback if API calls fail
    return extract_promise_rule_fallback(customer_reply)
