import time
import asyncio
from datetime import datetime, timezone, timedelta

import httpx

from config import settings
from schemas.models import Asset, HeatReading
from core.exceptions import FortyGuardUnavailableError


_cache: dict[str, tuple[float, HeatReading]] = {}
_CACHE_TTL_SECONDS = 300

_heatmap_cache: dict[str, tuple[float, dict]] = {}
_HEATMAP_CACHE_TTL_SECONDS = 600

BASE_URL = "https://api.fortyguard.com/v1"


def _cache_key(asset_id: str, mode: str) -> str:
    return f"{asset_id}:{mode}"


def _get_cached(key: str) -> HeatReading | None:
    entry = _cache.get(key)

    if not entry:
        return None

    ts, reading = entry

    if time.time() - ts > _CACHE_TTL_SECONDS:
        return None

    return reading


def _headers() -> dict:
    if not settings.fortyguard_api_key:
        raise FortyGuardUnavailableError(
            "FortyGuard API key not configured."
        )

    return {
        "api-key": settings.fortyguard_api_key.strip(),
        "Content-Type": "application/json",
    }


def _small_polygon_around(
    lat: float,
    lng: float,
    delta: float = 0.002,
) -> dict:
    """Builds a tiny GeoJSON polygon around a point."""

    return {
        "type": "Polygon",
        "coordinates": [
            [
                [lng - delta, lat - delta],
                [lng + delta, lat - delta],
                [lng + delta, lat + delta],
                [lng - delta, lat + delta],
                [lng - delta, lat - delta],
            ]
        ],
    }


async def _submit_heatmap(
    lat: float,
    lng: float,
    start_date: str,
    start_time: str,
    delta: float = 0.002,
) -> str:
    """Submits a heatmap request and returns the activity_id."""

    payload = {
        "polygon_aoi": _small_polygon_around(
            lat,
            lng,
            delta,
        ),
        "date_time": {
            "start_date": start_date,
            "start_time": start_time,
            "filter_type": 1,
        },
        "granularity": 100,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{BASE_URL}/heatmap",
                headers=_headers(),
                json=payload,
            )

            resp.raise_for_status()
            data = resp.json()

    except httpx.TimeoutException as exc:
        raise FortyGuardUnavailableError(
            f"FortyGuard heatmap submission timed out: {exc}"
        ) from exc

    except httpx.HTTPError as exc:
        raise FortyGuardUnavailableError(
            f"FortyGuard heatmap submission failed: {exc}"
        ) from exc

    activity_id = data.get("data", {}).get("activity_id")

    if not activity_id:
        raise FortyGuardUnavailableError(
            "FortyGuard did not return an activity_id."
        )

    return activity_id


async def _poll_status(
    activity_id: str,
    max_attempts: int = 20,
    delay_seconds: float = 1.5,
) -> dict:
    """
    Polls /status/{activity_id} until completed,
    failed, or timeout.
    """

    url = f"{BASE_URL}/status/{activity_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:

        for _ in range(max_attempts):

            try:
                resp = await client.get(
                    url,
                    headers=_headers(),
                )

                resp.raise_for_status()
                payload = resp.json()

            except httpx.TimeoutException as exc:
                raise FortyGuardUnavailableError(
                    f"FortyGuard status check timed out: {exc}"
                ) from exc

            except httpx.HTTPError as exc:
                raise FortyGuardUnavailableError(
                    f"FortyGuard status check failed: {exc}"
                ) from exc

            status_data = payload.get("data", {})

            status = str(
                status_data.get("status", "")
            ).lower()

            if status in ("completed", "succeeded"):
                return status_data.get("result", {})

            if status in ("failed", "error"):
                raise FortyGuardUnavailableError(
                    f"FortyGuard task failed: {status_data}"
                )

            await asyncio.sleep(delay_seconds)

    raise FortyGuardUnavailableError(
        "FortyGuard task timed out while waiting for completion."
    )


def has_coverage(result: dict) -> bool:
    """
    Returns True if FortyGuard returned actual
    thermal data for this AOI/date.
    """

    features = (
        result.get("map_data", {})
        .get("features", [])
    )

    n_cells = (
        result.get("stats_data", {})
        .get("n_cells")
    )

    if n_cells == 0:
        return False

    return bool(features)


def _extract_temperature(result: dict) -> float:
    """Extracts an average temperature from FortyGuard result."""

    if not has_coverage(result):
        raise FortyGuardUnavailableError(
            "No thermal data available for this location/date. "
            "It may be outside FortyGuard's coverage."
        )

    features = (
        result.get("map_data", {})
        .get("features", [])
    )

    temps = [
        feature["properties"]["average_temperature"]
        for feature in features
        if "average_temperature"
        in feature.get("properties", {})
    ]

    if temps:
        return round(
            sum(temps) / len(temps),
            2,
        )

    stats = (
        result.get("stats_data", {})
        .get("temperature_stats", {})
    )

    if stats.get("mean") is not None:
        return round(
            stats["mean"],
            2,
        )

    raise FortyGuardUnavailableError(
        "FortyGuard returned coverage but no usable temperature value."
    )


