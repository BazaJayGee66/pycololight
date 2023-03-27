# 2.1.0

## New Features

- Add ability to set timeout for device

# 2.0.0

This release enables support for the cololight strip device.

## New Features

- Add support for the cololight strip device
- Add dynamic effects for the cololight strip device
- Add custom effects for the cololight strip device

## Breaking Changes

- A device (`hexagon` or `strip`) must now be passed when creating `PyCololight` object

# 1.0.0

## New Features

- Add state to get light state (on/off) and brightness - Thanks [@pim12345](https://github.com/pim12345)

## Fixes

- Add missing exceptions
- Add BrightnessException if brightness not between 0 and 100
- Refactor for simpler code
- Rename `include_default_effects` to `restore_default_effects`
- Remove `count` property
- Add type hints, and docstring

# 0.0.2

## New Features

## Fixes

- Refactor for simpler code

# 0.0.1

Initial Release

## New Features

- Turn On
- Turn Off
- Set brightness
- Set colour
- Set effect
- Include/Exclude default effects
- Add custom effect

## Fixes
