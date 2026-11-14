import asyncio
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from .builder import CustomEffect, _from_packet, _packet
from .catalogue import _EFFECT_NAMES, EFFECT_PACKETS, _built_in_from_packet
from .device_type import DeviceType, _to_device_type
from .exceptions import (
    CololightConnectionError,
    CololightError,
    CololightValidationError,
)

_PREFIX = bytes.fromhex("535a30300000000000")
_SET_POWER = bytes.fromhex("04010301")
_STATE_QUERY = bytes.fromhex("03020100")
_ON = 0xCF
_OFF = 0xCE
_STATE_REPLY = 0x83
_STATE_REPLY_MIN_LENGTH = 56
_ITEM_2 = bytes.fromhex("02ff")
_PLAIN_COLOUR = 0x00
_MAC_MARKER = b"\x0d\x01"

_SET_EFFECT = {
    DeviceType.HEXAGON: bytes.fromhex("04010602ff"),
    DeviceType.STRIP: bytes.fromhex("07010602ff"),
    DeviceType.MIX: bytes.fromhex("04010602ff"),
}


@dataclass(frozen=True)
class CololightState:
    """
    What the light reported when asked. `brightness` is 0–100, and `None` while off.
    `mac` is lowercase hex with colons, such as `aa:bb:cc:dd:ee:ff`. The light shows
    a plain `colour` or an `effect`, and both are `None` if it can't be named.
    """

    on: bool
    brightness: int | None
    mac: str
    effect: str | CustomEffect | None = None
    colour: tuple[int, int, int] | None = None


class Cololight:
    """
    Controls a Cololight over its local UDP protocol, without keeping any light state.
    """

    def __init__(
        self,
        host: str,
        device_type: DeviceType,
        *,
        port: int = 8900,
        timeout: float = 4,
    ) -> None:
        self.host = host
        self.device_type = _to_device_type(device_type)
        self.port = port
        self.timeout = timeout
        self._counter = 1

    async def turn_on(self, brightness: int) -> None:
        """
        Turns the light on at a brightness of 1–100.
        """
        _check_brightness(brightness)
        await self._send(_SET_POWER + bytes([_ON, brightness]))

    async def turn_off(self, brightness: int = 100) -> None:
        """
        Turns the light off. The light stores `brightness` (1–100) while it's off, so
        pass the brightness it was on at to keep it.
        """
        _check_brightness(brightness)
        await self._send(_SET_POWER + bytes([_OFF, brightness]))

    async def set_colour(self, rgb: tuple[int, int, int]) -> None:
        """
        Sets the light to a plain colour, each channel 0–255.
        """
        if len(rgb) != 3 or not all(0 <= channel <= 255 for channel in rgb):
            raise CololightValidationError(
                "rgb", f"Colour must be three channels of 0–255, not {rgb}"
            )
        await self._send(_SET_EFFECT[self.device_type] + bytes([0, *rgb]))

    async def set_effect(self, effect: str | CustomEffect) -> None:
        """
        Shows one of the device type's built-in effects, by name, or a custom effect.
        """
        prefix = _SET_EFFECT[self.device_type]
        await self._send(*(prefix + packet for packet in self._effect_packets(effect)))

    def _effect_packets(self, effect: str | CustomEffect) -> list[bytes]:
        if isinstance(effect, CustomEffect):
            if effect.device_type != self.device_type:
                raise CololightValidationError(
                    "effect",
                    f"Custom effect is for a {effect.device_type}, "
                    f"not a {self.device_type}",
                )
            return [_packet(effect)]
        if effect not in _EFFECT_NAMES[self.device_type]:
            raise CololightValidationError(
                "effect", f"Unknown {self.device_type} effect {effect!r}"
            )
        return [bytes.fromhex(packet) for packet in EFFECT_PACKETS[effect]]

    async def get_state(self) -> CololightState:
        """
        Asks the light whether it's on, at what brightness, what it's showing, and for
        its MAC address.
        """
        async with _open_endpoint(self.host, self.port, self.timeout) as endpoint:
            endpoint.send(self._frame(_STATE_QUERY))
            reply = await endpoint.reply
        return _parse_state(self.device_type, reply)

    def _frame(self, body: bytes) -> bytes:
        """
        Wraps a body in the header, whose packet counter flips between 1 and 2 on every
        packet.
        """
        counter = self._counter
        self._counter = 2 if counter == 1 else 1
        payload = bytes(16) + bytes([counter]) + bytes(9) + body
        return _PREFIX + bytes([len(payload)]) + payload

    async def _send(self, *bodies: bytes) -> None:
        async with _open_endpoint(self.host, self.port, self.timeout) as endpoint:
            for body in bodies:
                endpoint.send(self._frame(body))


