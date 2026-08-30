from fastapi import APIRouter
from services import asset_service, fortyguard_service, risk_engine, priority_engine, agent_service
from schemas.models import AgentQuery
from core.response import success_response

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask")
async def ask(query: AgentQuery):
    assets = asset_service.get_all_assets()
    risks = []
    for asset in assets:
        heat = await fortyguard_service.get_current_heat(asset)
        risks.append(risk_engine.calculate_risk(asset, heat))

    priorities = priority_engine.rank_priorities(assets, risks)
    response = agent_service.ask_agent(query, assets, risks, priorities)
    return success_response(response.model_dump())