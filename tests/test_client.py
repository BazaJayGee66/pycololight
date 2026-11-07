import asyncio
import socket

import pytest

from pycololight import (
    Cololight,
    CololightConnectionError,
    CololightError,
    CololightState,
    CololightValidationError,
    DeviceType,
)

ON_AT_51_COUNTER_1 = bytes.fromhex(
    "535a3030000000000020000000000000000000000000000000000100000000000000000004010301cf33"
)
ON_AT_51_COUNTER_2 = bytes.fromhex(
    "535a3030000000000020000000000000000000000000000000000200000000000000000004010301cf33"
)
OFF_COUNTER_1 = bytes.fromhex(
    "535a3030000000000020000000000000000000000000000000000100000000000000000004010301ce64"
)
OFF_FROM_51_COUNTER_1 = bytes.fromhex(
    "535a3030000000000020000000000000000000000000000000000100000000000000000004010301ce33"
)
COLOUR_255_34_34_COUNTER_1 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff00ff2222"
)
COLOUR_36_12_255_COUNTER_2 = bytes.fromhex(
    "535a3030000000000023000000000000000000000000000000000200000000000000000004010602ff00240cff"
)
STATE_QUERY_COUNTER_1 = bytes.fromhex(
    "535a303000000000001e000000000000000000000000000000000100000000000000000003020101"
)
ON_AT_100_REPLY = bytes.fromhex(
    "535a303080000000002e00000000000004ac00000000000000000100000000000000003883020301cf64"
    "0d01414142424343444445454646"
)
STRIP_ON_AT_100_REPLY = bytes.fromhex(
    "535a303080000000002e00000000000004de00000000000000000100000000000000003f83020301cf64"
    "0d01313132323333343435353636"
)
MIX_ON_AT_100_REPLY = bytes.fromhex(
    "535a303080000000002e00000000000004bf00000000000000000100000000000000003f83020301cf64"
    "0d01413142324333443445354636"
)
ON_AT_51_REPLY = bytes.fromhex(
    "535a303080000000003a00000000000006ef00000000000000000100000000000000000083020f01cf33"
    "02ff049a000003fe000000000d01414142424343444445454646"
)
OFF_FROM_51_REPLY = bytes.fromhex(
    "535a303080000000003a000000000000072f00000000000000000100000000000000004083020f01ce33"
    "02ff0497040003fe000000000d01414142424343444445454646"
)
ON_AT_51_ACK = bytes.fromhex(
    "535a303080000000002e000000000000044400000000000000000200000000000000000084010301cf33"
    "0d01414142424343444445454646"
)

Address = tuple[str, int]


class FakeLight(asyncio.DatagramProtocol):
    def __init__(self) -> None:
        self.replies: list[bytes] = []
        self._received: asyncio.Queue[tuple[bytes, Address]] = asyncio.Queue()

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Address) -> None:
        self._received.put_nowait((data, addr))
        if self.replies:
            self.transport.sendto(self.replies.pop(0), addr)

    async def next_request(self) -> tuple[bytes, Address]:
        async with asyncio.timeout(1):
            return await self._received.get()

    async def next_packet(self) -> bytes:
        packet, _ = await self.next_request()
        return packet


@pytest.fixture
async def fake_light():
    transport, light = await asyncio.get_running_loop().create_datagram_endpoint(
        FakeLight, local_addr=("127.0.0.1", 0)
    )
    light.port = transport.get_extra_info("sockname")[1]
    yield light
    transport.close()


@pytest.fixture
def client(fake_light):
    return Cololight("127.0.0.1", DeviceType.HEXAGON, port=fake_light.port)


@pytest.mark.parametrize(
    "extra_args", [(8900,), (8900, 4)], ids=["port", "port and timeout"]
)
def test_port_and_timeout_are_keyword_only(extra_args):
    with pytest.raises(TypeError):
        Cololight("127.0.0.1", DeviceType.HEXAGON, *extra_args)


async def test_turn_on_sends_on_with_the_brightness(client, fake_light):
    await client.turn_on(51)

    assert await fake_light.next_packet() == ON_AT_51_COUNTER_1


async def test_turn_off_sends_off_at_full_brightness(client, fake_light):
    await client.turn_off()

    assert await fake_light.next_packet() == OFF_COUNTER_1


async def test_turn_off_from_a_brightness_sends_off_at_that_brightness(
    client, fake_light
):
    await client.turn_off(brightness=51)

    assert await fake_light.next_packet() == OFF_FROM_51_COUNTER_1


async def test_set_colour_sends_the_colour(client, fake_light):
    await client.set_colour((255, 34, 34))

    assert await fake_light.next_packet() == COLOUR_255_34_34_COUNTER_1


async def test_packet_counter_flips_on_every_packet_across_calls(client, fake_light):
    await client.turn_on(51)
    await client.set_colour((36, 12, 255))
    await client.turn_on(51)
    await client.turn_on(51)

    assert [await fake_light.next_packet() for _ in range(4)] == [
        ON_AT_51_COUNTER_1,
        COLOUR_36_12_255_COUNTER_2,
        ON_AT_51_COUNTER_1,
        ON_AT_51_COUNTER_2,
    ]


