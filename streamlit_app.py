# streamlit_app.py

import streamlit as st
import json
import tempfile
from datetime import date

# We’ll import both your existing monthly runner and the full-run entrypoint:
from app.main import run__monthly_workflow, initial_state, data
from app.main import backtest_simulation, NUM_MONTHS
from app.types import Report
from fpdf import FPDF

st.set_page_config(page_title="StratifyAI Demo", layout="wide")
st.title("📊 StratifyAI: Multi-Agent Portfolio Allocator")

# ---- Sidebar controls ----
st.sidebar.header("Simulation Controls")
mode = st.sidebar.selectbox("Mode", ["Live Allocation", "Historical Backtest"])

# How many months of data do we have?
months_count = NUM_MONTHS

# If you have >1 month, show a slider. Otherwise default to 1.
if months_count > 1:
    months_to_run = st.sidebar.slider(
        "Months to simulate",
        min_value=1,
        max_value=months_count,
        value=1,
        help="Only run the first N months of your historical data",
    )
else:
    months_to_run = 1

# ---- Live Allocation ----
if mode == "Live Allocation":
    st.header("🚀 Live Allocation (Today)")

    if st.button("Run Allocation"):
        # initialize progress bar and state
        progress = st.sidebar.progress(0)
        state = initial_state

        log_lines = []
        reports = {}

        # run month by month, streaming progress
        for idx in range(months_to_run):
            # update progress bar
            progress.progress((idx + 1) / months_to_run)

            # invoke your per-month workflow
            state = run__monthly_workflow(state)

            # capture logs from your logger (assuming you push them into SharedState)
            if "log" in state:
                log_lines.extend(state["log"])

        # once done, extract final reports & logs
        # assuming your SharedState contains a dict of Reports under 'reports'
        reports = state.get("reports", {})
        log_lines = state.get("log", log_lines)

        # display them
        cols = st.columns(len(reports))
        for col, (agent_name, rpt) in zip(cols, reports.items()):
            col.subheader(agent_name)
            col.json(rpt.dict() if isinstance(rpt, Report) else rpt)

        st.markdown(f"## ⚠️ Risk Agent Decision: **{reports['Risk'].decision}**")

        # write out logs
        with open("logs/last_run.log", "w") as f:
            f.write("\n".join(log_lines))

        st.success("✅ Allocation complete!")

# ---- Historical Backtest ----
else:
    st.header("📈 Historical Backtest")
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input(
            "Start Date",
            value=date.today().replace(year=date.today().year - 1),
        )
    with c2:
        end = st.date_input("End Date", value=date.today())

    if st.button("Run Backtest"):
        st.info(f"Backtesting from {start} to {end}…")
        bt_results = backtest_simulation(start, end)
        st.line_chart(bt_results["equity_curve"])
        st.json(bt_results["metrics"])

# ---- Audit Log & PDF Export ----
st.markdown("---")
st.subheader("📝 Audit Log")
if st.checkbox("Show raw logs"):
    try:
        st.code(open("logs/last_run.log").read())
    except FileNotFoundError:
        st.warning("No logs found—run a simulation first!")

st.markdown("---")
st.subheader("📥 Download CIO Report")
if st.button("Export PDF"):
    try:
        cio = reports["CIO"]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, "StratifyAI CIO Report", ln=True, align="C")
        for line in cio.summary.split("\n"):
            pdf.multi_cell(0, 8, line)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        st.download_button(
            "Download CIO Report PDF",
            data=open(tmp.name, "rb").read(),
            file_name="CIO_Report.pdf",
            mime="application/pdf",
        )
    except Exception:
        st.error("Run a live allocation first to generate a CIO report!")




