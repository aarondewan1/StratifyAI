
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from app.config import LLM, settings

from app.types import Report
from app.tools import searcher

from app.types import SharedState, Report

from pprint import pprint
from langchain_core.tools import tool

from app.agents.quant_agent import quant_agent
from app.agents.analyst_agent import analyst_agent

from app.logger import logger

@tool
def question_quant(question: str) -> str:
    """
        Grill the Quantitative Analyst on his report.
    """
    logger.info("🤖 CIO agent | 🔨 question quant tool")
    logger.info(question)
    prompt = f"This is the CIO. I read your report. My question is {question}."
    result = quant_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    answer = result['messages'][-1].content
    logger.info(f"🤖 CIO agent | 🔨 question quant tool | {answer}")
    return answer

@tool
def question_analyst(question: str) -> str:
    """
        Grill the Market Analyst on her report.
    """
    logger.info("🤖 CIO agent | 🔨 question analyst tool")
    logger.info(question)
    prompt = f"This is the CIO. I read your report. My question is {question}."
    result = analyst_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    answer = result['messages'][-1].content
    logger.info(f"🤖 CIO agent | 🔨 question analyst tool | {answer}")
    return answer

CIO_agent = create_react_agent(
    model=LLM,
    tools=[searcher.google, question_quant, question_analyst],
    prompt="""
    You are a CIO (Chief Investment Officer) with years of experience in making portfolio allocation decisions for a multi-billion dollar asset management firm.

    You receive a quant report, and an analyst report.
    
    You need to produce a final decision for portfolio allocation (split between equities and bonds), as well as the justification for the decision.
    
    Refer to the quant and analyst reports when justifying your decision.

    You should ask detailed, pointed follow-up questions to the Quant Agent and the Analyst Agent to grill them to make sure their justifications and assumptions are valid.
    Whenever asking them a question, include their full report after your question.

    After deliberating the reports, and some back-and-forth with the Quant and Analyst Agents, 
    you should make a final decision for portfolio allocation (split between equities and bonds), as well as the justification for the decision.
    
    Your output should be a structured Report with equity and bond allocations (summing to 1.0) and your executive justification. 
    
    IMPORTANT NOTE: Ensure that allocation percentages for equities and bonds sum to 1.0 (100%).

    """,
    response_format=Report,
    debug=settings.debug
    )

def CIO_agent_node(state: SharedState) -> SharedState:

    logger.info("🤖 CIO agent | was invoked")

    response = CIO_agent.invoke(
        {"messages": [HumanMessage(content=f"""
        The Quant's report is:
        {state['quant_report']}
        
        The Analyst's qualitative report is:
        {state['analyst_report']}
        
        The previous month's allocation was {state['prev_equity_allocation']} to equities and {state['prev_bond_allocation']} to bonds.
        """)]} 
    )
    CIO_report = response['structured_response']
    
    logger.info("🤖 CIO agent | generated report")
    
    logger.info("///////////////////////////////////////////////////")
    logger.info(CIO_report)
    logger.info("///////////////////////////////////////////////////")
    
    return {"CIO_report": CIO_report}


if __name__ == "__main__":
    test_state = SharedState(
        market_data="sample_data",
        current_month="January",
        analyst_report=Report(equities=0.9, bonds=0.1, justification="."),
        quant_report=Report(equities=0.9, bonds=0.1, justification="."),
        prev_equity_allocation=0.6,
        prev_bond_allocation=0.4,
        CIO_report=None
    )

    answer = question_quant.invoke("Why do you think that equity should be 0.4? What made you believe that?")
    # TODO get the analyst to pull up the report when it senses it is getting a question.
    pprint(answer)

    #pprint(CIO_agent_node(test_state))
