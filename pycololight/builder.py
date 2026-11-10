from dataclasses import dataclass

from .constants import (
    CUSTOM_EFFECT_COLOURS,
    HEXAGON_LOWER_PATTERNS,
    HEXAGON_PATTERNS,
    STRIP_LOWER_PATTERNS,
    STRIP_PATTERNS,
)
from .device_type import DeviceType
from .exceptions import CololightValidationError

_PATTERNS = {
    DeviceType.HEXAGON: (HEXAGON_PATTERNS, HEXAGON_LOWER_PATTERNS),
    DeviceType.STRIP: (STRIP_PATTERNS, STRIP_LOWER_PATTERNS),
    DeviceType.MIX: (HEXAGON_PATTERNS, HEXAGON_LOWER_PATTERNS),
}
_PATTERN_2_SPEEDS = {1: 0x03, 2: 0x0B, 3: 0x13}


@dataclass(frozen=True)
class BuilderLimits:
    """
    What the effect builder offers on a device type. Speeds run slowest to fastest,
    except on pattern 2, which runs fastest to slowest.
    """

    colours: dict[str, tuple[str, ...]]
    speeds: dict[int, range]

    @property
    def patterns(self) -> int:
        return len(self.speeds)


def builder_limits(device_type: DeviceType) -> BuilderLimits:
    """
    Lists a device type's colour schemes and their colours, and each pattern's speeds.
    """
    patterns, _ = _PATTERNS[device_type]
    return BuilderLimits(
        colours={
            scheme: tuple(colours) for scheme, colours in CUSTOM_EFFECT_COLOURS.items()
        },
        speeds={
            pattern: range(1, 4) if pattern == 2 else range(1, 34)
            for pattern in range(1, len(patterns) + 1)
        },
    )


@dataclass(frozen=True, kw_only=True)
class CustomEffect:
    """
    An effect made with the effect builder, checked against the device type's
    `builder_limits` when it's built.
    """

    device_type: DeviceType
    colour_scheme: str
    colour: str
    pattern: int
    speed: int

    def __post_init__(self) -> None:
        if self.device_type not in _PATTERNS:
            raise CololightValidationError(
                "device_type", f"Unknown device type {self.device_type!r}"
            )
        limits = builder_limits(self.device_type)
        if self.colour_scheme not in limits.colours:
            raise CololightValidationError(
                "colour_scheme", f"Unknown colour scheme {self.colour_scheme!r}"
            )
        if self.colour not in limits.colours[self.colour_scheme]:
            raise CololightValidationError(
                "colour", f"{self.colour_scheme} has no colour {self.colour!r}"
            )
        if type(self.pattern) is not int or self.pattern not in limits.speeds:
            raise CololightValidationError(
                "pattern", f"Pattern must be 1–{limits.patterns}, not {self.pattern}"
            )
        speeds = limits.speeds[self.pattern]
        if type(self.speed) is not int or self.speed not in speeds:
            raise CololightValidationError(
                "speed",
                f"Speed must be 1–{speeds[-1]} on pattern {self.pattern}, "
                f"not {self.speed}",
            )


def _packet(effect: CustomEffect) -> bytes:
    patterns, lower_patterns = _PATTERNS[effect.device_type]
    mode, suffix = patterns[effect.pattern - 1]
    colour = CUSTOM_EFFECT_COLOURS[effect.colour_scheme][effect.colour]
    if effect.pattern in lower_patterns:
        colour -= 0x80
    if effect.pattern == 2:
        return bytes([mode, _PATTERN_2_SPEEDS[effect.speed], colour, suffix])
    return bytes([mode, colour, 33 - effect.speed, suffix])
