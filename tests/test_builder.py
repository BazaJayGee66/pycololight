import pytest

from pycololight import (
    Cololight,
    CololightValidationError,
    CustomEffect,
    DeviceType,
    builder_limits,
)

BREATH_ON_PATTERN_1 = {
    "device_type": DeviceType.HEXAGON,
    "colour_scheme": "Breath",
    "colour": "Red, Green, Blue",
    "pattern": 1,
    "speed": 10,
}
HEXAGON_EFFECT_PREFIX = (
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff"
)
STRIP_EFFECT_PREFIX = (
    "535a3030000000000023000000000000000000000000000000000100000000000000000007010602ff"
)
COLOUR_PAIRS = [
    ("Breath", "Red, Green, Blue"),
    ("Breath", "Rainbow"),
    ("Breath", "Green"),
    ("Breath", "Azure"),
    ("Breath", "Blue"),
    ("Breath", "Purple"),
    ("Breath", "Red"),
    ("Breath", "Orange"),
    ("Breath", "Yellow"),
    ("Breath", "White"),
    ("Breath", "Green, Blue"),
    ("Shadow", "Red, Yellow"),
    ("Shadow", "Red, Green"),
    ("Shadow", "Red, Purple"),
    ("Shadow", "Red, Blue"),
    ("Shadow", "Green, Yellow"),
    ("Shadow", "Green, Azure"),
    ("Shadow", "Green, Blue"),
    ("Shadow", "Blue, Azure"),
    ("Shadow", "Blue, Purple"),
    ("Shadow", "Yellow, White"),
    ("Shadow", "Red, White"),
    ("Shadow", "Green, White"),
    ("Shadow", "Azure, White"),
    ("Shadow", "Blue, White"),
    ("Shadow", "Purple, White"),
    ("Flash", "Red, Green, Blue"),
    ("Flash", "Rainbow"),
    ("Flash", "Green"),
    ("Flash", "Azure"),
    ("Flash", "Blue"),
    ("Flash", "Purple"),
    ("Flash", "Red"),
    ("Flash", "Orange"),
    ("Flash", "Yellow"),
    ("Flash", "White"),
    ("Flicker", "Red, Green, Blue"),
    ("Flicker", "Rainbow"),
    ("Flicker", "Green"),
    ("Flicker", "Azure"),
    ("Flicker", "Blue"),
    ("Flicker", "Purple"),
    ("Flicker", "Red"),
    ("Flicker", "Orange"),
    ("Flicker", "Yellow"),
    ("Flicker", "White"),
    ("Scene", "Birthday"),
    ("Scene", "Girlfriends"),
    ("Scene", "Friends"),
    ("Scene", "Workmates"),
    ("Scene", "Family"),
    ("Scene", "Lover"),
    ("Mood", "Red"),
    ("Mood", "Orange"),
    ("Mood", "Yellow"),
    ("Mood", "Green"),
    ("Mood", "Grass"),
    ("Mood", "Azure"),
    ("Mood", "Blue"),
    ("Mood", "Pink"),
    ("Mood", "Gold"),
    ("Mood", "Color"),
    ("Mood", "True Color"),
    ("Selected", "Savasana"),
    ("Selected", "Sunrise"),
    ("Selected", "Unicorns"),
]


async def sent_packet(fake_light, effect):
    client = Cololight("127.0.0.1", effect.device_type, port=fake_light.port)
    await client.set_effect(effect)
    return await fake_light.next_packet()


@pytest.mark.parametrize(
    ("colour_scheme", "colour", "effect_bytes"),
    [
        ("Breath", "Red, Green, Blue", "01801700"),
        ("Breath", "Rainbow", "01811700"),
        ("Breath", "Green", "01821700"),
        ("Breath", "Azure", "01831700"),
        ("Breath", "Blue", "01841700"),
        ("Breath", "Purple", "01851700"),
        ("Breath", "Red", "01861700"),
        ("Breath", "Orange", "01871700"),
        ("Breath", "Yellow", "01881700"),
        ("Breath", "White", "01891700"),
        ("Breath", "Green, Blue", "01c41700"),
        ("Shadow", "Red, Yellow", "018a1700"),
        ("Shadow", "Purple, White", "01981700"),
        ("Flash", "Red, Green, Blue", "01991700"),
        ("Flash", "White", "01a21700"),
        ("Flicker", "Red, Green, Blue", "01a31700"),
        ("Flicker", "White", "01ac1700"),
        ("Scene", "Birthday", "01ad1700"),
        ("Scene", "Lover", "01b21700"),
        ("Mood", "Red", "01b31700"),
        ("Mood", "True Color", "01bd1700"),
        ("Selected", "Savasana", "01bf1700"),
        ("Selected", "Unicorns", "01c31700"),
    ],
)
async def test_a_colour_sends_its_colour_byte(
    fake_light, colour_scheme, colour, effect_bytes
):
    effect = CustomEffect(
        **(BREATH_ON_PATTERN_1 | {"colour_scheme": colour_scheme, "colour": colour})
    )

    packet = await sent_packet(fake_light, effect)

    assert packet == bytes.fromhex(HEXAGON_EFFECT_PREFIX + effect_bytes)


@pytest.mark.parametrize(
    ("pattern", "speed", "effect_bytes"),
    [
        (1, 1, "01802000"),
        (1, 10, "01801700"),
        (1, 33, "01800000"),
        (2, 1, "02038000"),
        (2, 2, "020b8000"),
        (2, 3, "02138000"),
    ],
)
async def test_a_speed_sends_its_speed_byte(fake_light, pattern, speed, effect_bytes):
    effect = CustomEffect(
        **(BREATH_ON_PATTERN_1 | {"pattern": pattern, "speed": speed})
    )

    packet = await sent_packet(fake_light, effect)

    assert packet == bytes.fromhex(HEXAGON_EFFECT_PREFIX + effect_bytes)


