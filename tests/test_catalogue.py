import pytest

from pycololight import Cololight, CololightValidationError, DeviceType

HEXAGON_LIFESMART_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff04970400"
)
MIX_RHYTHM_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff0a000000"
)
STRIP_LIFESMART_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000007010602ff04970400"
)
RED_METEOR_PACKETS = [
    bytes.fromhex(
        "535a3030000000000023000000000000000000000000000000000100000000000000000007010602ff93fefefe"
    ),
    bytes.fromhex(
        "535a3030000000000023000000000000000000000000000000000200000000000000000007010602ff93020237"
    ),
    bytes.fromhex(
        "535a3030000000000023000000000000000000000000000000000100000000000000000007010602ff93f04800"
    ),
    bytes.fromhex(
        "535a3030000000000023000000000000000000000000000000000200000000000000000007010602ff93ff0000"
    ),
]


@pytest.mark.parametrize(
    ("device_type", "name", "packet"),
    [
        (DeviceType.HEXAGON, "LifeSmart", HEXAGON_LIFESMART_COUNTER_1),
        (DeviceType.MIX, "Mix Rhythm default", MIX_RHYTHM_COUNTER_1),
        (DeviceType.STRIP, "LifeSmart", STRIP_LIFESMART_COUNTER_1),
    ],
    ids=["hexagon", "mix", "strip"],
)
async def test_set_effect_sends_the_effect(fake_light, device_type, name, packet):
    client = Cololight("127.0.0.1", device_type, port=fake_light.port)

    await client.set_effect(name)

    assert await fake_light.next_packet() == packet


async def test_a_multi_packet_effect_goes_out_in_order_on_one_socket(fake_light):
    client = Cololight("127.0.0.1", DeviceType.STRIP, port=fake_light.port)

    await client.set_effect("Red meteor")

    requests = [await fake_light.next_request() for _ in RED_METEOR_PACKETS]
    assert [packet for packet, _ in requests] == RED_METEOR_PACKETS
    assert len({address for _, address in requests}) == 1


@pytest.mark.parametrize(
    ("device_type", "name"),
    [
        (DeviceType.HEXAGON, "Mix Rhythm default"),
        (DeviceType.HEXAGON, "Rainbow Flow"),
        (DeviceType.STRIP, "Mix Rhythm default"),
    ],
)
async def test_an_effect_the_device_type_does_not_have_raises_a_validation_error(
    fake_light, device_type, name
):
    client = Cololight("127.0.0.1", device_type, port=fake_light.port)

    with pytest.raises(CololightValidationError) as raised:
        await client.set_effect(name)

    assert raised.value.field == "effect"
