from typing import Any, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class Envelope(BaseModel):
    success: bool
    data: Optional[Any] = None
    metadata: dict = {}
    error: Optional[ErrorDetail] = None


def success_response(data: Any, metadata: Optional[dict] = None) -> dict:
    return Envelope(
        success=True,
        data=data,
        metadata=metadata or {},
        error=None,
    ).model_dump()


def error_response(code: str, message: str, metadata: Optional[dict] = None) -> dict:
    return Envelope(
        success=False,
        data=None,
        metadata=metadata or {},
        error=ErrorDetail(code=code, message=message),
    ).model_dump()