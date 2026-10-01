
import streamlit as st

from graph.graph import build_graph
from models.schemas import AgentState


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchOS - Multi-Agent Research",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM DARK THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(99, 102, 241, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(139, 92, 246, 0.10),
                transparent 30%
            ),
            #08090f;
        color: #f5f5f7;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ======================================================
       STREAMLIT TEXT
       ====================================================== */

    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
    }

    h2 {
        color: #ffffff !important;
        font-weight: 750 !important;
    }

    h3 {
        color: #ffffff !important;
    }

    p {
        color: #a0a5b5;
    }

    /* ======================================================
       TEXT AREA
       ====================================================== */

    div[data-testid="stTextArea"] textarea {
        background: #11131c !important;
        color: #ffffff !important;
        border: 1px solid #292d3d !important;
        border-radius: 14px !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    /* ======================================================
       MAIN BUTTON
       ====================================================== */

    div.stButton > button {
        width: 100%;
        min-height: 3.1rem;
        border-radius: 12px;
        border: 1px solid rgba(129, 140, 248, 0.35);
        background: linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }

    div.stButton > button:hover {
        border-color: #a5b4fc;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
    }

    /* ======================================================
       METRICS
       ====================================================== */

    div[data-testid="stMetric"] {
        background: #10121a;
        border: 1px solid #292d3d;
        border-radius: 14px;
        padding: 1rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #777d91 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* ======================================================
       STATUS BOX
       ====================================================== */

    div[data-testid="stStatus"] {
        background: #10121a !important;
        border: 1px solid #292d3d !important;
        border-radius: 14px !important;
    }

    /* ======================================================
       EXPANDERS
       ====================================================== */

    div[data-testid="stExpander"] {
        background: #10121a;
        border: 1px solid #292d3d;
        border-radius: 12px;
    }

    /* ======================================================
       CODE BLOCKS
       ====================================================== */

    pre {
        border-radius: 12px !important;
    }

    /* ======================================================
       FOOTER
       ====================================================== */

    .footer-text {
        text-align: center;
        color: #555b6e;
        font-size: 0.75rem;
        margin-top: 4rem;
        padding-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_value(obj, key, default=""):
    """
    Safely get a value from either a dictionary
    or a Pydantic object.
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def show_agent_event(event):
    """
    Display one agent execution event.

    IMPORTANT:
    This function intentionally does NOT inject HTML.
    """

    agent = get_value(
        event,
        "agent",
        "Unknown Agent",
    )

    status = str(
        get_value(
            event,
            "status",
            "unknown",
        )
    ).lower()

    message = get_value(
        event,
        "message",
        "",
    )

    if status == "started":

        st.info(
            f"↻  **{agent}**\n\n"
            f"{message}"
        )

    elif status == "completed":

        st.success(
            f"✓  **{agent}**\n\n"
            f"{message}"
        )

    elif status == "passed":

        st.success(
            f"✓  **{agent} — Verification Passed**\n\n"
            f"{message}"
        )

    elif status == "failed":

        st.error(
            f"✗  **{agent}**\n\n"
            f"{message}"
        )

    elif status == "error":

        st.warning(
            f"!  **{agent}**\n\n"
            f"{message}"
        )

    else:

        st.info(
            f"↻  **{agent}**\n\n"
            f"{message}"
        )


def show_finding(index, finding):
    """
    Display a research finding without raw HTML.
    """

    claim = get_value(
        finding,
        "claim",
        "",
    )

    evidence = get_value(
        finding,
        "evidence",
        "",
    )

    source_url = get_value(
        finding,
        "source_url",
        "",
    )

    with st.container(border=True):

        st.markdown(
            f"#### Finding {index}"
        )

        st.markdown(
            f"**Claim**  \n{claim}"
        )

        st.markdown(
            f"**Evidence**  \n{evidence}"
        )

        if source_url:

            st.link_button(
                "Open source",
                source_url,
            )


def show_source(source):
    """
    Display a source without raw HTML.
    """

    title = get_value(
        source,
        "title",
        "Untitled source",
    )

    url = get_value(
        source,
        "url",
        "",
    )

    with st.container(border=True):

        st.markdown(
            f"**{title}**"
        )

        if url:

            st.link_button(
                "Open source",
                url,
            )


# ============================================================
# HERO
#
# NO HTML HERE.
# This is deliberate.
# ============================================================

st.caption(
    "MULTI-AGENT RESEARCH SYSTEM"
)

st.title(
    "Research, verify, then generate."
)

st.write(
    "Ask a research question and let a coordinated AI "
    "workflow search the web, analyze evidence, verify "
    "findings, retry weak research, and generate a final report."
)


# ============================================================
# RESEARCH QUESTION
# ============================================================

st.subheader(
    "Research Question"
)

query = st.text_area(
    "Enter your research question",
    placeholder=(
        "Example: What are the latest developments "
        "in AI agents?"
    ),
    height=120,
    label_visibility="collapsed",
)


# ============================================================
# START RESEARCH
# ============================================================

research_button = st.button(
    "Start Research",
    use_container_width=True,
)


# ============================================================
# WORKFLOW
# ============================================================

if research_button:

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not query.strip():

        st.warning(
            "Please enter a research question before starting."
        )

        st.stop()

    # --------------------------------------------------------
    # Create initial state
    # --------------------------------------------------------

    initial_state = AgentState(
        user_query=query.strip()
    )

    # --------------------------------------------------------
    # Build workflow
    # --------------------------------------------------------

    try:

        workflow = build_graph()

    except Exception as exc:

        st.error(
            "Could not build the research workflow."
        )

        st.exception(exc)

        st.stop()

    # --------------------------------------------------------
    # Run workflow
    # --------------------------------------------------------

    with st.spinner(
        "Researching, verifying and generating your report..."
    ):

        try:

            result = workflow.invoke(
                initial_state.model_dump()
            )

        except Exception as exc:

            st.error(
                "The research workflow encountered an error."
            )

            st.exception(exc)

            st.stop()

    # ========================================================
    # EXTRACT RESULT
    # ========================================================

    status = result.get(
        "status",
        "unknown",
    )

    verdict = result.get(
        "verification_verdict",
        "N/A",
    )

    attempts = result.get(
        "research_attempts",
        0,
    )

    sources = result.get(
        "sources",
        [],
    )

    findings = result.get(
        "research_findings",
        [],
    )

    execution_history = result.get(
        "execution_history",
        [],
    )

    final_answer = result.get(
        "final_answer",
        None,
    )

    verification_reason = result.get(
        "verification_reason",
        None,
    )

    error = result.get(
        "error",
        None,
    )

    # ========================================================
    # QUERY
    # ========================================================

    st.divider()

    st.header(
        "Research Query"
    )

    st.info(
        query.strip()
    )

    # ========================================================
    # WORKFLOW OVERVIEW
    # ========================================================

    st.header(
        "Workflow Overview"
    )

    st.caption(
        "Research → Verify → Retry → Write"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if status == "completed":
            display_status = "Completed"

        elif status == "verification_failed":
            display_status = "Failed"

        elif status == "failed":
            display_status = "Failed"

        else:
            display_status = str(
                status
            ).replace(
                "_",
                " ",
            ).title()

        st.metric(
            "Workflow Status",
            display_status,
        )

    with col2:

        st.metric(
            "Research Attempts",
            attempts,
        )

    with col3:

        st.metric(
            "Sources",
            len(sources),
        )

    with col4:

        st.metric(
            "Verification",
            verdict,
        )

    # ========================================================
    # OVERALL RESULT
    # ========================================================

    if (
        status == "completed"
        and str(verdict).upper() == "PASS"
    ):

        st.success(
            "Research completed and successfully verified."
        )

    elif status == "verification_failed":

        st.error(
            f"Research did not pass verification after "
            f"{attempts} attempt(s)."
        )

        if verification_reason:

            with st.expander(
                "View verification details"
            ):

                st.code(
                    verification_reason
                )

    elif status == "failed":

        st.error(
            error
            or "The research workflow failed."
        )

    # ========================================================
    # AGENT EXECUTION
    # ========================================================

    st.header(
        "Agent Execution"
    )

    st.caption(
        "Research → Verify → Retry → Write"
    )

    if execution_history:

        for event in execution_history:

            show_agent_event(
                event
            )

    else:

        st.info(
            "No execution history was returned."
        )

    # ========================================================
    # RESEARCH FINDINGS
    # ========================================================

    st.header(
        "Research Findings"
    )

    if findings:

        for index, finding in enumerate(
            findings,
            start=1,
        ):

            show_finding(
                index,
                finding,
            )

    else:

        st.info(
            "No research findings were generated."
        )

    # ========================================================
    # SOURCES
    # ========================================================

    st.header(
        "Sources"
    )

    if sources:

        for source in sources:

            show_source(
                source
            )

    else:

        st.info(
            "No sources were returned."
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    st.header(
        "Final Report"
    )

    if (
        final_answer
        and status == "completed"
        and str(verdict).upper() == "PASS"
    ):

        # ----------------------------------------------------
        # IMPORTANT:
        # final_answer is Markdown.
        # We let Streamlit render it normally.
        # ----------------------------------------------------

        st.markdown(
            final_answer
        )

        st.download_button(
            label="Download Report",
            data=final_answer,
            file_name="research_report.md",
            mime="text/markdown",
        )

    elif str(verdict).upper() == "FAIL":

        st.warning(
            "A final report was not displayed because "
            "the research findings did not pass verification."
        )

        if verification_reason:

            with st.expander(
                "Why did verification fail?"
            ):

                st.code(
                    verification_reason
                )

    elif final_answer:

        st.markdown(
            final_answer
        )

    else:

        st.info(
            "No final report was generated."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ResearchOS · Multi-Agent Research Pipeline · "
    "Search · Analyze · Verify · Retry · Write"
)