async def test_get_state_sends_the_state_query(client, fake_light):
    fake_light.replies.append(ON_AT_100_REPLY)

    await client.get_state()

    assert await fake_light.next_packet() == STATE_QUERY_COUNTER_1


async def test_get_state_reads_an_on_light_and_its_brightness(client, fake_light):
    fake_light.replies.append(ON_AT_51_REPLY)

    assert await client.get_state() == CololightState(
        on=True, brightness=51, mac="aa:bb:cc:dd:ee:ff"
    )


async def test_get_state_reports_no_brightness_while_the_light_is_off(
    client, fake_light
):
    fake_light.replies.append(OFF_FROM_51_REPLY)

    assert await client.get_state() == CololightState(
        on=False, brightness=None, mac="aa:bb:cc:dd:ee:ff"
    )


@pytest.mark.parametrize(
    ("reply", "mac"),
    [
        (ON_AT_100_REPLY, "aa:bb:cc:dd:ee:ff"),
        (STRIP_ON_AT_100_REPLY, "11:22:33:44:55:66"),
        (MIX_ON_AT_100_REPLY, "a1:b2:c3:d4:e5:f6"),
    ],
)
async def test_get_state_reads_the_mac_as_lowercase_hex_with_colons(
    client, fake_light, reply, mac
):
    fake_light.replies.append(reply)

    state = await client.get_state()

    assert state.mac == mac
    assert state.brightness == 100


async def test_get_state_with_no_reply_raises_a_connection_error(fake_light):
    client = Cololight(
        "127.0.0.1", DeviceType.HEXAGON, port=fake_light.port, timeout=0.1
    )

    with pytest.raises(CololightConnectionError):
        await client.get_state()


@pytest.mark.parametrize(
    "operation",
    [
        lambda client: client.turn_on(51),
        lambda client: client.get_state(),
    ],
    ids=["command", "get_state"],
)
async def test_a_host_that_does_not_resolve_raises_a_connection_error(operation):
    client = Cololight("light.invalid", DeviceType.HEXAGON)

    with pytest.raises(CololightConnectionError):
        await operation(client)


async def test_get_state_from_a_closed_port_raises_a_connection_error_without_waiting():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        closed_port = sock.getsockname()[1]
    client = Cololight("127.0.0.1", DeviceType.HEXAGON, port=closed_port)

    with pytest.raises(CololightConnectionError) as raised:
        await client.get_state()

    assert isinstance(raised.value.__cause__, ConnectionRefusedError)


@pytest.mark.parametrize(
    "reply",
    [
        ON_AT_100_REPLY[:41],
        ON_AT_51_ACK,
        ON_AT_100_REPLY[:40] + b"\x00" + ON_AT_100_REPLY[41:],
        ON_AT_100_REPLY[:41] + b"\x65" + ON_AT_100_REPLY[42:],
        ON_AT_100_REPLY[:-14] + bytes(14),
        ON_AT_100_REPLY[:-1] + b"Z",
    ],
    ids=[
        "truncated",
        "command ack",
        "unknown power",
        "brightness over 100",
        "no MAC",
        "MAC not hex",
    ],
)
async def test_get_state_raises_for_a_reply_it_cannot_parse(client, fake_light, reply):
    fake_light.replies.append(reply)

    with pytest.raises(CololightError) as raised:
        await client.get_state()

    assert type(raised.value) is CololightError


@pytest.mark.parametrize("brightness", [0, 101, -1])
@pytest.mark.parametrize(
    "operation",
    [
        lambda client, brightness: client.turn_on(brightness),
        lambda client, brightness: client.turn_off(brightness=brightness),
    ],
    ids=["turn_on", "turn_off"],
)
async def test_a_brightness_outside_1_to_100_raises_a_validation_error(
    client, operation, brightness
):
    with pytest.raises(CololightValidationError) as raised:
        await operation(client, brightness)

    assert raised.value.field == "brightness"
    assert isinstance(raised.value, ValueError)


@pytest.mark.parametrize("rgb", [(256, 0, 0), (0, -1, 0), (0, 0, 300), (0, 0, 0, 0)])
async def test_a_colour_that_is_not_three_channels_of_0_to_255_raises_a_validation_error(
    client, rgb
):
    with pytest.raises(CololightValidationError) as raised:
        await client.set_colour(rgb)

    assert raised.value.field == "rgb"


async def test_overlapping_operations_each_get_their_own_reply(client, fake_light):
    first = asyncio.create_task(client.get_state())
    _, first_address = await fake_light.next_request()
    second = asyncio.create_task(client.get_state())
    _, second_address = await fake_light.next_request()

    fake_light.transport.sendto(OFF_FROM_51_REPLY, second_address)
    fake_light.transport.sendto(ON_AT_51_REPLY, first_address)

    assert first_address != second_address
    assert (await second).on is False
    assert (await first).on is True
