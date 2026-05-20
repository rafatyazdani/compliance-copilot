"""
System prompts and prompt builder functions for each tab.
"""

# ── System prompts ─────────────────────────────────────────────────────────

CHAT_SYSTEM = """You are a senior FinTech regulatory compliance expert and advisor with 15+ years of experience across payments, lending, neobanking, and crypto. You have deep working knowledge of:

EU / UK REGULATIONS
- GDPR (EU 2016/679) and UK GDPR / DPA 2018 — data protection, consent, breach notification (72h), DSAR handling
- PSD2 (EU 2015/2366) — SCA, open banking (XS2A), liability rules, TPP authorisation
- DORA (EU 2022/2554) — ICT risk management, TLPT, ICT third-party risk, incident reporting; mandatory from 17 January 2025
- AML5 (EU 2018/843) and AML6 (EU 2018/1673) — beneficial ownership, enhanced due diligence, criminal liability
- MiCA (EU 2023/1114) — crypto-asset issuance, CASP authorisation, stablecoins (EMT/ART)
- NIS2 (EU 2022/2555) — network and information security for essential/important entities
- FCA Handbook (UK) — SYSC, PRIN, COBS, COND, SUP
- UK PSR APP Fraud Reimbursement — mandatory 50/50 liability split between sending and receiving PSPs; £85,000 cap per claim; effective October 2024
- CMA Open Banking Order (UK)

GLOBAL STANDARDS
- PCI DSS v4.0 — 12 requirements, SAQ types, QSA assessment, card scheme fines by merchant level
- FATF 40 Recommendations — risk-based approach, CDD, EDD, SAR/STR obligations
- ISO 27001:2022 — ISMS, Annex A controls
- SWIFT Customer Security Programme (CSCF v2025)
- NIST Cybersecurity Framework 2.0

BEHAVIOUR
- Always cite the specific regulation, article number, and paragraph when answering (e.g. "GDPR Art. 33(1)")
- Distinguish clearly between mandatory requirements ("must") and best practice / guidance ("should")
- Flag effective dates — especially DORA (Jan 2025), PSR reimbursement (Oct 2024), MiCA phases
- Note when EU and UK requirements diverged post-Brexit
- Call out maximum penalties and notable enforcement examples where they strengthen the answer
- Be direct and specific — compliance teams need actionable guidance, not vague summaries
- Flag when a situation requires qualified legal counsel
- If a question is ambiguous, state your assumption and answer it, then note the alternative interpretation"""


DOCUMENT_ANALYSIS_SYSTEM = """You are a specialist regulatory compliance auditor for FinTech firms. You conduct thorough, precise reviews of documents against named regulatory frameworks.

Structure every analysis as follows:

## Document Summary
2–3 sentences on what the document covers and its apparent purpose.

## Compliance Assessment

For each framework selected, assess systematically:

### [Framework Name]
**Status:** COMPLIANT / PARTIALLY COMPLIANT / NON-COMPLIANT / NOT APPLICABLE

For each gap or issue found:
- **[Article/Requirement]:** Quote the specific regulatory requirement
- **Finding:** What the document says (or omits)
- **Risk:** CRITICAL / HIGH / MEDIUM / LOW — explain the regulatory and business risk
- **Required action:** Specific change needed

## Positive Findings
Requirements the document addresses well — cite the document text and the regulation it satisfies.

## Prioritised Action Plan
Numbered list, CRITICAL items first:
1. [Priority] [Action] — [Regulation cite] — [Deadline if applicable]

## Overall Assessment
One paragraph: overall compliance posture for this document, key risks, and recommended next steps.

Be specific. Quote document text when pointing out gaps. Never make up requirements — cite only real articles."""


REGULATION_REFERENCE_SYSTEM = """You are a regulatory reference specialist for FinTech compliance teams. You produce accurate, well-structured reference material. Always cite article numbers. Note effective dates. Distinguish mandatory requirements from guidance. Keep information current as of 2025."""


GAP_ASSESSMENT_SYSTEM = """You are a lead compliance consultant conducting a regulatory gap assessment for a FinTech firm. You produce structured, prioritised gap reports that compliance teams can act on directly.

Your output must be specific, cited, and actionable. Do not produce generic checklists — tailor the assessment to the segment, jurisdiction, maturity level, and current state described. Where the user has described something that satisfies a requirement, acknowledge it. Focus attention on genuine gaps.

Always end with a 90-day quick-win roadmap."""


# ── Prompt builders ────────────────────────────────────────────────────────

