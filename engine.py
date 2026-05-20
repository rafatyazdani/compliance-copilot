"""
Audit finding analysis engine.

Uses llm.py — works with both Anthropic and Ollama with no code changes.

Ollama model notes for JSON reliability:
  llama3.1:8b    — good balance of speed and instruction following  (recommended)
  phi4:14b       — best reasoning quality, larger download
  mistral:7b     — reliable JSON output, fast
  llama3.2:3b    — fast but may be inconsistent on complex findings
"""

import json
import re

from llm import get_response, BACKEND, ACTIVE_MODEL

# Extra emphasis on JSON-only output — critical for smaller Ollama models
# that tend to wrap responses in prose or markdown.
SYSTEM_PROMPT = """You are a senior GRC analyst specialising in ISO 27001, SOC 2 Type II, and NIST CSF.
Your task: analyse a raw audit finding or control exception and return a structured remediation plan.

CRITICAL FORMATTING RULE: respond with ONLY a valid JSON object. No markdown fences. No preamble.
No explanation before or after. The very first character of your response must be '{' and the last must be '}'.

Required JSON keys (all must be present):
{
  "issue_summary":            "2-3 sentence plain-English summary of the finding",
  "severity":                 "Critical | High | Medium | Low",
  "root_cause":               "Most likely systemic root cause — not just symptoms",
  "root_cause_category":      "Process Gap | Technical Debt | Ownership Unclear | Resource Constraint | Third-Party Dependency",
  "remediation_steps":        ["step 1", "step 2", "step 3"],
  "suggested_owner_role":     "Job title most accountable, e.g. CISO, IT Security Manager, HR Director",
  "estimated_effort":         "Low | Medium | High",
  "recommended_due_date_days": 30,
  "relevant_frameworks":      ["ISO 27001 A.9.1.2", "SOC 2 CC6.2", "NIST CSF PR.AC-1"]
}

remediation_steps must contain 3–5 items. relevant_frameworks must cite specific control references, not just framework names."""


# ── JSON extraction ────────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """
    Strip markdown fences and any prose surrounding the JSON object.
    Handles the common failure modes of smaller Ollama models.
    """
    text = text.strip()

    # Remove ```json ... ``` or ``` ... ``` fences (common with llama models)
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text, flags=re.MULTILINE)

    # Find outermost JSON object in case the model added prose before/after
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()

    return text.strip()


# ── Required fields and defaults ───────────────────────────────────────────

REQUIRED_KEYS = {
    "issue_summary",
    "severity",
    "root_cause",
    "root_cause_category",
    "remediation_steps",
    "suggested_owner_role",
    "estimated_effort",
    "recommended_due_date_days",
    "relevant_frameworks",
}

SEVERITY_VALUES        = {"Critical", "High", "Medium", "Low"}
ROOT_CAUSE_CATEGORIES  = {"Process Gap", "Technical Debt", "Ownership Unclear", "Resource Constraint", "Third-Party Dependency"}
EFFORT_VALUES          = {"Low", "Medium", "High"}


def _validate_and_coerce(data: dict) -> dict:
    """
    Fill in any missing keys with safe defaults and coerce types.
    Prevents KeyError crashes in the UI when a model omits a field.
    """
    data.setdefault("issue_summary",            "No summary provided.")
    data.setdefault("severity",                 "Medium")
    data.setdefault("root_cause",               "Root cause not identified.")
    data.setdefault("root_cause_category",      "Process Gap")
    data.setdefault("remediation_steps",        ["Review and remediate the finding."])
    data.setdefault("suggested_owner_role",     "IT Security Manager")
    data.setdefault("estimated_effort",         "Medium")
    data.setdefault("recommended_due_date_days", 30)
    data.setdefault("relevant_frameworks",      [])

    # Coerce severity / category / effort to valid enum values
    if data["severity"] not in SEVERITY_VALUES:
        data["severity"] = "Medium"
    if data["root_cause_category"] not in ROOT_CAUSE_CATEGORIES:
        data["root_cause_category"] = "Process Gap"
    if data["estimated_effort"] not in EFFORT_VALUES:
        data["estimated_effort"] = "Medium"

    # Ensure list types
    if isinstance(data["remediation_steps"], str):
        data["remediation_steps"] = [data["remediation_steps"]]
    if isinstance(data["relevant_frameworks"], str):
        data["relevant_frameworks"] = [data["relevant_frameworks"]]

    # Ensure integer due-date
    try:
        data["recommended_due_date_days"] = int(data["recommended_due_date_days"])
    except (ValueError, TypeError):
        data["recommended_due_date_days"] = 30

    return data


# ── Public API ─────────────────────────────────────────────────────────────

def analyze_finding(raw_finding: str) -> dict:
    """
    Analyse a raw audit finding and return a validated remediation plan dict.

    Raises:
        ValueError  — if the LLM response cannot be parsed as JSON after cleanup.
                      The error message includes the raw response for debugging.
    """
    messages = [{"role": "user", "content": f"Analyse this audit finding:\n\n{raw_finding}"}]
    response_text = get_response(messages, system=SYSTEM_PROMPT)

    try:
        cleaned = _extract_json(response_text)
        data    = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        backend_hint = (
            "Try a larger Ollama model: `ollama pull llama3.1:8b` or `ollama pull phi4:14b`."
            if BACKEND == "ollama"
            else "Check your API key and that the model is available."
        )
        raise ValueError(
            f"Model returned invalid JSON ({ACTIVE_MODEL}).\n"
            f"{backend_hint}\n\n"
            f"Raw response (first 600 chars):\n{response_text[:600]}"
        ) from exc

    return _validate_and_coerce(data)
