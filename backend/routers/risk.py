from fastapi import APIRouter
import asyncio
import time

from services import (
    asset_service,
    fortyguard_service,
    risk_engine,
    priority_engine,
)
from core.response import success_response


router = APIRouter(
    prefix="/risk",
    tags=["risk"],
)


@router.get("/{asset_id}")
async def get_risk(asset_id: str):
    asset = asset_service.get_asset_by_id(asset_id)

    start_time = time.perf_counter()

    heat = await fortyguard_service.get_current_heat(asset)

    elapsed = time.perf_counter() - start_time

    print(
        f"[RISK] Single asset heat fetch "
        f"({asset.id}) took {elapsed:.2f}s"
    )

    risk = risk_engine.calculate_risk(
        asset,
        heat,
    )

    return success_response(
        risk.model_dump()
    )


@router.get("")
async def get_all_risk_and_priority():
    assets = asset_service.get_all_assets()

    start_time = time.perf_counter()

    # Fetch heat data for all assets in parallel
    heat_readings = await asyncio.gather(
        *[
            fortyguard_service.get_current_heat(asset)
            for asset in assets
        ]
    )

    heat_fetch_time = (
        time.perf_counter() - start_time
    )

    print(
        f"[RISK] All {len(assets)} FortyGuard heat "
        f"requests completed in {heat_fetch_time:.2f}s"
    )

    risk_start_time = time.perf_counter()

    # Calculate risk for each asset
    risks = [
        risk_engine.calculate_risk(
            asset,
            heat,
        )
        for asset, heat in zip(
            assets,
            heat_readings,
        )
    ]

    risk_calculation_time = (
        time.perf_counter() - risk_start_time
    )

    print(
        f"[RISK] Risk calculation took "
        f"{risk_calculation_time:.4f}s"
    )

    priorities = priority_engine.rank_priorities(
        assets,
        risks,
    )

    # Facility-level overall risk
    total_weight = sum(
        asset.criticality
        for asset in assets
    )

    overall_score = (
        round(
            sum(
                risk.score * asset.criticality
                for risk, asset in zip(
                    risks,
                    assets,
                )
            )
            / total_weight,
            1,
        )
        if total_weight
        else 0.0
    )

    if overall_score >= 85:
        overall_level = "CRITICAL"

    elif overall_score >= 65:
        overall_level = "HIGH"

    elif overall_score >= 40:
        overall_level = "MEDIUM"

    else:
        overall_level = "LOW"

    total_time = (
        time.perf_counter() - start_time
    )

    print(
        f"[RISK] Total /risk endpoint time: "
        f"{total_time:.2f}s"
    )

    return success_response(
        {
            "risks": [
                risk.model_dump()
                for risk in risks
            ],
            "priorities": [
                priority.model_dump()
                for priority in priorities
            ],
            "overall": {
                "score": overall_score,
                "level": overall_level,
            },
        }
    )