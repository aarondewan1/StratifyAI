import re
from app.config import LLM
from app.types import InterestRateAnalysis
from langgraph.prebuilt import create_react_agent


def extract_and_analyse(text):
    """
        Combines the rules-based extraction and the LLM analysis.
    """
    result = extract(text)
    result = analyse(result)
    return result

def extract(text):
    """
        Extracts interest rate information from a given text.
        We have a clear structure in the given text, so we are using simple rules.
    """
    result = {
        "nominal_rate": None,
        "new_range": None,
        "basis_points_change": None
    }

    # Extract new range (e.g., "to a range of 4.50% to 4.75%")
    range_match = re.search(r'to a range of ([\d.]+)% to ([\d.]+)%', text)
    if range_match:
        lower = float(range_match.group(1))
        upper = float(range_match.group(2))
        midpoint = (lower + upper) / 2
        result["nominal_rate"] = round(midpoint, 3)
        result["new_range"] = (lower, upper)

    # Extract basis point change (e.g., "raised by 25 basis points")
    bp_match = re.search(r'by (\d+)\s*basis points', text, re.IGNORECASE)
    if bp_match:
        result["basis_points_change"] = int(bp_match.group(1))
    print(result)
    return result

def analyse(text):
    """
        Analyses further interest rate information from the given text.
        Uses an LLM.
    """
    interest_rate_analyst = create_react_agent(
        model=LLM,
        tools=[],
        prompt="""You are an Interest Rate Analyst. Next, you will be given a statement about how interest rates have changed this month, you need to PRECISELY extract the following financial indicators based on the interest rate, EXCLUSIVELY from the statement provided, and using your contextual expertise in financial markets. 
        For exmaple 'The Federal Reserve raised the target for the federal funds rate by 25 basis points to a range of 4.50% to 4.75%'
        should return:
        {
            "nominal_rate": 4.625, // PAY CLOSE ATTENTION HERE
            "new_range": (4.5, 4.75), // PAY CLOSE ATTENTION HERE
            "basis_points_change": 25,
            "change_type": "increase",
            "policy_direction": "hawkish",
            "rate_hike_size": "moderate",
            "range_given": True,
            "range_width": 0.25
        }

        This is the list of fields I want:

        1. Nominal rate (if not already provided)
        2. New range (if not already provided)
        3. Basis points change (if not already provided)
        4. Change type
        5. Policy direction
        6. Rate hike size
        7. Range given
        8. Range width
        """,
        response_format=InterestRateAnalysis,
    )
    return interest_rate_analyst.invoke(text)

if __name__=="__main__":
    # Example usage
    text = "The Federal Reserve raised the target for the federal funds rate by 25 basis points to a range of 3.50% to 3.75%"
    info = extract_and_analyse(text)
    print(info['structured_response'])
