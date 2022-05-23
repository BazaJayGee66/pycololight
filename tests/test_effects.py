import pytest

from pycololight import (
    Effects,
    DefaultEffectExecption,
)  # pylint: disable=import-error


class TestEffects:
    def test_effects_returns_dict_effects(self):
        effects = Effects(device="hexigon", default_effects=True)

        expected_effects = {
            "80s Club": "049a0000",
            "Cherry Blossom": "04940800",
            "Cocktail Parade": "05bd0690",
            "Instagrammer": "03bc0190",
            "Pensieve": "04c40600",
            "Savasana": "04970400",
            "Sunrise": "01c10a00",
            "The Circus": "04810130",
            "Unicorns": "049a0e00",
            "Christmas": "068b0900",
            "Rainbow Flow": "03810690",
            "Music Mode": "07bd0990",
        }

        assert effects.effects == expected_effects

    def test_default_effects_returns_dict_default_effects(self):
        effects = Effects(device="hexigon", default_effects=True)

        expected_default_effects = {
            "80s Club": "049a0000",
            "Cherry Blossom": "04940800",
            "Cocktail Parade": "05bd0690",
            "Instagrammer": "03bc0190",
            "Pensieve": "04c40600",
            "Savasana": "04970400",
            "Sunrise": "01c10a00",
            "The Circus": "04810130",
            "Unicorns": "049a0e00",
            "Christmas": "068b0900",
            "Rainbow Flow": "03810690",
            "Music Mode": "07bd0990",
        }

        assert effects.default_effects == expected_default_effects

    def test_restore_default_effects_adds_given_default_effects(self):
        effects = Effects(device="hexigon", default_effects=False)

        restore_effects = [
            "Pensieve",
            "Savasana",
            "Sunrise",
        ]

        expected_effects = {
            "Pensieve": "04c40600",
            "Savasana": "04970400",
            "Sunrise": "01c10a00",
        }

        effects.restore_default_effects(restore_effects)

        assert effects.effects == expected_effects

    def test_restore_default_effects_raises_exception_when_effect_doesnt_exist(self):
        effects = Effects(device="hexigon", default_effects=False)

        restore_effects = [
            "Bad Effect",
        ]

        with pytest.raises(DefaultEffectExecption):
            effects.restore_default_effects(restore_effects)
