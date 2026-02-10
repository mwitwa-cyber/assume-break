"""Streamlit web UI for ASSUME-BREAK stress testing."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="ASSUME-BREAK",
    page_icon="🔨",
    layout="wide",
)

st.title("ASSUME-BREAK")
st.markdown("**Adversarial business plan stress-testing against Zambian economic realities**")

# ── Sidebar Settings ──
with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Claude Model",
        ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"],
        index=0,
    )
    max_revisions = st.slider("Max Revision Rounds", 1, 5, 3)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    st.divider()
    st.markdown("### Workflow")
    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=rounded];
        Extract [label="Extract\\nAssumptions"];
        Reality [label="Retrieve\\nReality"];
        Adversary [label="Adversary\\nCritique"];
        Proponent [label="Proponent\\nRevise"];
        Judge [label="Judge"];
        End [label="Final\\nVerdict", shape=doublecircle];

        Extract -> Reality -> Adversary;
        Adversary -> End [label="FATAL"];
        Adversary -> Proponent [label="MAJOR"];
        Adversary -> Judge [label="MINOR"];
        Proponent -> Judge;
        Judge -> End [label="VALIDATED\\nor BROKEN"];
        Judge -> Adversary [label="NEEDS\\nREVISION"];
    }
    """)

# ── Main Content ──
plan_text = st.text_area(
    "Enter your business plan",
    height=250,
    placeholder="Describe your Zambian business plan here...\n\nExample: We plan to start a fresh produce delivery service from Mongu (Western Province) to Lusaka...",
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("Run Stress Test", type="primary", use_container_width=True)

if run_button and plan_text.strip():
    import os

    from assume_break.config import get_settings
    from assume_break.graph import stress_test_plan
    from assume_break.report import result_to_dict

    # Apply sidebar settings via environment
    os.environ["CLAUDE_MODEL"] = model
    os.environ["TEMPERATURE"] = str(temperature)

    # Clear cached settings so new env vars take effect
    get_settings.cache_clear()

    with st.spinner("Running ASSUME-BREAK stress test..."):
        result = stress_test_plan(plan_text, max_revisions=max_revisions)

    # ── Results ──
    st.divider()

    # Status Banner
    status_colors = {
        "VALIDATED": "green",
        "BROKEN": "red",
        "NEEDS_REVISION": "orange",
        "UNDER_REVIEW": "blue",
        "DRAFT": "gray",
    }
    color = status_colors.get(result.plan_status.value, "gray")
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">PLAN STATUS: {result.plan_status.value}</h2>
            <p style="color: white; margin: 5px 0 0 0;">Severity: {result.critique_severity.value} | Rounds: {result.revision_count}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Assumptions
    with st.expander("Extracted Assumptions", expanded=True):
        for i, assumption in enumerate(result.assumptions, 1):
            st.markdown(f"**{i}.** {assumption}")

    # Reality Context
    with st.expander("Reality Context & Citations"):
        for citation in result.reality_citations:
            st.markdown(f"- {citation}")

    # Adversarial Debate
    with st.expander("Adversarial Debate", expanded=True):
        for round_data in result.critiques:
            round_num = round_data.get("round", "?")
            st.markdown(f"#### Critique Round {round_num}")
            for critique in round_data.get("critiques", []):
                verdict = critique.get("verdict", "MINOR")
                icon = {"FATAL": "🔴", "MAJOR": "🟡", "MINOR": "🟢"}.get(verdict, "⚪")
                st.markdown(f"{icon} **[{verdict}]** {critique.get('fracture', 'N/A')}")
                st.markdown(f"> **Reality:** {critique.get('reality', 'N/A')}")
                st.markdown(f"> **Impact:** {critique.get('impact', 'N/A')}")
                st.markdown(f"> *Citation: {critique.get('citation', 'N/A')}*")
                st.markdown("---")

        for defense_round in result.defenses:
            round_num = defense_round.get("round", "?")
            st.markdown(f"#### Defense Round {round_num}")
            for defense in defense_round.get("defenses", []):
                st.markdown(f"**RE:** {defense.get('response_to', 'N/A')}")
                if defense.get("defense"):
                    st.markdown(f"> {defense['defense']}")
                if defense.get("revision"):
                    st.markdown(f"> **Revision:** {defense['revision']}")
                st.markdown("---")

    # JSON Export
    with st.expander("Raw JSON Output"):
        st.json(result_to_dict(result))

elif run_button:
    st.warning("Please enter a business plan before running the stress test.")
