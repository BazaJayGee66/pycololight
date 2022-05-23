from .constants import (
    CUSTOM_EFFECT_COLOURS,
    CUSTOM_EFFECT_MODES,
    DEFAULT_EFFECTS,
)


class DefaultEffectExecption(Exception):
    pass


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
    def default_effects(self) -> dict:
        """
        Returns a dict of default effects with names and command hex values for the device.
        """
        return self._default_effects

    def restore_default_effects(self, effects: list):
        """
        Restors the given default effects, to the saved effects of the device.
        """
        for effect in effects:
            if effect not in self.default_effects:
                raise DefaultEffectExecption

            self._effects[effect] = self.default_effects[effect]
