from typing import Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.output_parsers import PydanticOutputParser

from app.config import LLM, settings
from app.types import Report, SharedState

from langchain_core.messages import HumanMessage

from app.tools.yfinance_api import fetch_and_summarise_ticker
from app.tools.searcher import google

from app.config import settings

from app.logger import logger

analyst_agent = create_react_agent(
    model=LLM,
    tools=[fetch_and_summarise_ticker, google],
    prompt="""
    You are a Senior Market Analyst Agent, with expertise in qualitative analysis of the markets.

    You have 2 primary roles.
    ONE: When given market data, you should analyze Market News, Headlines, and Sentiment for the given month, and then recommend equity/bond allocation splits for optimal yields.

    When given market data for a specific month, you should:
    - Analyze the news summary and headlines to gauge market sentiment
    - Identify some related ticker values based on the news. Focus on ticker values for private equity etc. companies, rather than macro-economic or bond indicators.
    (NOTE: ^IRX and SPY are already analyzed by your colleague, the Quant Agent)
    - Verify these ticker symbols are correct by searching online with the google search tool.
    - Use the fetch_and_summarise_ticker tool to get the summaries of the related tickers.
    IMPORTANT: You MUST do this for any companies that are called out directly in the news headlines or summaries.
    - Consider how the news might impact investor confidence and market direction
    - Consider the previous month's allocation if available
    - Provide a report on equity/bond allocation with detailed justification

    TWO: When asked a question directly by the CIO (chief investment officer) of your firm, you should:
    - Analyse the question
    - Analyse your report (provided with the question)
    - Answer the question in detail, with your qualitative justification

    ENSURE that you switch roles when asked a question by the CIO. Otherwise, your output should be a structured Report with equity and bond allocations (summing to 1.0) and justification.
    """,
    response_format=Report,
    debug=settings.debug,
)


def analyst_agent_node(state: SharedState) -> SharedState:
    
    logger.info("🤖 ANALYST agent | was invoked")

    
    market_month_data = state["market_data"]

    # Extract news data
    news = market_month_data.get("news", {})
    summary = news.get("summary", "")
    headlines = news.get("headlines", [])
    headlines_text = "\n".join([f"- {headline}" for headline in headlines])    

    response = analyst_agent.invoke(
    {"messages": [HumanMessage(content=f"""
    Month: {state.get('current_month', market_month_data.get('month', 'the current month'))}
    
    Market Summary: {summary}
    
    News Headlines:
    {headlines_text}
    
    Previous Allocation:
    - Equities: {state.get('prev_equity_allocation', 'N/A')}
    - Bonds: {state.get('prev_bond_allocation', 'N/A')}
        
    IMPORTANT NOTE: Ensure that allocation percentages for equities and bonds sum to 1.0 (100%).

    Provide a detailed justification for your recommendation based on the news sentiment and market outlook.
    """)]}
    )
    
    analyst_report = response['structured_response']
    
    logger.info("🤖 ANALYST agent | generated report")

    logger.info("///////////////////////////////////////////////////")
    logger.info(analyst_report)
    logger.info("///////////////////////////////////////////////////")
    
    return {"analyst_report": analyst_report}
    

if __name__ == "__main__":
    # testing with a sample month
    from app import loader
    
    sample_data = loader.load_month()
    
    test_state = SharedState(
        market_data=sample_data,
        current_month=sample_data.get('month', 'January'),
        prev_equity_allocation=0.6,
        prev_bond_allocation=0.4
    )
    
    analyst_report = analyst_agent_node(test_state)
    print(analyst_report)
