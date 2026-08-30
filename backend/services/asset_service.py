from schemas.models import Asset
from core.exceptions import AssetNotFoundError
from services import facility_service

ZONE_TEMPLATES = [
    {
        "id": "warehouse-01",
        "name": "Warehouse",
        "type": "warehouse",
        "criticality": 0.9,
        "description": "Main storage warehouse for temperature-sensitive goods.",
        "delta_lat": 0.0,
        "delta_lng": 0.0,
    },
    {
        "id": "loading-dock-01",
        "name": "Loading Dock",
        "type": "loading_dock",
        "criticality": 0.75,
        "description": "Primary loading/unloading dock, high foot and vehicle traffic.",
        "delta_lat": 0.0015,
        "delta_lng": 0.0022,
    },
    {
        "id": "outdoor-yard-01",
        "name": "Outdoor Storage Yard",
        "type": "outdoor_yard",
        "criticality": 0.6,
        "description": "Open-air storage yard, fully sun-exposed, no shade cover.",
        "delta_lat": -0.0019,
        "delta_lng": -0.0022,
    },
]


def _generate_assets_for_facility(facility) -> list[Asset]:
    return [
        Asset(
            id=tpl["id"],
            name=tpl["name"],
            type=tpl["type"],
            lat=facility.location.lat + tpl["delta_lat"],
            lng=facility.location.lng + tpl["delta_lng"],
            criticality=tpl["criticality"],
            description=tpl["description"],
        )
        for tpl in ZONE_TEMPLATES
    ]


_assets_cache: list[Asset] | None = None
_cache_facility_id: str | None = None


def get_all_assets() -> list[Asset]:
    global _assets_cache, _cache_facility_id
    facility = facility_service.get_facility()
    if _assets_cache is None or _cache_facility_id != facility.id:
        _assets_cache = _generate_assets_for_facility(facility)
        _cache_facility_id = facility.id
    return _assets_cache


def refresh_assets_for_current_facility() -> list[Asset]:
    global _assets_cache, _cache_facility_id
    facility = facility_service.get_facility()
    _assets_cache = _generate_assets_for_facility(facility)
    _cache_facility_id = facility.id
    return _assets_cache


def get_asset_by_id(asset_id: str) -> Asset:
    for asset in get_all_assets():
        if asset.id == asset_id:
            return asset
    raise AssetNotFoundError(asset_id)