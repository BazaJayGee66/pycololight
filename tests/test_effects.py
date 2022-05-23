import pytest

from pycololight import Effects  # pylint: disable=import-error


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

    def test_default_effects_returns_list_default_effect_names(self):
        effects = Effects(device="hexigon", default_effects=True)

        expected_default_effects = [
            "80s Club",
            "Cherry Blossom",
            "Cocktail Parade",
            "Instagrammer",
            "Pensieve",
            "Savasana",
            "Sunrise",
            "The Circus",
            "Unicorns",
            "Christmas",
            "Rainbow Flow",
            "Music Mode",
        ]

        assert effects.default_effects == expected_default_effects
