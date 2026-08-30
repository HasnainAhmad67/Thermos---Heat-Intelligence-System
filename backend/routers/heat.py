from fastapi import APIRouter, Query
from services import asset_service, fortyguard_service ,facility_service
from core.response import success_response

router = APIRouter(prefix="/heat", tags=["heat"])


@router.get("/current/{asset_id}")
async def current_heat(asset_id: str):
    asset = asset_service.get_asset_by_id(asset_id)
    reading = await fortyguard_service.get_current_heat(asset)
    return success_response(reading.model_dump(), metadata={"source": "fortyguard"})


@router.get("/forecast/{asset_id}")
async def forecast_heat(asset_id: str, hours_ahead: int = Query(6, ge=1, le=12)):
    asset = asset_service.get_asset_by_id(asset_id)
    reading = await fortyguard_service.get_forecast_heat(asset, hours_ahead)
    return success_response(reading.model_dump(), metadata={"source": "fortyguard"})

@router.get("/facility-map")
async def facility_map():
    facility = facility_service.get_facility()
    geojson = await fortyguard_service.get_facility_heatmap(
        facility.location.lat, facility.location.lng
    )
    return success_response(geojson)