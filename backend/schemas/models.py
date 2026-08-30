from typing import Optional, Literal
from pydantic import BaseModel


# ---------- Assets ----------

class Asset(BaseModel):
    id: str
    name: str
    type: str
    lat: float
    lng: float
    criticality: float  # 0.0 - 1.0
    description: Optional[str] = None


# ---------- Heat ----------

class HeatReading(BaseModel):
    asset_id: str
    temperature_c: float
    exceedance_minutes: Optional[float] = None   # minutes over threshold, if available
    persistence_score: Optional[float] = None    # 0-1, how continuous the heat has been
    source: Literal["fortyguard", "demo"] = "fortyguard"
    timestamp: str
    data_state: Literal["RECENT_OBSERVED", "MODELED", "SIMULATED", "DEMO"] = "RECENT_OBSERVED"


# ---------- Risk ----------

class RiskDrivers(BaseModel):
    hazard: float
    exposure: float
    vulnerability: float
    persistence: float
    response_gap: float


class RiskScore(BaseModel):
    asset_id: str
    score: float                 # 0-100
    level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    drivers: RiskDrivers
    model_version: str = "risk-v1"
    data_state: Literal["RECENT_OBSERVED", "MODELED", "SIMULATED", "DEMO"] = "RECENT_OBSERVED"


# ---------- Priority ----------

class PriorityItem(BaseModel):
    asset_id: str
    asset_name: str
    risk_score: float
    criticality: float
    priority_score: float
    rank: int
    reason: str
    recommended_action: str

# ---------- Scenarios ----------

class ScenarioRequest(BaseModel):
    asset_id: str
    intervention: Literal[
        "shade_structure",
        "reflective_coating",
        "ventilation_fans",
        "vegetation_buffer",
    ]


class ScenarioResult(BaseModel):
    asset_id: str
    intervention: str
    baseline_risk: float
    projected_risk: float
    risk_reduction_pct: float
    notes: str
    data_state: Literal["SIMULATED"] = "SIMULATED"


# ---------- Agent ----------

class AgentQuery(BaseModel):
    question: str
    asset_id: Optional[str] = None  # optional focus asset


class AgentResponse(BaseModel):
    answer: str
    grounded_on: list[str] = []   # which asset_ids / data the answer used


# ---------- Facility ----------

class FacilitySelectRequest(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None