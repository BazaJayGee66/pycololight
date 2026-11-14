[![CI](https://github.com/BazaJayGee66/pycololight/actions/workflows/ci.yml/badge.svg)](https://github.com/BazaJayGee66/pycololight/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pycololight)](https://pypi.org/project/pycololight/)
[![Downloads](https://img.shields.io/pypi/dm/pycololight)](https://pypistats.org/packages/pycololight)

# pycololight

An asyncio Python library for controlling LifeSmart Cololight lights on your local network.

## Supported device types

| Device type          | Checked on                       |
| -------------------- | -------------------------------- |
| `DeviceType.HEXAGON` | Hexagon Pro, firmware 5.20.17.14 |
| `DeviceType.STRIP`   | Strip, firmware 6.10.3.12        |
| `DeviceType.MIX`     | MIX Pro, firmware 7.6.2.6        |

## Usage

```python
import asyncio

from pycololight import (
    Cololight,
    CololightConnectionError,
    CustomEffect,
    DeviceType,
)


async def main() -> None:
    light = Cololight("192.168.1.50", DeviceType.HEXAGON)

    try:
        state = await light.get_state()
    except CololightConnectionError:
        print("The light didn't answer")
        return
    print(state.on, state.brightness, state.mac, state.effect, state.colour)

    # Turn on at 60% brightness
    await light.turn_on(60)

    # Set light colour
    await light.set_colour((255, 127, 255))

    # Set effect
    await light.set_effect("Sunrise")

    # Set custom effect
    await light.set_effect(
        CustomEffect(
            device_type=DeviceType.HEXAGON,
            colour_scheme="Shadow",
            colour="Red, Yellow",
            pattern=1,
            speed=11,
        )
    )

    # Turn off
    await light.turn_off(60)


asyncio.run(main())
```

The patterns for custom effects are on the [patterns page](https://github.com/BazaJayGee66/pycololight/blob/main/MODES.md).

## Reading the state

`get_state()` returns a `CololightState`:

| Field        | Holds                                                |
| ------------ | ---------------------------------------------------- |
| `on`         | Whether the light is on                              |
| `brightness` | 0–100, or `None` while the light is off              |
| `mac`        | The light's MAC address, such as `aa:bb:cc:dd:ee:ff` |
| `effect`     | A built-in effect's name, or a `CustomEffect`        |
| `colour`     | A plain colour, as `(red, green, blue)`, each 0–255  |

At most one of `effect` and `colour` is set. Both are `None` when the light shows something pycololight can't name:

- Laser and Macaron away from their default speeds, because they're the same effect at different speeds.
- Eight of the Strip's multi-packet effects. The light only reports an effect's last packet, and these pairs end with the same one: Tricolor and Tron, Red meteor and Tropic affair, Sunset and Break dance, and Cranberry and Witch hut.
