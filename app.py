import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from llm import stream_response, BACKEND, ACTIVE_MODEL
import prompts
from engine import analyze_finding

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Compliance Copilot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]          { background: #0c1425; }
[data-testid="stSidebar"] *        { color: #94a3b8; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3       { color: #e2e8f0; }
[data-testid="stAppViewContainer"] { background: #070d1a; }
.stTabs [data-baseweb="tab-list"]  { background: #0c1425; border-radius: 8px; }
.stTabs [data-baseweb="tab"]       { color: #94a3b8; }
.stTabs [aria-selected="true"]     { color: #e2e8f0; }
div[data-testid="stChatMessage"]   { background: #111827; border-radius: 8px; margin-bottom: 8px; }
textarea, input, select            { background: #111827 !important; color: #e2e8f0 !important; }
.stButton > button[kind="primary"] { background: #2563eb; border: none; }
.stButton > button[kind="primary"]:hover { background: #1d4ed8; }
.stAlert                           { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# ⚖️ Compliance Copilot")
    st.caption("FinTech regulatory guidance powered by AI")
    st.divider()

    # Backend / model status
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY")) or BACKEND == "ollama"
    status_icon = "🟢" if api_key_set else "🔴"
    st.markdown(f"**Backend:** {status_icon} `{BACKEND.upper()}`")
    st.markdown(f"**Model:** `{ACTIVE_MODEL}`")

    if not api_key_set:
        st.error("ANTHROPIC_API_KEY missing.\nCopy `.env.example` → `.env` and add your key.")

    st.divider()
    st.markdown("**Regulatory coverage:**")
    st.caption(
        "GDPR · UK GDPR · PSD2 · DORA · AML5/6 · MiCA · NIS2 · "
        "PCI DSS v4.0 · FCA Handbook · PSR APP Reimbursement · "
        "FATF · ISO 27001"
    )
    st.divider()
    st.caption(
        "To switch to **Ollama** (local, free):  \n"
        "Set `LLM_BACKEND=ollama` in `.env`  \n"
        "and `pip install openai`"
    )

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_chat, tab_doc, tab_ref, tab_gap, tab_rem = st.tabs([
    "💬 Chat",
    "📄 Document Analyser",
    "📚 Regulation Reference",
    "🔍 Gap Assessment",
    "🛡️ Remediation Planner",
])


# ── Tab 1: Chat ────────────────────────────────────────────────────────────
with tab_chat:
    st.subheader("Regulatory Compliance Chat")
    st.caption(
        "Ask anything about FinTech compliance. "
        "Responses cite specific articles and distinguish mandatory requirements from guidance."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show starter prompts if conversation is empty
    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        starters = [
            "What are the DORA ICT incident reporting timelines for significant incidents?",
            "How does PSD2 SCA exemption for low-value transactions work?",
            "What must a GDPR breach notification to a supervisory authority include?",
            "What controls does PCI DSS v4.0 require for stored cardholder data?",
            "Explain the UK PSR APP fraud reimbursement rules for receiving PSPs.",
        ]
        cols = st.columns(len(starters))
        for col, starter in zip(cols, starters):
            with col:
                if st.button(starter, key=f"starter_{starter[:20]}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": starter})
                    st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask a compliance question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = st.write_stream(
                stream_response(st.session_state.messages, system=prompts.CHAT_SYSTEM)
            )
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Controls row
    if st.session_state.messages:
        col_clear, col_export, _ = st.columns([1, 1, 6])
        with col_clear:
            if st.button("🗑 Clear", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()
        with col_export:
            transcript = "\n\n".join(
                f"**{m['role'].upper()}:** {m['content']}"
                for m in st.session_state.messages
            )
            st.download_button(
                "⬇ Export",
                data=transcript,
                file_name="compliance_chat.md",
                mime="text/markdown",
                key="export_chat",
            )


# ── Tab 2: Document Analyser ───────────────────────────────────────────────
with tab_doc:
    st.subheader("Compliance Document Analyser")
    st.caption(
        "Paste any policy, procedure, contract, or process document. "
        "The analyser checks it against your chosen frameworks and flags gaps with article-level citations."
    )

    col_left, col_right = st.columns([3, 2])

    with col_left:
        doc_text = st.text_area(
            "Document text",
            height=280,
            placeholder=(
                "Paste the full text of your policy, procedure, data processing agreement, "
                "incident response plan, or any other compliance document here..."
            ),
        )

    with col_right:
        frameworks = st.multiselect(
            "Check against",
            [
                "GDPR / UK GDPR",
                "PSD2",
                "DORA",
                "AML5 / AML6",
                "MiCA",
                "NIS2",
                "PCI DSS v4.0",
                "FCA Handbook",
                "UK PSR APP Reimbursement",
                "FATF Recommendations",
                "ISO 27001:2022",
            ],
            default=["GDPR / UK GDPR", "DORA"],
        )

        analysis_type = st.radio(
            "Output type",
            ["Full Analysis", "Gaps Only", "Risk Summary", "Action Plan"],
            help=(
                "Full Analysis: complete structured report  |  "
                "Gaps Only: non-compliant items only  |  "
                "Risk Summary: executive 400-word summary  |  "
                "Action Plan: prioritised remediation list"
            ),
        )

    run_analysis = st.button(
        "Analyse Document",
        type="primary",
        disabled=not doc_text.strip() or not frameworks,
    )

    if not doc_text.strip():
        st.info("Paste a document above to get started.")
    elif not frameworks:
        st.warning("Select at least one framework to check against.")

    if run_analysis and doc_text.strip() and frameworks:
        prompt = prompts.build_document_analysis_prompt(doc_text, frameworks, analysis_type)
        with st.container():
            st.markdown("---")
            st.write_stream(
                stream_response(
                    [{"role": "user", "content": prompt}],
                    system=prompts.DOCUMENT_ANALYSIS_SYSTEM,
                )
            )


# ── Tab 3: Regulation Reference ────────────────────────────────────────────
with tab_ref:
    st.subheader("Regulation Quick Reference")
    st.caption(
        "Generate structured reference cards, key article summaries, "
        "penalty tables, and compliance checklists for any major FinTech regulation."
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        regulation = st.selectbox(
            "Select regulation",
            [
                "GDPR (EU 2016/679)",
                "UK GDPR / Data Protection Act 2018",
                "PSD2 (EU 2015/2366)",
                "DORA (EU 2022/2554)",
                "AML6 (EU 2018/1673)",
                "MiCA (EU 2023/1114)",
                "NIS2 (EU 2022/2555)",
                "PCI DSS v4.0",
                "FCA SYSC / Senior Management",
                "UK PSR APP Fraud Reimbursement (Oct 2024)",
                "FATF 40 Recommendations",
                "ISO 27001:2022",
            ],
        )

    with col_right:
        ref_type = st.radio(
            "View",
            ["Overview & Scope", "Key Requirements", "Penalties & Enforcement", "Compliance Checklist"],
        )

    if st.button("Generate Reference", type="primary"):
        prompt = prompts.build_regulation_reference_prompt(regulation, ref_type)
        st.markdown("---")
        st.write_stream(
            stream_response(
                [{"role": "user", "content": prompt}],
                system=prompts.REGULATION_REFERENCE_SYSTEM,
            )
        )


# ── Tab 4: Gap Assessment ──────────────────────────────────────────────────
with tab_gap:
    st.subheader("Compliance Gap Assessment")
    st.caption(
        "Describe your current compliance programme. "
        "The tool identifies gaps against the regulations applicable to your segment and jurisdiction, "
        "then produces a prioritised remediation roadmap."
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        segment = st.selectbox(
            "Business segment",
            ["Payments / PSP", "Lending / BNPL", "Neobank", "Crypto Exchange", "Other FinTech"],
        )
        jurisdictions = st.multiselect(
            "Jurisdiction(s)",
            ["EU", "UK", "US", "Global / Multi-jurisdiction"],
            default=["EU", "UK"],
        )

    with col_right:
        maturity = st.select_slider(
            "Current compliance maturity",
            options=["Initial", "Developing", "Defined", "Managed", "Optimising"],
            value="Developing",
            help=(
                "Initial: ad-hoc, no formal programme  |  "
                "Developing: some policies, gaps remain  |  "
                "Defined: documented programme in place  |  "
                "Managed: measured and monitored  |  "
                "Optimising: continuous improvement"
            ),
        )
        tpv_range = st.selectbox(
            "Annual TPV / loan book",
            ["< €100M", "€100M – €1B", "€1B – €10B", "> €10B"],
        )

    current_state = st.text_area(
        "Describe your current compliance controls, policies, and programmes",
        height=220,
        placeholder=(
            "Be as specific as you can. For example:\n\n"
            "- We have a GDPR privacy policy, a DPO appointed, and a data register in place.\n"
            "- AML screening runs via Refinitiv World-Check on onboarding.\n"
            "- ISO 27001 certified since 2023, certificate valid until 2026.\n"
            "- No formal DORA ICT risk framework yet — early-stage gap assessment ongoing.\n"
            "- Incident response plan exists but not tested in the last 12 months.\n"
            "- No MiCA readiness work started."
        ),
    )

    run_assessment = st.button(
        "Generate Gap Report",
        type="primary",
        disabled=not current_state.strip() or not jurisdictions,
    )

    if not current_state.strip():
        st.info("Describe your current compliance state above to generate a gap report.")
    elif not jurisdictions:
        st.warning("Select at least one jurisdiction.")

    if run_assessment and current_state.strip() and jurisdictions:
        prompt = prompts.build_gap_assessment_prompt(
            segment, jurisdictions, maturity, tpv_range, current_state
        )
        st.markdown("---")
        st.write_stream(
            stream_response(
                [{"role": "user", "content": prompt}],
                system=prompts.GAP_ASSESSMENT_SYSTEM,
            )
        )


# ── Tab 5: Remediation Planner ─────────────────────────────────────────────
with tab_rem:
    st.subheader("Audit Finding Remediation Planner")
    st.caption(
        "Paste a raw audit finding or control exception. "
        "The engine classifies severity, identifies root cause, and produces a structured remediation plan "
        "with framework citations — structured JSON rendered as a visual report."
    )

    EXAMPLE_FINDING = """\
Access review for privileged accounts has not been completed for Q4 2024.
IT confirmed that 12 former employees retain active domain admin accounts in Active Directory.
No formal deprovisioning process exists for leavers; HR notifies IT informally via email.
Finding raised during SOC 2 Type II audit by external auditors."""

    with st.expander("Load example finding"):
        if st.button("Use example"):
            st.session_state["rem_finding"] = EXAMPLE_FINDING
            st.rerun()

    finding_input = st.text_area(
        "Paste audit finding or control exception",
        value=st.session_state.get("rem_finding", ""),
        height=180,
        placeholder=(
            "e.g. 'Penetration test identified that the production API does not enforce rate limiting. "
            "An attacker could enumerate customer account numbers via the /balance endpoint. "
            "Finding severity rated High by external pentest team.'"
        ),
        key="rem_finding_input",
    )

    # Keep textarea value in session state so example persists across reruns
    if finding_input:
        st.session_state["rem_finding"] = finding_input

    run_rem = st.button(
        "Generate Remediation Plan",
        type="primary",
        disabled=not finding_input.strip(),
    )

    if not finding_input.strip():
        st.info("Paste an audit finding above to generate a remediation plan.")

    if run_rem and finding_input.strip():
        with st.spinner("Analysing finding..."):
            try:
                result = analyze_finding(finding_input)

                severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
                effort_icon   = {"High": "🔺", "Medium": "🔸", "Low": "🔹"}
                icon = severity_icon.get(result["severity"], "⚪")

                st.markdown("---")

                col_main, col_meta = st.columns([3, 2])

                with col_main:
                    st.markdown(
                        f"### {icon} {result['severity']} Severity — Issue Summary"
                    )
                    st.write(result["issue_summary"])

                    st.markdown("#### 🔍 Root Cause")
                    st.write(result["root_cause"])
                    st.caption(f"Category: `{result['root_cause_category']}`")

                    st.markdown("#### ✅ Remediation Steps")
                    for i, step in enumerate(result["remediation_steps"], 1):
                        st.write(f"**{i}.** {step}")

                with col_meta:
                    st.markdown("#### 📋 Assignment")
                    st.metric("Suggested Owner", result["suggested_owner_role"])
                    st.metric(
                        "Effort",
                        f"{effort_icon.get(result['estimated_effort'], '')} {result['estimated_effort']}",
                    )
                    st.metric(
                        "Target Closure",
                        f"{result['recommended_due_date_days']} days",
                    )

                    st.markdown("#### 📚 Framework Controls")
                    for fw in result["relevant_frameworks"]:
                        st.code(fw, language=None)

                with st.expander("Raw JSON"):
                    st.json(result)

                # Download as JSON
                st.download_button(
                    "⬇ Download plan (JSON)",
                    data=__import__("json").dumps(result, indent=2),
                    file_name="remediation_plan.json",
                    mime="application/json",
                )

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
