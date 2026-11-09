import asyncio

import pytest

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
