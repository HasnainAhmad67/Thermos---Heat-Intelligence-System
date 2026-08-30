from pydantic import BaseModel


class FacilityLocation(BaseModel):
    city: str
    state: str
    country: str
    lat: float
    lng: float


class Facility(BaseModel):
    id: str
    name: str
    location: FacilityLocation


DEFAULT_FACILITY = Facility(
    id="dallas-dc-01",
    name="Dallas Distribution Center",
    location=FacilityLocation(
        city="Dallas", state="Texas", country="USA", lat=32.7767, lng=-96.7970
    ),
)

# In-memory only — resets to Dallas on every server restart (by design for MVP).
_current_facility: Facility = DEFAULT_FACILITY


def get_facility() -> Facility:
    return _current_facility


def set_facility(facility: Facility) -> None:
    global _current_facility
    _current_facility = facility


def reset_to_default() -> Facility:
    global _current_facility
    _current_facility = DEFAULT_FACILITY
    return _current_facility