import pytest

from pycololight import (
    Effects,
    ColourSchemeException,
    ColourException,
    CycleSpeedException,
    ModeExecption,
)  # pylint: disable=import-error

from pycololight.constants import (
    STRIP_DYANMIC_EFFECTS,
)  # pylint: disable=import-error


class TestEffects:
    def test_default_effects_returns_dict_default_effects(self):
        effects = Effects(device="hexigon")

        expected_default_effects = {
            "80s Club": ["049a0000"],
            "Cherry Blossom": ["04940800"],
            "Cocktail Parade": ["05bd0690"],
            "Instagrammer": ["03bc0190"],
            "Pensieve": ["04c40600"],
            "Savasana": ["04970400"],
            "Sunrise": ["01c10a00"],
            "The Circus": ["04810130"],
            "Unicorns": ["049a0e00"],
            "Christmas": ["068b0900"],
            "Rainbow Flow": ["03810690"],
            "Music Mode": ["07bd0990"],
        }

        assert effects.default_effects == expected_default_effects

    def test_custom_effect_colour_schemes_returns_supported_colour_schemes(self):
        effects = Effects(device="hexigon")

        supported_colour_schemes = [
            "Breath",
            "Shadow",
            "Flash",
            "Flicker",
            "Scene",
            "Mood",
            "Selected",
        ]

        assert effects.custom_effect_colour_schemes() == supported_colour_schemes

    def test_custom_effect_colour_scheme_colours_returns_colour_scheme_colours(self):
        effects = Effects(device="hexigon")

        expected_colours = [
            "Red, Green, Blue",
            "Rainbow",
            "Green",
            "Azure",
            "Blue",
            "Purple",
            "Red",
            "Orange",
            "Yellow",
            "White",
        ]

        assert (
            effects.custom_effect_colour_scheme_colours("Flicker") == expected_colours
        )

    def test_colour_hex_raises_exception_when_bad_scheme(self):
        effects = Effects(device="hexigon")

        with pytest.raises(ColourSchemeException):
            effects._colour_hex("bad_scheme", "colour", 1)

    def test_colour_hex_raises_exception_when_bad_colour(self):
        effects = Effects(device="hexigon")

        with pytest.raises(ColourException):
            effects._colour_hex("Mood", "bad_colour", 1)

    def test_cycle_speed_hex_raises_exception_when_bad_speed(self):
        effects = Effects(device="hexigon")

        with pytest.raises(CycleSpeedException):
            effects._cycle_speed_hex(35, 1)

    def test_mode_hex_raises_exception_when_bad_mode(self):
        effects = Effects(device="hexigon")

        with pytest.raises(ModeExecption):
            effects._mode_hex(0)

    def test_cycle_speed_hex_returns_hex_value(self):
        effects = Effects(device="hexigon")

        expected_responses = ["01", "20", "0d", "0b"]

        test_cycle_speeds = [(32, 1), (1, 1), (20, 1), (2, 2)]

        for index, test_speed in enumerate(test_cycle_speeds):
            cycle_speed = test_speed[0]
            mode = test_speed[1]
            cycle_speed_hex = effects._cycle_speed_hex(cycle_speed, mode)
            assert cycle_speed_hex == expected_responses[index]

    def test_mode_hex_returns_tuple_of_hex_values(self):
        effects = Effects(device="hexigon")

        expected_responses = [("05", "10"), ("05", "80"), ("06", "10"), ("06", "70")]

        test_modes = [3, 8, 17, 26]

        for index, mode in enumerate(test_modes):
            mode_hex = effects._mode_hex(mode)
            assert mode_hex == expected_responses[index]

    def test_colour_hex_returns_hex_value(self):
        effects = Effects(device="hexigon")

        expected_responses = ["80", "06", "a6", "b4", "bf", "c1", "c3"]

        test_colours = [
            ["Breath", "Red, Green, Blue", 1],
            ["Breath", "Red", 13],
            ["Flicker", "Azure", 1],
            ["Mood", "Orange", 1],
            ["Selected", "Savasana", 1],
            ["Selected", "Sunrise", 1],
            ["Selected", "Unicorns", 1],
        ]

        for index, colour in enumerate(test_colours):
            colour_hex = effects._colour_hex(colour[0], colour[1], colour[2])
            assert colour_hex == expected_responses[index]

    def test_custom_effect_command_returns_effect_command_hex(self):
        effects = Effects(device="hexigon")

        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 11
        effect_mood = 1

        custom_effect_command = effects.custom_effect_command(
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert custom_effect_command == "01b41600"

    def test_custom_effect_command_returns_effect_hex_when_mode_is_2(self):
        effects = Effects(device="hexigon")

        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 3
        effect_mood = 2

        custom_effect_command = effects.custom_effect_command(
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert custom_effect_command == "0213b400"

    def test_dynamic_effects_returns_dict_dynamic_effects(self):
        hexigon_effects = Effects(device="hexigon")
        strip_effects = Effects(device="strip")

        expected_hexigon_dynamic_effects = {}
        expected_strip_dynamic_effects = STRIP_DYANMIC_EFFECTS

        assert hexigon_effects.dynamic_effects == expected_hexigon_dynamic_effects
        assert strip_effects.dynamic_effects == expected_strip_dynamic_effects
