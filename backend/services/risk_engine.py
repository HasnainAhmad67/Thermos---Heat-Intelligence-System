from schemas.models import Asset, HeatReading, RiskScore, RiskDrivers

# Weights from the THERMOS PRD (§17) — configurable, not "scientifically validated"
WEIGHTS = {
    "hazard": 0.30,
    "exposure": 0.25,
    "vulnerability": 0.20,
    "persistence": 0.15,
    "response_gap": 0.10,
}

# Simple, explainable thresholds for the MVP
HAZARD_TEMP_FLOOR_C = 30.0   # below this, hazard ~0
HAZARD_TEMP_CEIL_C = 45.0    # at/above this, hazard = 100


def _scale(value: float, low: float, high: float) -> float:
    if value <= low:
        return 0.0
    if value >= high:
        return 100.0
    return ((value - low) / (high - low)) * 100.0


def calculate_risk(asset: Asset, heat: HeatReading) -> RiskScore:
    hazard = _scale(heat.temperature_c, HAZARD_TEMP_FLOOR_C, HAZARD_TEMP_CEIL_C)

    # Exposure: outdoor/uncovered assets score higher (MVP proxy, no full GIS context yet)
    exposure_by_type = {"outdoor_yard": 90.0, "loading_dock": 65.0, "warehouse": 35.0}
    exposure = exposure_by_type.get(asset.type, 50.0)

    # Vulnerability: proxy from asset criticality (0-1 -> 0-100)
    vulnerability = asset.criticality * 100.0

    # Persistence: from FortyGuard if available, else fall back to a modeled midpoint
    persistence = (heat.persistence_score or 0.5) * 100.0

    # Response gap: MVP has no live response/resource data yet, use a fixed modeled value
    response_gap = 50.0

    score = (
        hazard * WEIGHTS["hazard"]
        + exposure * WEIGHTS["exposure"]
        + vulnerability * WEIGHTS["vulnerability"]
        + persistence * WEIGHTS["persistence"]
        + response_gap * WEIGHTS["response_gap"]
    )
    score = round(score, 1)

    if score >= 85:
        level = "CRITICAL"
    elif score >= 65:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskScore(
        asset_id=asset.id,
        score=score,
        level=level,
        drivers=RiskDrivers(
            hazard=round(hazard, 1),
            exposure=round(exposure, 1),
            vulnerability=round(vulnerability, 1),
            persistence=round(persistence, 1),
            response_gap=round(response_gap, 1),
        ),
        data_state="RECENT_OBSERVED" if heat.data_state == "RECENT_OBSERVED" else "MODELED",
    )