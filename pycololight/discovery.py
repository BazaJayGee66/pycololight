from .client import DeviceType, _open_endpoint
from .exceptions import CololightConnectionError

_SEARCH = b"Z-SEARCH * \r\n"
_MIX_MODEL = b"OD_WE_MIX32"


async def detect_device_type(
    host: str, *, port: int = 12345, timeout: float = 4
) -> DeviceType | None:
    """
    Asks the light at `host` what it is. Only the MIX is recognised for now, so
    anything else gives `None`.
    """
    try:
        async with _open_endpoint(host, port, timeout) as endpoint:
            endpoint.send(_SEARCH)
            reply = await endpoint.reply
    except CololightConnectionError:
        return None
    return DeviceType.MIX if _parse_model(reply) == _MIX_MODEL else None


def _parse_model(reply: bytes) -> bytes | None:
    for line in reply.splitlines():
        key, _, value = line.partition(b"=")
        if key == b"MOD":
            return value
    return None
