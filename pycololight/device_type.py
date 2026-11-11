from enum import StrEnum

from .exceptions import CololightValidationError


class DeviceType(StrEnum):
    HEXAGON = "hexagon"
    STRIP = "strip"
    MIX = "mix"


def _to_device_type(value: str) -> DeviceType:
    try:
        return DeviceType(value)
    except ValueError as err:
        raise CololightValidationError(
            "device_type", f"Unknown device type {value!r}"
        ) from err
