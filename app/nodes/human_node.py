from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda

from app.types import HumanApproval

from app.logger import logger

def human_node(state):
    logger.info("👱‍♂️ HUMAN APPROVAL | human approval required")
    print("👱‍♂️ HUMAN APPROVAL | human approval required. Enter your choice")
    print("The proposed split is: ")
    print(f"{state['CIO_report'].equities} for equities")
    print(f"{state['CIO_report'].bonds} for bonds")
    print("[ 1 ] Approve")
    print("[ 0 ] Reject")
    print("[ X ] Try again")

    is_valid = False
    while not is_valid:
        human_input = input("Enter your decision: ")
        match human_input:
            case "X":
                human_input = HumanApproval.try_again
            case "1":
                human_input = HumanApproval.approve
            case "0":
                human_input = HumanApproval.reject
            case _:
                print("Invalid input, please try again")
                continue
        is_valid = True
    state["human_approval"] = human_input

    logger.info(f"👱‍♂️ HUMAN APPROVAL | {human_input} was selected")
    return state

human_approval = RunnableLambda(human_node)
