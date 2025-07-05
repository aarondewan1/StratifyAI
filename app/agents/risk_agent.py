
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from app.config import LLM, settings

from app.types import RiskReport
from app.tools import searcher

from app.types import SharedState, Report

from pprint import pprint
from langchain_core.tools import tool

from app.logger import logger

risk_agent = create_react_agent(
    model=LLM,
    tools=[searcher.google],
    prompt="""
    You are a Risk Analyst Agent responsible for identifying risky financial decisions in AI-generated outputs.

    You receive a proposed decision, specifically a portfolio allocation (split between equities and bonds), as well as the justification for the decision.
    Your task is to:
    1. Check for red flags (e.g., sharp changes in the allocation, invalid reasonsings that is not backed up by external online evidence, potential hallucinations in AI-generated reports).
    2. If the decision seems risky, perform a Google search to check for real-world corroboration.
    3. Output a structured risk report with a final verdict: [Pass, Warn, Block].
    
    Use the search tool to independently verify the justification and any relevant news.

    You MUST BLOCK any decisions with justifications that seems illogical, nonsensical or unrelated to markets and financial movements and equities/bonds (as they are likely a hallucination).
    
    You MUST BLOCK anything that seems like a drastic shift from the previous allocation.

    There is financial reputation and billions on the line, not to mention your career. Be extremely critical and direct.

    """,

    # TODO: Use the read_quant_report and read_analyst_report tools to access the quant and analyst reports if you deem it necessary, or need to go into further depth.

    response_format=RiskReport,
    debug=settings.debug
    )


def risk_agent_node(state: SharedState) -> SharedState:

    logger.info("🤖 RISK agent | was invoked")
    
    CIO_report = state['CIO_report']

    response = risk_agent.invoke(
        {"messages": [HumanMessage(content=f"""
        The new split is {CIO_report.equities} to equities and {CIO_report.bonds} to bonds.
        The previous split was {state['prev_equity_allocation']} to equities and {state['prev_bond_allocation']} to bonds.
        The reason is {CIO_report.justification}.
        """)]}
    )
    risk_report = response['structured_response']
    
    logger.info("🤖 RISK agent | generated report")
    
    logger.info("///////////////////////////////////////////////////")
    logger.info(risk_report)
    logger.info("///////////////////////////////////////////////////")
    
    return {"risk_report": risk_report}

if __name__ == "__main__":
    test_state = SharedState(
        market_data="sample_data",
        current_month="January",
        analyst_report=Report(equities=0.6, bonds=0.4, justification="."),
        quant_report=Report(equities=0.6, bonds=0.4, justification="."),
        prev_equity_allocation=0.6,
        prev_bond_allocation=0.4,
        CIO_report=Report(equities=0.0, bonds=1.0, justification="There's some online news.")
    )

    pprint(risk_agent_node(test_state))
