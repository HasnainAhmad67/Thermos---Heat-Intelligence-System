from fastapi import APIRouter
from services import asset_service, fortyguard_service, risk_engine, priority_engine, agent_service, facility_service
from schemas.models import AgentQuery
from core.response import success_response
from routers.risk import fetch_heat_staggered

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask")
async def ask(query: AgentQuery):
    facility = facility_service.get_facility()
    assets = asset_service.get_all_assets()

    heat_readings = await fetch_heat_staggered(assets)
    risks = [
        risk_engine.calculate_risk(asset, heat)
        for asset, heat in zip(assets, heat_readings)
    ]

    priorities = priority_engine.rank_priorities(assets, risks)
    response = agent_service.ask_agent(query, facility, assets, risks, priorities)
    return success_response(response.model_dump())