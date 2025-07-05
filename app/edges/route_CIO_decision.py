from app.types import RiskVerdict, SharedState

def route_CIO_decision(state: SharedState) -> SharedState:
    """
    Routes the workflow based on the human approval.
    """
    match state["risk_report"].verdict:
        case RiskVerdict.pass_:
            return "ExecutionNode"
        case RiskVerdict.warn:
            return "HumanNode"
        case RiskVerdict.block:
            return "HumanNode"
            # TODO maybe route back to CIOAgent here? or START?
        case _:
            raise ValueError("Invalid risk verdict")