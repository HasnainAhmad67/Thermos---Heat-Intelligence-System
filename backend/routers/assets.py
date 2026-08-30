from fastapi import APIRouter
from services import asset_service
from core.response import success_response

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
async def list_assets():
    assets = asset_service.get_all_assets()
    return success_response([a.model_dump() for a in assets])


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    asset = asset_service.get_asset_by_id(asset_id)
    return success_response(asset.model_dump())