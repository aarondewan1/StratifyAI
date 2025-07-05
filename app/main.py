# app/main.py

from app import loader
from langgraph.graph import StateGraph, START, END
from app.types import SharedState

from app.agents.analyst_agent import analyst_agent_node
from app.agents.quant_agent import quant_agent_node
from app.agents.CIO_agent import CIO_agent_node
from app.agents.risk_agent import risk_agent_node
from app.nodes.human_node import human_node
from app.nodes.execution_node import execution_node

from app.edges.route_CIO_decision import route_CIO_decision

from app.utils import convert_date

from app.logger import logger

# Load your entire dataset once
data = loader.load_data()
NUM_MONTHS = len(data["market_data"])

# Build the multi-agent graph
builder = StateGraph(SharedState)
builder.add_node("AnalystAgent", analyst_agent_node)
builder.add_node("QuantAgent", quant_agent_node)
builder.add_node("CIOAgent", CIO_agent_node)
builder.add_node("RiskAgent", risk_agent_node)
builder.add_node("HumanNode", human_node)
builder.add_node("ExecutionNode", execution_node)
builder.add_edge(START, "AnalystAgent")
builder.add_edge(START, "QuantAgent")
builder.add_edge("AnalystAgent", "CIOAgent")
builder.add_edge("QuantAgent", "CIOAgent")
builder.add_edge("CIOAgent", "RiskAgent")
builder.add_conditional_edges("RiskAgent", route_CIO_decision)
builder.add_edge("HumanNode", "ExecutionNode")
builder.add_edge("ExecutionNode", END)
graph = builder.compile()

# ========== INITIAL STATE SETUP ==========
initial_year, initial_month = convert_date(data["market_data"][0]["month"])
initial_state = SharedState(
    capital=1000,
    market_data=data["market_data"][0],
    current_month=data["market_data"][0]["month"],
    prev_equity_allocation=0.6,
    prev_bond_allocation=0.4,
    analyst_report=None,
    quant_report=None,
    CIO_report=None,
    human_decision=None,
    year=initial_year,
    month=initial_month,
)

def run__monthly_workflow(state: SharedState) -> SharedState:
    return graph.invoke(state)

def run_simulation(months_to_run: int = None):
    """
    Run up to `months_to_run` months of your market_data (from the start).
    If months_to_run is None or exceeds available data, will run all.
    """
    # Decide how many months to process
    if months_to_run is None or months_to_run > NUM_MONTHS:
        months_to_run = NUM_MONTHS

    # Start from a fresh copy of the initial state
    state = initial_state

    for month_idx in range(months_to_run):
        month_label = data["market_data"][month_idx]["month"]
        logger.info(f"====== {month_label} ======")
        logger.info("💿 STATE BEFORE")
        logger.info(state)
        logger.info("⌛️ WORKFLOW | running monthly workflow")

        # invoke the graph for this month
        state = run__monthly_workflow(state)

        logger.info("✅✅✅ WORKFLOW COMPLETE")
        logger.info("💿 STATE AFTER")
        logger.info(state)

        # prepare for next month (if any)
        if month_idx + 1 < months_to_run:
            next_data = data["market_data"][month_idx + 1]
            state["market_data"]         = next_data
            state["current_month"]       = next_data["month"]
            state["prev_equity_allocation"] = state["CIO_report"].equities
            state["prev_bond_allocation"]   = state["CIO_report"].bonds

            # clear out last reports & flags
            for key in ["analyst_report", "quant_report", "risk_report", "CIO_report", "human_approval"]:
                state[key] = None

    logger.info("✅✅✅ SIMULATION | completed")
    # return the final state or any summary as needed
    return {"final_state": state}

def backtest_simulation(start_date, end_date):
    """
    Stub for historical backtest. Replace with real logic or loop over run_simulation.
    """
    equity_curve = []
    metrics = {}
    return {"equity_curve": equity_curve, "metrics": metrics}

if __name__ == "__main__":
    # Example: run only 1 month by default
    run_simulation(months_to_run=1)

