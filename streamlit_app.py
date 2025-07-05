# streamlit_app.py
import streamlit as st
import json
import tempfile
from datetime import date
from app.main import run_simulation, backtest_simulation  # your existing entrypoints
from app.types import Report
from fpdf import FPDF

st.set_page_config(page_title="StratifyAI Demo", layout="wide")

st.title("📊 StratifyAI: Multi-Agent Portfolio Allocator")

# ---- Sidebar params ----
st.sidebar.header("Simulation Controls")
mode = st.sidebar.selectbox("Mode", ["Live Allocation", "Historical Backtest"])

# ---- Live Allocation ----
if mode == "Live Allocation":
    st.header("🚀 Live Allocation (Today)")
    if st.button("Run Allocation"):
        with st.spinner("Running multi-agent workflow…"):
            # your `run_simulation()` should return e.g. a dict of Reports and logs
            result = run_simulation()  
        reports, log_lines = result["reports"], result["log"]
        # Display each agent’s report in columns
        cols = st.columns(len(reports))
        for col, (agent_name, rpt) in zip(cols, reports.items()):
            col.subheader(agent_name)
            # Assuming Report has an `.dict()` or JSONable representation
            col.json(rpt.dict() if isinstance(rpt, Report) else rpt)
        # Show risk decision prominently
        st.markdown(f"## ⚠️ Risk Agent Decision: **{reports['Risk'].decision}**")
        # Save last run log to disk
        with open("logs/last_run.log", "w") as f:
            f.write("\n".join(log_lines))
        st.success("Allocation complete!")

# ---- Historical Backtest ----
else:
    st.header("📈 Historical Backtest")
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start Date", value=date.today().replace(year=date.today().year-1))
    with c2:
        end   = st.date_input("End Date",   value=date.today())
    if st.button("Run Backtest"):
        st.info(f"Backtesting from {start} to {end}…")
        # stub: hook to your backtest API
        bt_results = backtest_simulation(start, end)  
        # Example: bt_results = {"equity_curve": [...], "metrics": {...}}
        st.line_chart(bt_results["equity_curve"])
        st.json(bt_results["metrics"])

# ---- Audit Log & Export ----
st.markdown("---")
st.subheader("📝 Audit Log")
if st.checkbox("Show raw logs"):
    try:
        st.code(open("logs/last_run.log").read())
    except FileNotFoundError:
        st.warning("No logs found—run a simulation first!")

# PDF export of CIO report
st.markdown("---")
st.subheader("📥 Download CIO Report")
if st.button("Export PDF"):
    # Grab the CIO report from last run
    try:
        cio = reports["CIO"]  # your Report object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, "StratifyAI CIO Report", ln=True, align="C")
        for line in cio.summary.split("\n"):
            pdf.multi_cell(0, 8, line)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        st.download_button("Download CIO Report PDF", data=open(tmp.name, "rb").read(),
                           file_name="CIO_Report.pdf", mime="application/pdf")
    except Exception:
        st.error("Run a live allocation first to generate a CIO report!")

