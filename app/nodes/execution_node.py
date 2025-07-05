from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pprint import pprint

from app.types import HumanApproval, RiskVerdict

from app.logger import logger


def execution_node(state):
    """
        A mock node that, in production, would actually go ahead and execute the rebalanced portfolio.
    """
    if state['risk_report'].verdict == RiskVerdict.pass_:
        # we implicity give human approval if we passed the RiskVerdict
        state['human_approval'] = HumanApproval.approve
    
    match state['human_approval']:
        case HumanApproval.approve:
            logger.info("++++++++++++++++++++++++++++++++++++++")
            logger.info("✅ EXECUTION | executed action")
            logger.info(f"portfolio was rebalanced to {state['CIO_report'].equities} equities and {state['CIO_report'].bonds} bonds.")
            logger.info("++++++++++++++++++++++++++++++++++++++")
        case HumanApproval.reject:
            logger.info("++++++++++++++++++++++++++++++++++++++")
            logger.info("⛔️ EXECUTION | rejected action")
            logger.info("portfolio was not rebalanced.")
            logger.info("++++++++++++++++++++++++++++++++++++++")
        case HumanApproval.try_again:
            logger.info("++++++++++++++++++++++++++++++++++++++")
            logger.info("🔁 EXECUTION | redo workflow action")
            logger.info("The portfolio was not rebalanced.")
            logger.info("++++++++++++++++++++++++++++++++++++++")
            # TODO retry the workflow > this is not implemented
        case _:
            logger.info("++++++++++++++++++++++++++++++++++++++")
            logger.info("❌ EXECUTION | invalid approval inputted")
            logger.info("++++++++++++++++++++++++++++++++++++++")
            
    return state