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
    CololightError,
    CololightValidationError,
    CustomEffect,
    DeviceType,
    detect_device_type,
)


async def main() -> None:
    host = "192.168.1.50"

    # Only the MIX can be detected, so pass the type of anything else yourself.
    device_type = await detect_device_type(host) or DeviceType.HEXAGON
    light = Cololight(host, device_type)

    try:
        state = await light.get_state()
    except CololightConnectionError:
        print("The light didn't answer")
        return
    except CololightError:
        print("The light's answer couldn't be read")
        return
    print(state.on, state.brightness, state.mac, state.effect, state.colour)

    await light.set_colour((255, 127, 255))
    await light.turn_on(60)
    await light.set_effect("Sunrise")
    await light.set_effect(
        CustomEffect(
            device_type=device_type,
            colour_scheme="Shadow",
            colour="Red, Yellow",
            pattern=1,
            speed=11,
        )
    )
    await light.turn_off(60)

    try:
        await light.set_effect("Disco")
    except CololightValidationError as err:
        print(err.field, err)


asyncio.run(main())
```

`turn_on()` also sets the brightness, from 1 to 100. `turn_off()` takes the brightness the light was on at, because the light keeps it while it's off. Setting an effect doesn't switch an off light on.

Commands are send-and-forget. They return as soon as their packets are sent, without waiting for the light to acknowledge them. So a command to a light that isn't there doesn't raise anything, unless its packets can't be sent at all, such as when the host name doesn't resolve. `get_state()` does wait for the light's answer, for up to `timeout` seconds (4 by default, set with `Cololight(host, device_type, timeout=...)`).

`CololightError` is the base class of the other two errors, and is also raised when the light's answer can't be read. `CololightConnectionError` means the light didn't answer in time or the socket failed. `CololightValidationError` is also a `ValueError`, and its `field` names the argument that's out of range.

### Effects

`effect_names(device_type)` lists a device type's built-in effects, by the names the Cololight app uses and in the app's order.

On the Strip, 22 built-in effects are multi-packet effects, sent as several packets in a row: Tricolor, Children park, Tide, Forest, Red meteor, Go by, Sunset, Lilac, Innocence, Cranberry, Graffiti, Tron, Thunder, Witch hut, World cup, Break dance, Green meteor, Cyberpunk, Tropic affair, Cherry lake, Urban beauty and Blue meteor.

A `CustomEffect` is an effect from the app's effect builder: a colour scheme, a colour, a pattern and a speed. It's checked against its device type when it's made, and raises `CololightValidationError` if a field is out of range. `builder_limits(device_type)` lists the colour schemes and their colours, and each pattern's speeds. The patterns and the speed scale are on the [patterns page](https://github.com/BazaJayGee66/pycololight/blob/main/MODES.md).

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
- Effects pycololight doesn't have, such as the app's Discover effects and its own versions of the Strip's multi-packet effects.

A custom effect that's identical to a built-in reads back as the built-in's name. For example, pattern 16 with Shadow "Red, Green" at speed 24 is Christmas.

While the light is on, a `get_state()` sent straight after a command can still return the previous effect. A Strip's multi-packet effect can also read as `None` until the light has worked through its packets, which took no more than 2 seconds in testing.

## After a power cut

In testing, a light that was on came back on at the same brightness. The effect it came back with depends on the device type:

- **Hexagon:** it loses the last effect, and comes back on one it saved earlier. pycololight sends effects to the hexagon the way the app does, and the hexagon doesn't keep those.
- **Strip:** it keeps the last effect, unless that was a multi-packet effect. The Strip only saves an effect's last packet, so a multi-packet effect comes back as a different one.
- **MIX:** it keeps the last effect.

## Upgrading from 2.x

3.0 replaces `PyCololight` with `Cololight`, an asyncio client that keeps no state. Every call that talks to the light is awaited, and what the light is doing comes from `get_state()` instead of properties.

| 2.x                                                                                      | 3.0                                                                       |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `PyCololight(device="hexagon", host=host)`                                               | `Cololight(host, DeviceType.HEXAGON)`                                     |
| `light.state`, then `light.on` and `light.brightness`                                    | `state = await light.get_state()`, then `state.on` and `state.brightness` |
| `light.colour` and `light.effect`                                                        | `state.colour` and `state.effect`, read from the light                    |
| `light.on = 60` or `light.brightness = 60`                                               | `await light.turn_on(60)`                                                 |
| `light.on = 0`                                                                           | `await light.turn_off(brightness)`, passing the brightness it was on at   |
| `light.colour = (255, 127, 255)`                                                         | `await light.set_colour((255, 127, 255))`                                 |
| `light.effect = "Sunrise"`                                                               | `await light.set_effect("Sunrise")`                                       |
| `light.add_custom_effect(...)`, then `light.effect = name`                               | `await light.set_effect(CustomEffect(...))`                               |
| `light.effects`, `light.default_effects` and `light.dynamic_effects`                     | `effect_names(device_type)`                                               |
| `default_effects=` and `dynamic_effects=` arguments, and `restore_effects()`             | Removed. Every device type has its full list of effects.                  |
| `light.custom_effect_colour_schemes()` and `light.custom_effect_colour_scheme_colours()` | `builder_limits(device_type).colours`                                     |
| `Effects(device)`                                                                        | Removed. Use `effect_names()`, `builder_limits()` and `CustomEffect`.     |

The library no longer keeps a list of custom effects by name. Keep your own if you need one, such as a dict of names to `CustomEffect`s.

### Exceptions

| 2.x                                                                                   | 3.0                                                                                              |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `UnavailableException`                                                                | `CololightConnectionError`                                                                       |
| `BrightnessException`                                                                 | `CololightValidationError`, with `field` `"brightness"`                                          |
| `UnsupportedDeviceException`                                                          | `CololightValidationError`, with `field` `"device_type"`                                         |
| `ColourSchemeException`, `ColourException`, `ModeExecption` and `CycleSpeedException` | `CololightValidationError`, with `field` `"colour_scheme"`, `"colour"`, `"pattern"` or `"speed"` |
| `KeyError` for an unknown effect                                                      | `CololightValidationError`, with `field` `"effect"`                                              |
| `DefaultEffectExecption`                                                              | Removed with `restore_effects()`                                                                 |

### Built-in effects

Built-in effects now take the app's names:

| 2.x             | 3.0           |
| --------------- | ------------- |
| Savasana        | LifeSmart     |
| Cherry Blossom  | Peach blossom |
| Pensieve        | Aurora        |
| Unicorns        | Macaron       |
| Cocktail Parade | Rainbow       |
| Instagrammer    | Ice cream     |
| 80s Club        | Laser         |

Rainbow Flow, Music Mode and The Circus are removed, because the app doesn't offer them. 3.0's Circus is a different effect.

### Custom effects

`add_custom_effect`'s `mode` is now `CustomEffect`'s `pattern`, and `cycle_speed` is now `speed`. Speeds 1–32 run at the same speeds as in 2.x, and 33 is a new, faster step. Pattern 2 now only takes 1–3, where 2.x turned anything higher into 3.
