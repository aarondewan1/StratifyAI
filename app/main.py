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

data = loader.load_data()

builder = StateGraph(SharedState)

builder.add_node("AnalystAgent", analyst_agent_node)
builder.add_node("QuantAgent", quant_agent_node)
builder.add_node("CIOAgent", CIO_agent_node)
builder.add_node("RiskAgent", risk_agent_node)
builder.add_node("HumanNode", human_node)
builder.add_node("ExecutionNode", execution_node)

# Analyst and Quant are both entry points
builder.add_edge(START, "AnalystAgent")
builder.add_edge(START, "QuantAgent")

builder.add_edge("AnalystAgent", "CIOAgent")
builder.add_edge("QuantAgent", "CIOAgent")

builder.add_edge("CIOAgent", "RiskAgent")

builder.add_conditional_edges("RiskAgent", route_CIO_decision)

builder.add_edge("HumanNode", "ExecutionNode")

builder.add_edge("ExecutionNode", END)

graph = builder.compile()


# ========== SETUP INITIAL STATE ==========

initial_year, initial_month = convert_date(data['market_data'][0]['month'])

initial_capital = 1000

initial_state = SharedState(
    capital=initial_capital,
    market_data=data['market_data'][0],
    current_month=data['market_data'][0]['month'],
    prev_equity_allocation=0.6,
    prev_bond_allocation=0.4,
    analyst_report=None,
    quant_report=None,
    CIO_report=None,
    human_decision=None,
    year=initial_year,
    month=initial_month
)

def run__monthly_workflow(state):
    output = graph.invoke(state)
    return output


def run_simulation():
    NUM_MONTHS = len(data['market_data'])

    state = initial_state

    for month_idx in range(NUM_MONTHS):

        logger.info("======================================= " + data['market_data'][month_idx]['month'] + " =======================================")
        
        logger.info("----------------------------------------------------------------------")
        logger.info("💿 STATE")
        logger.info(state)
        logger.info("----------------------------------------------------------------------")

        logger.info("⌛️ WORKFLOW | running monthly workflow")

        state = run__monthly_workflow(state)

        logger.info("✅✅✅ WORKFLOW | ran monthly workflow")

        logger.info("----------------------------------------------------------------------")
        logger.info("💿 STATE")
        logger.info(state)
        logger.info("----------------------------------------------------------------------")

        # make updates to the state as per the previous run
        if month_idx + 1 < NUM_MONTHS:

            # update the state for the next month's data

            state["market_data"] = data['market_data'][month_idx + 1]
            state["current_month"] = data['market_data'][month_idx + 1]['month']
            state["prev_equity_allocation"] = state["CIO_report"].equities
            state["prev_bond_allocation"] = state["CIO_report"].bonds

            # reset all reports, new allocations and the human approval flag
            state['analyst_report'] = None
            state['quant_report'] = None
            state['risk_report'] = None
            state['CIO_report'] = None

            state['new_equity_allocation'] = None
            state['new_bond_allocation'] = None

            state["human_approval"] = None
        
    logger.info("✅✅✅ SIMULATION | COMPLETED SIMULATION. TERMINATING")


if __name__ == "__main__":
    run_simulation()

def backtest_simulation(start_date, end_date):
    """
    Stub for historical backtest. Replace with real logic.
    """
    equity_curve = []
    metrics = {}
    return {"equity_curve": equity_curve, "metrics": metrics}
