from fastapi import APIRouter
from services import asset_service, fortyguard_service, risk_engine, scenario_engine
from schemas.models import ScenarioRequest
from core.response import success_response

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/simulate")
async def simulate(request: ScenarioRequest):
    asset = asset_service.get_asset_by_id(request.asset_id)
    heat = await fortyguard_service.get_current_heat(asset)
    baseline_risk = risk_engine.calculate_risk(asset, heat)
    result = scenario_engine.simulate_scenario(asset, heat, baseline_risk, request)
    return success_response(result.model_dump())