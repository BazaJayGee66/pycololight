from .constants import (
    CUSTOM_EFFECT_COLOURS,
    CUSTOM_EFFECT_MODES,
    DEFAULT_EFFECTS,
)


class Effects:
    """
    Effects for cololight deveices
    """

    def __init__(self, device, default_effects=True) -> None:
        self.device = device
        self._effects = DEFAULT_EFFECTS.copy() if default_effects else {}
        self._default_effects = DEFAULT_EFFECTS.copy()

    @property
    def effects(self) -> dict:
        """
        Returns a dict of effects with names and command hex values saved for the device.
        """
        return self._effects

    @property
    def default_effects(self) -> list:
        """
        Returns a list of names of the default effects for the device.
        """
        return list(self._default_effects.keys())
