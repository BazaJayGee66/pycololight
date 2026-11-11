from dataclasses import dataclass
from typing import NamedTuple

from .device_type import DeviceType
from .exceptions import CololightValidationError


class _Pattern(NamedTuple):
    first_byte: int
    colour_high_bit: int
    suffix: int


_COLOURS: dict[str, dict[str, int]] = {
    "Breath": {
        "Red, Green, Blue": 0x80,
        "Rainbow": 0x81,
        "Green": 0x82,
        "Azure": 0x83,
        "Blue": 0x84,
        "Purple": 0x85,
        "Red": 0x86,
        "Orange": 0x87,
        "Yellow": 0x88,
        "White": 0x89,
        "Green, Blue": 0xC4,
    },
    "Shadow": {
        "Red, Yellow": 0x8A,
        "Red, Green": 0x8B,
        "Red, Purple": 0x8C,
        "Red, Blue": 0x8D,
        "Green, Yellow": 0x8E,
        "Green, Azure": 0x8F,
        "Green, Blue": 0x90,
        "Blue, Azure": 0x91,
        "Blue, Purple": 0x92,
        "Yellow, White": 0x93,
        "Red, White": 0x94,
        "Green, White": 0x95,
        "Azure, White": 0x96,
        "Blue, White": 0x97,
        "Purple, White": 0x98,
    },
    "Flash": {
        "Red, Green, Blue": 0x99,
        "Rainbow": 0x9A,
        "Green": 0x9B,
        "Azure": 0x9C,
        "Blue": 0x9D,
        "Purple": 0x9E,
        "Red": 0x9F,
        "Orange": 0xA0,
        "Yellow": 0xA1,
        "White": 0xA2,
    },
    "Flicker": {
        "Red, Green, Blue": 0xA3,
        "Rainbow": 0xA4,
        "Green": 0xA5,
        "Azure": 0xA6,
        "Blue": 0xA7,
        "Purple": 0xA8,
        "Red": 0xA9,
        "Orange": 0xAA,
        "Yellow": 0xAB,
        "White": 0xAC,
    },
    "Scene": {
        "Birthday": 0xAD,
        "Girlfriends": 0xAE,
        "Friends": 0xAF,
        "Workmates": 0xB0,
        "Family": 0xB1,
        "Lover": 0xB2,
    },
    "Mood": {
        "Red": 0xB3,
        "Orange": 0xB4,
        "Yellow": 0xB5,
        "Green": 0xB6,
        "Grass": 0xB7,
        "Azure": 0xB8,
        "Blue": 0xB9,
        "Pink": 0xBA,
        "Gold": 0xBB,
        "Color": 0xBC,
        "True Color": 0xBD,
    },
    "Selected": {
        "Savasana": 0xBF,
        "Sunrise": 0xC1,
        "Unicorns": 0xC3,
    },
}

_HEXAGON_PATTERNS = (
    _Pattern(0x01, 0x80, 0x00),
    _Pattern(0x02, 0x80, 0x00),
    _Pattern(0x05, 0x80, 0x10),
    _Pattern(0x05, 0x80, 0x30),
    _Pattern(0x05, 0x80, 0x40),
    _Pattern(0x05, 0x80, 0x50),
    _Pattern(0x05, 0x80, 0x70),
    _Pattern(0x05, 0x80, 0x80),
    _Pattern(0x05, 0x80, 0x90),
    _Pattern(0x05, 0x80, 0xA0),
    _Pattern(0x05, 0x80, 0xB0),
    _Pattern(0x05, 0x80, 0xC0),
    _Pattern(0x05, 0x00, 0x00),
    _Pattern(0x05, 0x00, 0x20),
    _Pattern(0x05, 0x00, 0x30),
    _Pattern(0x06, 0x80, 0x00),
    _Pattern(0x06, 0x80, 0x10),
    _Pattern(0x06, 0x80, 0x20),
    _Pattern(0x06, 0x80, 0x30),
    _Pattern(0x06, 0x80, 0x50),
    _Pattern(0x05, 0x80, 0xF0),
    _Pattern(0x05, 0x00, 0x10),
    _Pattern(0x05, 0x00, 0x40),
    _Pattern(0x05, 0x00, 0x50),
    _Pattern(0x06, 0x80, 0x60),
    _Pattern(0x06, 0x80, 0x70),
    _Pattern(0x06, 0x80, 0x80),
)

_STRIP_PATTERNS = (
    _Pattern(0x01, 0x80, 0x00),
    _Pattern(0x02, 0x80, 0x00),
    _Pattern(0x05, 0x80, 0x10),
    _Pattern(0x05, 0x80, 0x30),
    _Pattern(0x05, 0x80, 0x40),
    _Pattern(0x05, 0x80, 0x50),
    _Pattern(0x05, 0x80, 0x70),
    _Pattern(0x05, 0x80, 0xC0),
    _Pattern(0x05, 0x80, 0xF0),
    _Pattern(0x05, 0x00, 0x10),
    _Pattern(0x06, 0x80, 0x00),
    _Pattern(0x06, 0x80, 0x30),
    _Pattern(0x06, 0x80, 0x60),
)

_PATTERNS = {
    DeviceType.HEXAGON: _HEXAGON_PATTERNS,
    DeviceType.STRIP: _STRIP_PATTERNS,
    DeviceType.MIX: _HEXAGON_PATTERNS,
}
_SPEED_BYTES = {speed: 33 - speed for speed in range(1, 34)}
_PATTERN_2_SPEED_BYTES = {1: 0x03, 2: 0x0B, 3: 0x13}


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
    return BuilderLimits(
        colours={scheme: tuple(colours) for scheme, colours in _COLOURS.items()},
        speeds={
            pattern: range(1, len(_speed_bytes(pattern)) + 1)
            for pattern in range(1, len(_PATTERNS[device_type]) + 1)
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
        try:
            object.__setattr__(self, "device_type", DeviceType(self.device_type))
        except ValueError as err:
            raise CololightValidationError(
                "device_type", f"Unknown device type {self.device_type!r}"
            ) from err
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


def _speed_bytes(pattern: int) -> dict[int, int]:
    return _PATTERN_2_SPEED_BYTES if pattern == 2 else _SPEED_BYTES


def _packet(effect: CustomEffect) -> bytes:
    patterns = _PATTERNS[effect.device_type]
    first_byte, colour_high_bit, suffix = patterns[effect.pattern - 1]
    colour_byte = _COLOURS[effect.colour_scheme][effect.colour]
    colour = (colour_byte & 0x7F) | colour_high_bit
    speed = _speed_bytes(effect.pattern)[effect.speed]
    if effect.pattern == 2:
        return bytes([first_byte, speed, colour, suffix])
    return bytes([first_byte, colour, speed, suffix])
