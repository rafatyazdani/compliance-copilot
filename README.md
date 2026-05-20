# Compliance Copilot

An AI-powered GRC assistant for FinTech compliance teams. Paste audit findings, regulatory documents, or describe your current programme — get structured remediation plans, gap reports, and regulatory reference material in seconds.

Built with Streamlit. Runs on Anthropic Claude or locally via Ollama — swap with one line in `.env`.

---

## Quick Start

```bash
# 1. Clone / copy the project
cd compliance-copilot

# 2. Activate the virtual environment
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # Mac / Linux

# 3. Configure
copy .env.example .env           # Windows
cp .env.example .env             # Mac / Linux
# → Open .env and add your ANTHROPIC_API_KEY

# 4. Run
streamlit run app.py
```

App opens at `http://localhost:8501`.

---

## Running Free with Ollama (Local)

No API key, no cost, fully offline.

```bash
# 1. Install Ollama
#    https://ollama.com → download for your OS

# 2. Pull a model
ollama pull llama3.1:8b        # recommended — good balance of speed and quality
# ollama pull phi4:14b         # better reasoning, larger download (~9 GB)
# ollama pull mistral:7b       # fast, reliable JSON output

# 3. Install the extra dependency
pip install openai             # Ollama uses an OpenAI-compatible API

# 4. Update .env
LLM_BACKEND=ollama
OLLAMA_MODEL=llama3.1:8b

# 5. Run
streamlit run app.py
```

The sidebar shows the active backend and model. No other code changes are needed.

**Model guidance for Ollama:**

| Use case | Recommended model |
|---|---|
| Chat + document analysis | `llama3.1:8b` |
| Remediation Planner (JSON output) | `llama3.1:8b` or `phi4:14b` |
| Fastest response / low RAM | `llama3.2:3b` (may miss JSON fields) |
| Best overall quality | `phi4:14b` |

---

## Features

### 💬 Chat
Conversational compliance Q&A. Responses cite specific article numbers and distinguish mandatory requirements from best practice guidance.

- Full conversation history with export to Markdown
- Five starter prompts for common questions
- Covers: GDPR, PSD2, DORA, AML5/6, MiCA, NIS2, PCI DSS v4.0, FCA Handbook, PSR APP Reimbursement, FATF, ISO 27001

### 📄 Document Analyser
Paste any policy, procedure, contract, or process document. Select one or more frameworks. Get a structured compliance review.

Output modes:
- **Full Analysis** — summary, gaps with article citations, risks, positive findings, prioritised action plan
- **Gaps Only** — non-compliant items only, concise
- **Risk Summary** — 400-word executive summary of the top risks
- **Action Plan** — prioritised remediation list with regulation cites and suggested deadlines

### 📚 Regulation Reference
Generate structured reference material for any major FinTech regulation on demand.

Regulations covered: GDPR, UK GDPR/DPA 2018, PSD2, DORA, AML6, MiCA, NIS2, PCI DSS v4.0, FCA SYSC, UK PSR APP Reimbursement, FATF 40 Recommendations, ISO 27001:2022.

View types:
- **Overview & Scope** — purpose, who it applies to, key obligations, regulator, effective date
- **Key Requirements** — article-by-article breakdown with evidence requirements
- **Penalties & Enforcement** — fine structure, aggravating factors, notable enforcement cases
- **Compliance Checklist** — actionable checklist with article references, flagged for commonly missed items and upcoming deadlines

### 🔍 Gap Assessment
Describe your current compliance programme. Get a gap report tailored to your business segment and jurisdictions.

Inputs:
- Business segment: Payments/PSP · Lending/BNPL · Neobank · Crypto Exchange
- Jurisdictions: EU · UK · US · Global
- Compliance maturity: Initial → Optimising
- Annual TPV / loan book range
- Free-text description of current controls, certifications, and programmes

Output:
- Applicable regulatory frameworks for the segment/jurisdiction combination
- Gap table: requirement · current status · gap · risk · priority
- Top 5 regulatory risks with fine ranges
- 90-day quick-win roadmap
- 12–18 month compliance programme

