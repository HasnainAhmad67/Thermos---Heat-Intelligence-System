from fastapi import APIRouter
from services import facility_service, asset_service, fortyguard_service
from services.facility_service import Facility, FacilityLocation
from schemas.models import FacilitySelectRequest
from core.response import success_response

router = APIRouter(prefix="/facility", tags=["facility"])


@router.get("")
async def get_facility():
    facility = facility_service.get_facility()
    return success_response(facility.model_dump())


@router.post("/select")
async def select_facility(request: FacilitySelectRequest):
    try:
        await fortyguard_service.check_coverage(request.lat, request.lng)
    except Exception as e:
        print(f"COVERAGE CHECK FAILED: {type(e).__name__}: {e}")
        raise

    candidate = Facility(
        id=f"custom-{request.lat}-{request.lng}",
        name=request.name or "Selected Facility",
        location=FacilityLocation(
            city=request.city or "Selected Location",
            state=request.state or "",
            country=request.country or "USA",
            lat=request.lat,
            lng=request.lng,
        ),
    )
    facility_service.set_facility(candidate)
    fortyguard_service.clear_cache()
    assets = asset_service.refresh_assets_for_current_facility()

    return success_response({
        "facility": candidate.model_dump(),
        "assets": [a.model_dump() for a in assets],
    })


@router.post("/reset")
async def reset_facility():
    facility = facility_service.reset_to_default()
    fortyguard_service.clear_cache()
    assets = asset_service.refresh_assets_for_current_facility()
    return success_response({
        "facility": facility.model_dump(),
        "assets": [a.model_dump() for a in assets],
    })