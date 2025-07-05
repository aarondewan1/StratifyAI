from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.config import LLM
from app.types import Report
from app.types import SharedState
from langchain_core.messages import HumanMessage

from app.tools import yfinance_api

from app.logger import logger

# Create the Quant Agent
quant_agent = create_react_agent(
    model=LLM,
    tools=[],
    prompt="""You are a Quantitative Analysis Agent, with expertise in economic indicators and their impact on financial markets.

    You have 2 primary roles.
    ONE: When given market data, you should analyze economic data (CPI, unemployment, interest rates) for the given month, and then to recommend 
    equity/bond allocation splits based on quantitative models and historical relationships.
    
    When given market data for a specific month, you should:
     - Analyze the economic indicators using established quantitative models
     - Calculate key metrics like the Misery Index, Phillips Curve pressure, and Taylor Rule rates
     - Consider the previous month's allocation if available
     - Provide a recommendation on equity/bond allocation with detailed quantitative justification
    

    TWO: When asked a question directly by the CIO (chief investment officer) of your firm, you should:
     - Analyze the question
     - Analyse your report (provided with the question)
     - Answer the question in detail, with your quantitative justification

    ENSURE that you switch roles when asked a question by the CIO. Otherwise, your output should be a structured Report with equity and bond allocations (summing to 1.0) and justification.
    """,
    response_format=Report,
)

def get_indicator_summaries(state: SharedState) -> SharedState:
    """
        Uses the yfinance tool (deterministically) to fetch some ticker summaries.
    """

    SP500_summary = yfinance_api.fetch_and_summarise_ticker.invoke({"symbol": "SPY", "year": state["year"], "month": state["month"]})
    IRX_summary = yfinance_api.fetch_and_summarise_ticker.invoke({"symbol": "^IRX", "year": state["year"], "month": state["month"]})

    return SP500_summary, IRX_summary

def quant_agent_node(state: SharedState) -> SharedState:

    logger.info("🤖 QUANT agent | was invoked")

    # some deterministic tool calls
    SP500_summary, IRX_summary = get_indicator_summaries(state)
    misery_index = state['market_data']['economic_indicators']['unemployment_rate'] + state['market_data']['economic_indicators']['cpi_yoy']

    response = quant_agent.invoke(
        {"messages": [HumanMessage(content=f"""

        Here is some information for your analysis:

        {SP500_summary}
        {IRX_summary}

        Here are some pre-computed indicators:
            - CPI YoY: {state['market_data']['economic_indicators']['cpi_yoy']}
            - Unemployment Rate: {state['market_data']['economic_indicators']['unemployment_rate']}
            - Fed Rate Decision: {state['market_data']['economic_indicators']['fed_interest_rate_decision']}
            - Misery index: {misery_index}
    
        The previous month's allocation was {state['prev_equity_allocation']} to equities and {state['prev_bond_allocation']} to bonds.
        """)]} 
    )
    quant_report = response['structured_response']

    logger.info("🤖 QUANT agent | generated report")
    
    logger.info("///////////////////////////////////////////////////")
    logger.info(quant_report)
    logger.info("///////////////////////////////////////////////////")
    
    return {"quant_report": quant_report}


if __name__ == "__main__":
    from app import loader
    
    sample_data = loader.load_month()
    
    test_state = SharedState(
        market_data=sample_data,
        current_month=sample_data.get('month', 'January'),
        prev_equity_allocation=0.6,
        prev_bond_allocation=0.4,
        year=2023,
        month=1
    )
    
    get_indicator_summaries(test_state)
    
    #report = quant_agent_node(test_state)
    #print(report['quant_report'])