### 🛡️ Remediation Planner
Paste a raw audit finding or control exception. Returns a structured remediation plan as both a visual report and downloadable JSON — suitable for dropping into a risk register or ticketing system.

Output fields:

| Field | Description |
|---|---|
| `issue_summary` | 2–3 sentence plain-English summary |
| `severity` | Critical / High / Medium / Low |
| `root_cause` | Systemic root cause, not just symptoms |
| `root_cause_category` | Process Gap / Technical Debt / Ownership Unclear / Resource Constraint / Third-Party Dependency |
| `remediation_steps` | 3–5 specific, actionable steps |
| `suggested_owner_role` | Job title most accountable |
| `estimated_effort` | Low / Medium / High |
| `recommended_due_date_days` | Integer — realistic days to closure |
| `relevant_frameworks` | Specific control references, e.g. `ISO 27001 A.9.1.2`, `SOC 2 CC6.2` |

---

## Project Structure

```
compliance-copilot/
├── app.py            # Streamlit UI — all five tabs
├── engine.py         # Audit finding analysis — JSON parsing, validation, error handling
├── llm.py            # LLM abstraction — swap Anthropic ↔ Ollama here
├── prompts.py        # System prompts and prompt builder functions
├── .env.example      # Configuration template
├── .env              # Your local config (never commit this)
├── .gitignore
└── requirements.txt
```

### How the abstraction works

All LLM calls go through two functions in `llm.py`:

```python
stream_response(messages, system)   # yields text chunks — used by Chat, Doc Analyser, Reference, Gap Assessment
get_response(messages, system)      # returns full string — used by Remediation Planner (needs complete JSON)
```

The backend is selected by `LLM_BACKEND` in `.env`. Switching from Anthropic to Ollama (or back) requires no code changes.

---

## Configuration

Copy `.env.example` to `.env` and edit:

```bash
# Backend: "anthropic" or "ollama"
LLM_BACKEND=anthropic

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001   # or claude-sonnet-4-6 for higher quality

# Ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434/v1    # default, change if Ollama runs elsewhere
```

**Anthropic model options:**

| Model | Speed | Cost | Best for |
|---|---|---|---|
| `claude-haiku-4-5-20251001` | Fast | Low | Development, testing, chat |
| `claude-sonnet-4-6` | Medium | Medium | Production, complex analysis |

---

## Dependencies

```
anthropic>=0.103.0     # Anthropic SDK
streamlit>=1.57.0      # UI framework
python-dotenv>=1.0.0   # .env loading
openai>=1.0.0          # Required for Ollama backend only
```

Install all (including Ollama support):
```bash
pip install anthropic streamlit python-dotenv openai
```

---

## Regulatory Coverage

| Regulation | Jurisdiction | Effective |
|---|---|---|
| GDPR (EU 2016/679) | EU + EEA | May 2018 |
| UK GDPR / DPA 2018 | UK | Jan 2021 (post-Brexit) |
| PSD2 (EU 2015/2366) | EU | Jan 2018 |
| DORA (EU 2022/2554) | EU | **Jan 2025** |
| AML6 (EU 2018/1673) | EU | Dec 2020 |
| MiCA (EU 2023/1114) | EU | Dec 2024 (CASP provisions) |
| NIS2 (EU 2022/2555) | EU | Oct 2024 |
| FCA Handbook (SYSC, PRIN, COBS) | UK | Ongoing |
| PSR APP Fraud Reimbursement | UK | **Oct 2024** |
| PCI DSS v4.0 | Global | Mar 2024 (v3.2.1 retired) |
| FATF 40 Recommendations | Global | Ongoing |
| ISO 27001:2022 | Global | Oct 2022 |

---

## Limitations

- All outputs are AI-generated and indicative. They are not legal advice and should not be relied on as a substitute for qualified legal or compliance counsel.
- Regulatory guidance, enforcement practice, and fine amounts change. Verify citations against primary sources before use in formal compliance programmes.
- Remediation Planner outputs structured JSON — smaller Ollama models (3B parameters) may occasionally omit fields or produce invalid JSON. The engine validates and fills defaults, but complex findings benefit from larger models (`llama3.1:8b` or above).
- The Document Analyser works best with documents under ~8,000 words. Larger documents should be split by section before analysis.
