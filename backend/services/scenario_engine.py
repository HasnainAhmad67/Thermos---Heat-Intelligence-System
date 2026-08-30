from schemas.models import Asset, RiskScore, ScenarioRequest, ScenarioResult
from services.risk_engine import calculate_risk
from schemas.models import HeatReading

# Modeled effect of each intervention on hazard/exposure (MVP simplification —
# clearly labeled SIMULATED, not measured)
INTERVENTION_EFFECTS = {
    "shade_structure": {"hazard_reduction_pct": 15, "exposure_reduction_pct": 25},
    "reflective_coating": {"hazard_reduction_pct": 10, "exposure_reduction_pct": 10},
    "ventilation_fans": {"hazard_reduction_pct": 8, "exposure_reduction_pct": 5},
    "vegetation_buffer": {"hazard_reduction_pct": 12, "exposure_reduction_pct": 20},
}

INTERVENTION_NOTES = {
    "shade_structure": "Reduces direct solar exposure; most effective for outdoor/uncovered assets.",
    "reflective_coating": "Lowers surface heat absorption on roofs/paved areas.",
    "ventilation_fans": "Improves air movement; modest hazard reduction, low cost.",
    "vegetation_buffer": "Adds shade and evapotranspirative cooling over time.",
}


def simulate_scenario(
    asset: Asset, baseline_heat: HeatReading, baseline_risk: RiskScore, request: ScenarioRequest
) -> ScenarioResult:
    effect = INTERVENTION_EFFECTS[request.intervention]

    adjusted_hazard = baseline_risk.drivers.hazard * (1 - effect["hazard_reduction_pct"] / 100)
    adjusted_exposure = baseline_risk.drivers.exposure * (1 - effect["exposure_reduction_pct"] / 100)

    # Recompute overall score with adjusted hazard/exposure, same weights as risk_engine
    from services.risk_engine import WEIGHTS

    projected_score = (
        adjusted_hazard * WEIGHTS["hazard"]
        + adjusted_exposure * WEIGHTS["exposure"]
        + baseline_risk.drivers.vulnerability * WEIGHTS["vulnerability"]
        + baseline_risk.drivers.persistence * WEIGHTS["persistence"]
        + baseline_risk.drivers.response_gap * WEIGHTS["response_gap"]
    )
    projected_score = round(projected_score, 1)

    reduction_pct = round(
        ((baseline_risk.score - projected_score) / baseline_risk.score) * 100, 1
    ) if baseline_risk.score > 0 else 0.0

    return ScenarioResult(
        asset_id=asset.id,
        intervention=request.intervention,
        baseline_risk=baseline_risk.score,
        projected_risk=projected_score,
        risk_reduction_pct=reduction_pct,
        notes=INTERVENTION_NOTES[request.intervention],
    )