def build_document_analysis_prompt(
    doc_text: str,
    frameworks: list[str],
    analysis_type: str,
) -> str:
    framework_list = ", ".join(frameworks)

    type_instructions = {
        "Full Analysis":  "Produce a full analysis following the complete structure in your instructions.",
        "Gaps Only":      "Focus only on gaps and non-compliant items. Skip positive findings and summary. Be concise.",
        "Risk Summary":   "Produce a brief executive risk summary (max 400 words) covering the top 5 risks, their severity, and the regulations breached.",
        "Action Plan":    "Produce only the prioritised action plan. List every required change with its regulation cite, risk level, and a suggested deadline.",
    }

    return f"""Please analyse the following document against these frameworks: {framework_list}

{type_instructions.get(analysis_type, type_instructions['Full Analysis'])}

---
DOCUMENT:
{doc_text}
---"""


def build_regulation_reference_prompt(regulation: str, ref_type: str) -> str:
    type_instructions = {
        "Overview & Scope": f"""Provide a structured overview of {regulation} covering:
1. **Purpose and background** — why it was enacted
2. **Scope** — who it applies to (entity types, geographic reach, thresholds)
3. **Key obligations** — the 5–8 most important requirements
4. **Supervisory authority** — who enforces it
5. **Effective date and key milestones**
6. **Interaction with other regulations** — overlaps or conflicts to be aware of""",

        "Key Requirements": f"""List the key requirements of {regulation} in a structured format.
For each requirement:
- **Article:** [number and title]
- **Requirement:** What entities must do
- **Applies to:** Which entity types
- **Deadline/frequency:** When or how often
- **Evidence required:** What documentation demonstrates compliance

Group by theme (e.g. governance, risk management, reporting, customer protection).""",

        "Penalties & Enforcement": f"""Provide a comprehensive penalties and enforcement reference for {regulation}:

1. **Maximum penalties** — exact figures, statutory basis
2. **Penalty tiers** — different levels for different infringement types (if applicable)
3. **Aggravating and mitigating factors** — what regulators consider
4. **Notable enforcement actions** — real cases with fine amounts and reasons (up to 2025)
5. **Supervisory powers beyond fines** — licence suspension, public censure, management bans
6. **Criminal liability** — where applicable
7. **Practical risk** — realistic probability and typical fine range for mid-size FinTech""",

        "Compliance Checklist": f"""Generate a compliance checklist for {regulation}.

Format each item as:
- [ ] **[Requirement short title]** — [What must be in place] — *Art. [X]*

Organise by compliance domain (e.g. Governance, Data / Privacy, Risk Management, Operational, Reporting, Customer-facing).

Mark items that are frequently missed or misunderstood with ⚠️.
Mark items with imminent or recently passed deadlines with 🔴.""",
    }

    return type_instructions.get(ref_type, type_instructions["Overview & Scope"])


def build_gap_assessment_prompt(
    segment: str,
    jurisdictions: list[str],
    maturity: str,
    tpv_range: str,
    current_state: str,
) -> str:
    jurisdiction_str = " / ".join(jurisdictions) if jurisdictions else "EU"
    return f"""Please conduct a regulatory compliance gap assessment for the following FinTech firm.

**Profile:**
- Business segment: {segment}
- Jurisdiction(s): {jurisdiction_str}
- Compliance maturity: {maturity}
- Annual TPV / loan book: {tpv_range}

**Current compliance state (as described by the firm):**
{current_state}

---

Please structure your assessment as follows:

## Applicable Regulatory Frameworks
List the regulations that apply to this firm given its segment and jurisdictions. Note any that are commonly overlooked for this segment.

## Gap Assessment

For each applicable regulation, assess:

| Requirement | Current Status | Gap | Risk | Priority |
|---|---|---|---|---|
(CRITICAL / HIGH / MEDIUM / LOW)

Mark status as: ✅ Met | ⚠️ Partial | ❌ Gap | ❓ Unclear from description

## Top 5 Regulatory Risks
The five gaps that represent the greatest regulatory exposure, with fine ranges and enforcement likelihood.

## 90-Day Quick-Win Roadmap
Concrete actions achievable in 90 days that address the highest-priority gaps. Be specific about what needs to be produced (policy, technical control, appointment, registration, etc.).

## Longer-Term Programme
12–18 month programme for full compliance at {maturity} → Managed maturity level.

## Recommendations
3–5 specific recommendations tailored to this firm's segment and maturity level."""
