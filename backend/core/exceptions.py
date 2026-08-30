from fastapi import Request
from fastapi.responses import JSONResponse
from core.response import error_response


class FortyGuardUnavailableError(Exception):
    def __init__(self, message: str = "Heat intelligence is temporarily unavailable."):
        self.message = message


class AssetNotFoundError(Exception):
    def __init__(self, asset_id: str):
        self.asset_id = asset_id


async def fortyguard_unavailable_handler(request: Request, exc: FortyGuardUnavailableError):
    return JSONResponse(
        status_code=503,
        content=error_response("FORTYGUARD_UNAVAILABLE", exc.message),
    )


async def asset_not_found_handler(request: Request, exc: AssetNotFoundError):
    return JSONResponse(
        status_code=404,
        content=error_response("ASSET_NOT_FOUND", f"Asset '{exc.asset_id}' not found."),
    )


def register_exception_handlers(app):
    app.add_exception_handler(FortyGuardUnavailableError, fortyguard_unavailable_handler)
    app.add_exception_handler(AssetNotFoundError, asset_not_found_handler)