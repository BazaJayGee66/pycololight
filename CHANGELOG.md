# Changelog

## [3.0.0](https://github.com/BazaJayGee66/pycololight/compare/2.2.0...3.0.0) (2026-11-15)


### ⚠ BREAKING CHANGES

* PyCololight is removed. Use the async Cololight client, which takes host then device_type, with port and timeout by keyword only. turn_on(brightness) and turn_off() replace setting on and brightness, set_colour(rgb) replaces setting colour, set_effect(name) replaces setting effect, and get_state() replaces state and the getters. turn_on takes a brightness of 1-100. The client doesn't keep a list of effects, so the default_effects and dynamic_effects arguments, effects, default_effects, dynamic_effects, restore_effects(), add_custom_effect(), custom_effect_colour_schemes() and custom_effect_colour_scheme_colours() are removed.
* All errors now derive from CololightError. UnavailableException is now CololightConnectionError, and every other exception is now CololightValidationError.
* Effects is removed. Use effect_names(device_type) to list a device type's built-in effects, including the Strip's dynamic effects, and set_effect(name) to show one. Effects take the app's names: Savasana is LifeSmart, Cherry Blossom is Peach blossom, Pensieve is Aurora, Unicorns is Macaron, Cocktail Parade is Rainbow, Instagrammer is Ice cream and 80s Club is Laser. Rainbow Flow, Music Mode and The Circus are removed.
* Build a custom effect as a CustomEffect with keyword arguments and show it with set_effect, and use builder_limits(device_type) to list the colour schemes, colours, patterns and speeds. cycle_speed is now speed and mode is now pattern. Speed runs 1-33, where 33 is a new fastest step, and pattern 2 takes only 1-3 instead of clamping higher speeds.

### Features

* add detect_device_type() to recognise the MIX ([#20](https://github.com/BazaJayGee66/pycololight/issues/20)) ([65b6db7](https://github.com/BazaJayGee66/pycololight/commit/65b6db7c98811c0b8cb0d9574f1251b1f04f66ca))
* add the hexagon and MIX effect catalogue ([#21](https://github.com/BazaJayGee66/pycololight/issues/21)) ([97f9b31](https://github.com/BazaJayGee66/pycololight/commit/97f9b31e80bc92ac6ac2a25b1468bd7f452a1626))
* add the Strip's effect catalogue ([#22](https://github.com/BazaJayGee66/pycololight/issues/22)) ([31fe5fe](https://github.com/BazaJayGee66/pycololight/commit/31fe5feabb43de2350bff89a1670b30189cf43e7))
* read the current effect and colour back from the light ([#27](https://github.com/BazaJayGee66/pycololight/issues/27)) ([65a179c](https://github.com/BazaJayGee66/pycololight/commit/65a179c527ecc36bd23fe26965ef52b162baa55f))
* replace the custom-effect builder with a validated CustomEffect ([#23](https://github.com/BazaJayGee66/pycololight/issues/23)) ([9431746](https://github.com/BazaJayGee66/pycololight/commit/9431746aad3cd9edb81f1447b02f69ce2604359e))
* rewrite the client on asyncio with a stateless API ([#18](https://github.com/BazaJayGee66/pycololight/issues/18)) ([87e036a](https://github.com/BazaJayGee66/pycololight/commit/87e036a00bdc3a9b41dd01d7b056e071e6ceef9a))

## [2.2.0](https://github.com/BazaJayGee66/pycololight/compare/2.1.0...2.2.0) (2026-11-01)


### Features

* add full type hints and ship a py.typed marker ([#9](https://github.com/BazaJayGee66/pycololight/issues/9)) ([03da40a](https://github.com/BazaJayGee66/pycololight/commit/03da40a8eb01bdf6e38eb11621ffcc3ac1850f63))


### Bug Fixes

* open a socket per call so polls and commands can't share one ([#6](https://github.com/BazaJayGee66/pycololight/issues/6)) ([16aba29](https://github.com/BazaJayGee66/pycololight/commit/16aba298bc8dc8326df326c7f289c2fb74be0efe))
* report no brightness while the light is off ([#7](https://github.com/BazaJayGee66/pycololight/issues/7)) ([66e38d1](https://github.com/BazaJayGee66/pycololight/commit/66e38d1413d76ba68a7db2200dfc97add92a190e))

## 2.1.0

### New Features

- Add ability to set timeout for device

## 2.0.0

This release enables support for the cololight strip device.

### New Features

- Add support for the cololight strip device
- Add dynamic effects for the cololight strip device
- Add custom effects for the cololight strip device

### Breaking Changes

- A device (`hexagon` or `strip`) must now be passed when creating `PyCololight` object

## 1.0.0

### New Features

- Add state to get light state (on/off) and brightness - Thanks [@pim12345](https://github.com/pim12345)

### Fixes

- Add missing exceptions
- Add BrightnessException if brightness not between 0 and 100
- Refactor for simpler code
- Rename `include_default_effects` to `restore_default_effects`
- Remove `count` property
- Add type hints, and docstring

## 0.0.2

### New Features

### Fixes

- Refactor for simpler code

## 0.0.1

Initial Release

### New Features

- Turn On
- Turn Off
- Set brightness
- Set colour
- Set effect
- Include/Exclude default effects
- Add custom effect

### Fixes