@asynccontextmanager
async def _open_endpoint(
    host: str, port: int, timeout: float
) -> AsyncIterator["_Endpoint"]:
    loop = asyncio.get_running_loop()
    try:
        async with asyncio.timeout(timeout):
            _, endpoint = await loop.create_datagram_endpoint(
                _Endpoint, remote_addr=(host, port)
            )
            try:
                yield endpoint
            finally:
                endpoint.close()
    except TimeoutError as err:
        raise CololightConnectionError(
            f"Timed out after {timeout} s talking to {host}"
        ) from err
    except (OSError, UnicodeError) as err:
        raise CololightConnectionError(f"Can't reach {host}: {err}") from err


class _Endpoint(asyncio.DatagramProtocol):
    def __init__(self) -> None:
        self.reply: asyncio.Future[bytes] = asyncio.get_running_loop().create_future()

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        assert isinstance(transport, asyncio.DatagramTransport)
        self._transport = transport

    def datagram_received(self, data: bytes, addr: Any) -> None:
        if not self.reply.done():
            self.reply.set_result(data)

    def error_received(self, exc: Exception) -> None:
        if not self.reply.done():
            self.reply.set_exception(exc)

    def send(self, packet: bytes) -> None:
        self._transport.sendto(packet)
        # asyncio hands a failed send to error_received rather than raising it.
        if self.reply.done():
            self.reply.result()

    def close(self) -> None:
        self._transport.close()


def _check_brightness(brightness: int) -> None:
    if not 1 <= brightness <= 100:
        raise CololightValidationError(
            "brightness", f"Brightness must be 1–100, not {brightness}"
        )


def _parse_state(device_type: DeviceType, reply: bytes) -> CololightState:
    """
    Reads the light's answer to the state query, and raises `CololightError` if it
    isn't one.
    """
    mac = _parse_mac(reply[-14:])
    if (
        len(reply) < _STATE_REPLY_MIN_LENGTH
        or reply[36] != _STATE_REPLY
        or reply[40] not in (_ON, _OFF)
        or reply[41] > 100
        or mac is None
    ):
        raise CololightError(f"Can't read the light's state from {reply.hex()}")
    on = reply[40] == _ON
    effect, colour = _parse_shown(device_type, reply)
    return CololightState(
        on=on,
        brightness=reply[41] if on else None,
        mac=mac,
        effect=effect,
        colour=colour,
    )


def _parse_shown(
    device_type: DeviceType, reply: bytes
) -> tuple[str | CustomEffect | None, tuple[int, int, int] | None]:
    """
    Reads what the light is showing from the reply's item 2, if it has one.
    """
    if reply[42:44] != _ITEM_2:
        return None, None
    shown = reply[44:48]
    if shown[0] == _PLAIN_COLOUR:
        return None, (shown[1], shown[2], shown[3])
    built_in = _built_in_from_packet(device_type, shown)
    return built_in or _from_packet(device_type, shown), None


def _parse_mac(tail: bytes) -> str | None:
    """
    Reads a reply's tail: `0d01`, then the MAC as 12 ASCII hex digits.
    """
    if tail[:2] != _MAC_MARKER or not re.fullmatch(rb"[0-9A-Fa-f]{12}", tail[2:]):
        return None
    return bytes.fromhex(tail[2:].decode()).hex(":")