async def get_current_heat(
    asset: Asset,
) -> HeatReading:
    """Gets the latest available heat reading for an asset."""

    key = _cache_key(
        asset.id,
        "current",
    )

    cached = _get_cached(key)

    if cached:
        return cached

    # FortyGuard processes only past dates.
    # Use yesterday as the most recent available date.
    reference_time = (
        datetime.now(timezone.utc)
        - timedelta(days=1)
    )

    activity_id = await _submit_heatmap(
        asset.lat,
        asset.lng,
        start_date=reference_time.strftime("%Y-%m-%d"),
        start_time="14:00",
    )

    result = await _poll_status(
        activity_id,
    )

    temperature = _extract_temperature(
        result,
    )

    reading = HeatReading(
        asset_id=asset.id,
        temperature_c=temperature,
        exceedance_minutes=None,
        persistence_score=None,
        source="fortyguard",
        timestamp=reference_time.isoformat(),
        data_state="RECENT_OBSERVED",
    )

    _cache[key] = (
        time.time(),
        reading,
    )

    return reading


async def get_forecast_heat(
    asset: Asset,
    hours_ahead: int = 6,
) -> HeatReading:
    """Gets a modeled heat reading for an asset."""

    key = _cache_key(
        asset.id,
        f"forecast:{hours_ahead}",
    )

    cached = _get_cached(key)

    if cached:
        return cached

    # Using yesterday's data as a modeled reference.
    reference_time = (
        datetime.now(timezone.utc)
        - timedelta(days=1)
    )

    forecast_hour = min(
        23,
        14 + (hours_ahead // 2),
    )

    activity_id = await _submit_heatmap(
        asset.lat,
        asset.lng,
        start_date=reference_time.strftime("%Y-%m-%d"),
        start_time=f"{forecast_hour:02d}:00",
    )

    result = await _poll_status(
        activity_id,
    )

    temperature = _extract_temperature(
        result,
    )

    reading = HeatReading(
        asset_id=asset.id,
        temperature_c=temperature,
        exceedance_minutes=None,
        persistence_score=None,
        source="fortyguard",
        timestamp=reference_time.isoformat(),
        data_state="MODELED",
    )

    _cache[key] = (
        time.time(),
        reading,
    )

    return reading


def clear_cache() -> None:
    """
    Wipes cached heat readings whenever
    the facility changes.
    """

    _cache.clear()
    _heatmap_cache.clear()


async def check_coverage(
    lat: float,
    lng: float,
) -> bool:
    """
    Raises FortyGuardUnavailableError if this location
    has no FortyGuard coverage.
    """

    reference_time = (
        datetime.now(timezone.utc)
        - timedelta(days=1)
    )

    activity_id = await _submit_heatmap(
        lat,
        lng,
        reference_time.strftime("%Y-%m-%d"),
        "14:00",
    )

    result = await _poll_status(
        activity_id,
    )

    if not has_coverage(result):
        raise FortyGuardUnavailableError(
            "This location appears to be outside "
            "FortyGuard's supported coverage area. "
            "Please select a location within the United States."
        )

    return True


async def get_facility_heatmap(
    lat: float,
    lng: float,
    delta: float = 0.008,
) -> dict:
    """
    Returns a FeatureCollection-style GeoJSON
    covering the whole facility area.
    """

    key = (
        f"{round(lat, 4)}:"
        f"{round(lng, 4)}:"
        f"{delta}"
    )

    cached_entry = _heatmap_cache.get(key)

    if cached_entry:
        ts, data = cached_entry

        if (
            time.time() - ts
            < _HEATMAP_CACHE_TTL_SECONDS
        ):
            return data

    reference_time = (
        datetime.now(timezone.utc)
        - timedelta(days=1)
    )

    activity_id = await _submit_heatmap(
        lat,
        lng,
        start_date=reference_time.strftime("%Y-%m-%d"),
        start_time="14:00",
        delta=delta,
    )

    result = await _poll_status(
        activity_id,
    )

    if not has_coverage(result):
        raise FortyGuardUnavailableError(
            "No heatmap coverage available for this facility area."
        )

    features = (
        result.get("map_data", {})
        .get("features", [])
    )

    temps = [
        feature["properties"]["average_temperature"]
        for feature in features
        if "average_temperature"
        in feature.get("properties", {})
    ]

    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "temperature_range": {
            "min": min(temps) if temps else None,
            "max": max(temps) if temps else None,
        },
        "reference_time": reference_time.isoformat(),
    }

    _heatmap_cache[key] = (
        time.time(),
        geojson,
    )

    return geojson