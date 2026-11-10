import pytest

from pycololight import Cololight, CololightValidationError, DeviceType

LIFESMART_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff04970400"
)
MIX_RHYTHM_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff0a000000"
)


@pytest.mark.parametrize(
    ("device_type", "name", "packet"),
    [
        (DeviceType.HEXAGON, "LifeSmart", LIFESMART_COUNTER_1),
        (DeviceType.MIX, "Mix Rhythm default", MIX_RHYTHM_COUNTER_1),
    ],
    ids=["hexagon", "mix"],
)
async def test_set_effect_sends_the_effect(fake_light, device_type, name, packet):
    client = Cololight("127.0.0.1", device_type, port=fake_light.port)

    await client.set_effect(name)

    assert await fake_light.next_packet() == packet


@pytest.mark.parametrize(
    ("device_type", "name"),
    [
        (DeviceType.HEXAGON, "Mix Rhythm default"),
        (DeviceType.HEXAGON, "Rainbow Flow"),
        (DeviceType.STRIP, "LifeSmart"),
    ],
)
async def test_an_effect_the_device_type_does_not_have_raises_a_validation_error(
    fake_light, device_type, name
):
    client = Cololight("127.0.0.1", device_type, port=fake_light.port)

    with pytest.raises(CololightValidationError) as raised:
        await client.set_effect(name)

    assert raised.value.field == "effect"
