
from enum import Enum
from pydantic import BaseModel, Field, validator 

from typing import Dict, Any, Optional

from typing_extensions import TypedDict

from pydantic import BaseModel, Field, conlist
from typing import Tuple


class ChangeType(str, Enum):
    increase = "increase"
    decrease = "decrease"
    hold = "hold"


class InterestRatePolicyDirection(str, Enum):
    hawkish = "hawkish"
    dovish = "dovish"
    neutral = "neutral"


class InterestRateHikeSize(str, Enum):
    small = "small"
    moderate = "moderate"
    aggressive = "aggressive"
    none = "none"


class InterestRateAnalysis(BaseModel):
    nominal_rate: float = Field(..., description="Midpoint of the target federal funds rate range (in %)")
    new_range: list[float] = Field(..., description="Target range for federal funds rate as [lower, upper]", min_items=2, max_items=2)
    basis_points_change: int = Field(..., description="Change in basis points (1 bp = 0.01%)")
    change_type: ChangeType = Field(..., description="Direction of interest rate change")
    policy_direction: InterestRatePolicyDirection = Field(..., description="Inferred monetary tone of the decision")
    rate_hike_size: InterestRateHikeSize = Field(..., description="Subjective categorization of hike size")
    range_given: bool = Field(..., description="Whether a target range was provided")
    range_width: float = Field(..., description="Width of the range (upper - lower)")

# The Decision Report that is produced by all 3 agents (Analyst, Quant, Exec)

class Report(BaseModel):
    equities: float = Field(..., description="Recommended allocation percentage for equities (0.0 to 1.0)")
    bonds: float = Field(..., description="Recommended allocation percentage for bonds (0.0 to 1.0)")
    justification: str = Field(..., description="Detailed explanation for the recommended allocations")
    
    @validator('equities', 'bonds')
    def check_allocation_range(cls, v):
        if not 0 <= v <= 1:
            raise ValueError(f"Allocation must be between 0 and 1, got {v}")
        return v
    
    @validator('equities', 'bonds')
    def round_to_two_decimals(cls, v):
        return round(v, 2)
    """
    @validator('*', pre=False)
    def validate_sum_to_one(cls, values):
        print(values)
        if 'equities' in values and 'bonds' in values:
            if abs(values['equities'] + values['bonds'] - 1.0) > 1e-6:
                raise ValueError("Equities and bonds must sum to 1.0")
        return values
    """


# ============ HUMAN APPROVAL ===============

class HumanApproval(str, Enum):
    approve = "approve"
    reject = "reject"
    try_again = "try_again"

# ============ RISK REPORT ===============

class RiskVerdict(str, Enum):
    pass_ = "Pass"
    warn = "Warn"
    block = "Block"

class RiskReport(BaseModel):
    verdict: RiskVerdict = Field(..., description="Final risk judgment after assessment")
    reason: str = Field(..., description="Explanation for the verdict, based on internal checks or search evidence")
    external_evidence: Optional[str] = Field(None, description="Any supporting information found via external sources like Google search")


# ============ SHARED STATE ===============

# the shared state for all agents
class SharedState(TypedDict, total=False):

    capital: float
    
    market_data: Dict[str, Any]
    current_month: str # the human friendly version (as per data)
    year: int
    month: int

    prev_equity_allocation: float
    prev_bond_allocation: float
    
    analyst_report: Report
    quant_report: Report
    risk_report: RiskReport
    CIO_report: Report

    new_equity_allocation: float
    new_bond_allocation: float

    human_approval: HumanApproval