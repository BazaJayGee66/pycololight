# pycololight

A Python3 wrapper for interacting with LifeSmart ColoLight

## Usage

```python
light = PyCololight(host="1.1.1.1")

# Turn on at 60% brightness
light.on = 60

# Set brightness to 70%
light.brightness = 70

# Set light colour
light.colour = (255, 127, 255)

# Set effect
light.effect = "Sunrise"

# Turn off
light.on = 0
```