@pytest.mark.parametrize(
    ("pattern", "effect_bytes"),
    [
        (1, "01801f00"),
        (2, "020b8000"),
        (3, "05801f10"),
        (4, "05801f30"),
        (5, "05801f40"),
        (6, "05801f50"),
        (7, "05801f70"),
        (8, "05801f80"),
        (9, "05801f90"),
        (10, "05801fa0"),
        (11, "05801fb0"),
        (12, "05801fc0"),
        (13, "05001f00"),
        (14, "05001f20"),
        (15, "05001f30"),
        (16, "06801f00"),
        (17, "06801f10"),
        (18, "06801f20"),
        (19, "06801f30"),
        (20, "06801f50"),
        (21, "05801ff0"),
        (22, "05001f10"),
        (23, "05001f40"),
        (24, "05001f50"),
        (25, "06801f60"),
        (26, "06801f70"),
        (27, "06801f80"),
    ],
)
async def test_a_hexagon_pattern_sends_its_pattern_bytes(
    fake_light, pattern, effect_bytes
):
    effect = CustomEffect(**(BREATH_ON_PATTERN_1 | {"pattern": pattern, "speed": 2}))

    packet = await sent_packet(fake_light, effect)

    assert packet == bytes.fromhex(HEXAGON_EFFECT_PREFIX + effect_bytes)


@pytest.mark.parametrize(
    ("pattern", "effect_bytes"),
    [
        (1, "01801f00"),
        (2, "020b8000"),
        (3, "05801f10"),
        (4, "05801f30"),
        (5, "05801f40"),
        (6, "05801f50"),
        (7, "05801f70"),
        (8, "05801fc0"),
        (9, "05801ff0"),
        (10, "05001f10"),
        (11, "06801f00"),
        (12, "06801f30"),
        (13, "06801f60"),
    ],
)
async def test_a_strip_pattern_sends_its_pattern_bytes_with_the_strip_verb(
    fake_light, pattern, effect_bytes
):
    effect = CustomEffect(
        **(
            BREATH_ON_PATTERN_1
            | {"device_type": DeviceType.STRIP, "pattern": pattern, "speed": 2}
        )
    )

    packet = await sent_packet(fake_light, effect)

    assert packet == bytes.fromhex(STRIP_EFFECT_PREFIX + effect_bytes)


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"device_type": "fake"}, "device_type"),
        ({"device_type": []}, "device_type"),
        ({"colour_scheme": "Rainbow"}, "colour_scheme"),
        ({"colour": "Grass"}, "colour"),
        ({"pattern": 0}, "pattern"),
        ({"pattern": 28}, "pattern"),
        ({"device_type": DeviceType.MIX, "pattern": 28}, "pattern"),
        ({"device_type": DeviceType.STRIP, "pattern": 14}, "pattern"),
        ({"speed": 0}, "speed"),
        ({"speed": 34}, "speed"),
        ({"pattern": 2, "speed": 0}, "speed"),
        ({"pattern": 2, "speed": 4}, "speed"),
        ({"pattern": 1.0}, "pattern"),
        ({"speed": 10.0}, "speed"),
    ],
    ids=[
        "unknown device type",
        "unhashable device type",
        "unknown colour scheme",
        "colour from another scheme",
        "pattern 0",
        "hexagon pattern 28",
        "mix pattern 28",
        "strip pattern 14",
        "speed 0",
        "speed 34",
        "pattern 2 speed 0",
        "pattern 2 speed 4",
        "pattern as a float",
        "speed as a float",
    ],
)
def test_an_invalid_field_raises_a_validation_error(changes, field):
    with pytest.raises(CololightValidationError) as raised:
        CustomEffect(**(BREATH_ON_PATTERN_1 | changes))

    assert raised.value.field == field


def test_fields_are_keyword_only():
    with pytest.raises(TypeError):
        CustomEffect(DeviceType.HEXAGON, "Breath", "Red, Green, Blue", 1, 10)


def test_a_device_type_given_as_a_plain_string_becomes_a_device_type():
    effect = CustomEffect(**(BREATH_ON_PATTERN_1 | {"device_type": "hexagon"}))

    assert effect.device_type is DeviceType.HEXAGON


async def test_a_custom_effect_for_another_device_type_raises_a_validation_error(
    fake_light,
):
    client = Cololight("127.0.0.1", DeviceType.STRIP, port=fake_light.port)

    with pytest.raises(CololightValidationError) as raised:
        await client.set_effect(CustomEffect(**BREATH_ON_PATTERN_1))

    assert raised.value.field == "effect"


@pytest.mark.parametrize("device_type", list(DeviceType))
def test_the_limits_list_each_colour_scheme_and_its_colours_in_order(device_type):
    limits = builder_limits(device_type)

    pairs = [
        (scheme, colour)
        for scheme, colours in limits.colours.items()
        for colour in colours
    ]
    assert pairs == COLOUR_PAIRS


@pytest.mark.parametrize(
    ("device_type", "patterns"),
    [(DeviceType.HEXAGON, 27), (DeviceType.MIX, 27), (DeviceType.STRIP, 13)],
    ids=["hexagon", "mix", "strip"],
)
def test_the_limits_count_the_patterns_and_give_each_its_speeds(device_type, patterns):
    limits = builder_limits(device_type)

    speeds = {pattern: range(1, 34) for pattern in range(1, patterns + 1)}
    speeds[2] = range(1, 4)
    assert limits.patterns == patterns
    assert limits.speeds == speeds
