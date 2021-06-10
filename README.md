# pycololight

A Python3 wrapper for interacting with LifeSmart ColoLight

## Usage

```python
from pycololight import PyCololight

light = PyCololight(host="1.1.1.1")

# Turn on at 60% brightness
light.on = 60

# Set brightness to 70%
light.brightness = 70

# Set light colour
light.colour = (255, 127, 255)

# Set effect
light.effect = "Sunrise"

# Create custom effect
light.add_custom_effect(
  name="custom effect",
  colour_scheme="Shadow",
  colour="Red, Yellow",
  cycle_speed=11,
  mode=1
)

# Turn off
light.on = 0
```

Mapping of modes for custom effects can be found [here](MODES.md)
