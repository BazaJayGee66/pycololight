import pytest

from pycololight import DeviceType, detect_device_type

HEXAGON_PRO_REPLY = (
    b"MOD=OD_WE_QUAN\r\nSN=aa:bb:cc:dd:ee:ff\r\nNAME=QUAN\r\nSUBKEY=C32\r\n"
)
STRIP_REPLY = b"MOD=OD_WE_QUAN\r\nSN=11:22:33:44:55:66\r\nNAME=QUAN\r\nSUBKEY=HKC32\r\n"
MIX_PRO_REPLY = (
    b"MOD=OD_WE_MIX32\r\nSN=a1:b2:c3:d4:e5:f6\r\nNAME=QUAN\r\nSUBKEY=C32\r\n"
)


@pytest.mark.parametrize(
    ("reply", "device_type"),
    [
        (HEXAGON_PRO_REPLY, None),
        (STRIP_REPLY, None),
        (MIX_PRO_REPLY, DeviceType.MIX),
    ],
    ids=["hexagon pro", "strip", "mix pro"],
)
async def test_detect_device_type_searches_and_recognises_only_the_mix(
    fake_light, reply, device_type
):
    fake_light.replies.append(reply)

    assert await detect_device_type("127.0.0.1", port=fake_light.port) is device_type
    assert await fake_light.next_packet() == b"Z-SEARCH * \r\n"


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "light.invalid", "light..invalid"],
    ids=["silent light", "host that does not resolve", "malformed host"],
)
async def test_detect_device_type_gives_none_when_no_light_answers(fake_light, host):
    assert await detect_device_type(host, port=fake_light.port, timeout=0.1) is None
