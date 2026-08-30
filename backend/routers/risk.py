import asyncio
from fastapi import APIRouter
from services import asset_service, fortyguard_service, risk_engine, priority_engine
from core.response import success_response

router = APIRouter(prefix="/risk", tags=["risk"])


async def fetch_heat_staggered(assets, delay_seconds: float = 1.0):
    results = []
    for i, asset in enumerate(assets):
        if i > 0:
            await asyncio.sleep(delay_seconds)
        results.append(await fortyguard_service.get_current_heat(asset))
    return results


@router.get("/{asset_id}")
async def get_risk(asset_id: str):
    asset = asset_service.get_asset_by_id(asset_id)
    heat = await fortyguard_service.get_current_heat(asset)
    risk = risk_engine.calculate_risk(asset, heat)
    return success_response(risk.model_dump())


@router.get("")
async def get_all_risk_and_priority():
    assets = asset_service.get_all_assets()

    try:
        heat_readings = await fetch_heat_staggered(assets)
    except Exception as e:
        print(f"RISK FETCH FAILED: {type(e).__name__}: {e}")
        raise

    risks = [
        risk_engine.calculate_risk(asset, heat)
        for asset, heat in zip(assets, heat_readings)
    ]

    priorities = priority_engine.rank_priorities(assets, risks)

    total_weight = sum(a.criticality for a in assets)
    overall_score = round(
        sum(r.score * a.criticality for r, a in zip(risks, assets)) / total_weight, 1
    ) if total_weight else 0.0

    if overall_score >= 85:
        overall_level = "CRITICAL"
    elif overall_score >= 65:
        overall_level = "HIGH"
    elif overall_score >= 40:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"

    return success_response(
        {
            "risks": [r.model_dump() for r in risks],
            "priorities": [p.model_dump() for p in priorities],
            "overall": {"score": overall_score, "level": overall_level},
        }
    )