import pytest

from pycololight import (  # pylint: disable=import-error
    PyCololight,
    BrightnessException,
    UnsupportedDeviceException,
)

from pycololight.constants import STRIP_DYANMIC_EFFECTS

from unittest.mock import patch


class TestPyCololight:
    def test_raises_exception_when_device_not_supported(self):
        with pytest.raises(UnsupportedDeviceException):
            PyCololight(device="fake", host="1.1.1.1")

    @patch("pycololight.PyCololight._send")
    def test_turn_on(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        assert light.on == False

        light.on = 60

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"
            ]
        )

        assert light.on == True
        assert light.brightness == 60

    @patch("pycololight.PyCololight._send")
    def test_setting_brightness(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        light.brightness = 60

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"
            ]
        )

        assert light.brightness == 60

    @patch("pycololight.PyCololight._send")
    def test_setting_brightness_raises_exception_when_outside_bound(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        with pytest.raises(BrightnessException):
            light.brightness = 130

    @patch("pycololight.PyCololight._send")
    def test_setting_colour(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        assert light.colour == None

        light.colour = (255, 127, 255)

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x00\xff\x7f\xff"
            ]
        )

        assert light.colour == (255, 127, 255)

    @patch("pycololight.PyCololight._send")
    def test_setting_effect(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        assert light.effect == None

        light.effect = "Sunrise"

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x01\xc1\n\x00"
            ]
        )
        assert light.effect == "Sunrise"

    def test_effects_returns_list_of_effects(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        default_effects = [
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

        assert light.effects == default_effects

    @patch("pycololight.PyCololight._send")
    def test_turn_off(self, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        light._on = True

        light.on = 0
        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xce\x1e"
            ]
        )

        assert light.on == False

    def test_add_custom_effect_adds_effect(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        effect_name = "test_effect"
        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 11
        effect_mood = 1

        light.add_custom_effect(
            effect_name,
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert effect_name in light.effects
        assert light._effects[effect_name] == ["01b41600"]

    def test_add_custom_effect_adds_effect_when_mode_is_2(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        effect_name = "test_effect"
        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 3
        effect_mood = 2

        light.add_custom_effect(
            effect_name,
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert effect_name in light.effects
        assert light._effects[effect_name] == ["0213b400"]

    def test_custom_effect_colour_schemes_returns_supported_colour_schemes(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        supported_colour_schemes = [
            "Breath",
            "Shadow",
            "Flash",
            "Flicker",
            "Scene",
            "Mood",
            "Selected",
        ]

        assert light.custom_effect_colour_schemes() == supported_colour_schemes

    def test_custom_effect_colour_scheme_colours_returns_colour_scheme_colours(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

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

        assert light.custom_effect_colour_scheme_colours("Flicker") == expected_colours

    def test_excluding_defualt_effects(self):
        light = PyCololight(device="hexagon", host="1.1.1.1", default_effects=False)

        assert light.effects == []

    def test_default_effects_returns_list_of_default_effects(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        default_effects = [
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

        assert light.default_effects == default_effects

    def test_dynamic_effects_returns_list_of_dynamic_effects(self):
        hexagon_light = PyCololight(device="hexagon", host="1.1.1.1")
        strip_light = PyCololight(device="strip", host="1.1.1.1")

        hexagon_dynamic_effects = []
        strip_dynamic_effects = list(STRIP_DYANMIC_EFFECTS.keys())

        assert hexagon_light.dynamic_effects == hexagon_dynamic_effects
        assert strip_light.dynamic_effects == strip_dynamic_effects

    def test_restore_default_effects_adds_given_default_effects(self):
        light = PyCololight(device="strip", host="1.1.1.1", default_effects=False)

        effects = ["Pensieve", "Savasana", "Sunrise", "Tron"]

        light.restore_effects(effects)

        assert light.effects == effects

    def test_counter_returns_boolen_counter(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        assert light._counter == 1

        light._toggle_counter()
        assert light._counter == 2

        light._toggle_counter()
        assert light._counter == 1

    def test_get_config_returns_config_for_command(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        first_command_call = light._get_config("command")
        second_command_call = light._get_config("command")

        assert (
            first_command_call
            == "535a3030000000000020000000000000000000000000000000000100000000000000000004010301c"
        )
        assert (
            second_command_call
            == "535a3030000000000020000000000000000000000000000000000200000000000000000004010301c"
        )

    def test_get_config_returns_config_for_effect(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        first_effect_call = light._get_config("effect")
        second_effect_call = light._get_config("effect")

        assert (
            first_effect_call
            == "535a3030000000000023000000000000000000000000000000000100000000000000000004010602ff"
        )
        assert (
            second_effect_call
            == "535a3030000000000023000000000000000000000000000000000200000000000000000004010602ff"
        )

    def test_get_config_returns_config_for_state(self):
        light = PyCololight(device="hexagon", host="1.1.1.1")

        first_effect_call = light._get_config("state")
        second_effect_call = light._get_config("state")

        assert (
            first_effect_call
            == "535a303000000000001e000000000000000000000000000000000100000000000000000003020101"
        )
        assert (
            second_effect_call
            == "535a303000000000001e000000000000000000000000000000000200000000000000000003020101"
        )

    @patch("pycololight.PyCololight._send")
    @patch("pycololight.PyCololight._receive")
    def test_state_updates_state_and_brightness(self, mock_receive, mock_send):
        light = PyCololight(device="hexagon", host="1.1.1.1")
        assert light.on == False

        mock_receive.return_value = b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"

        light.state

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x02\x01\x01"
            ],
            response=True,
        )

        assert light.on == True
        assert light.brightness == 60

    @patch("pycololight.PyCololight._send")
    def test_setting_dynamic_effect(self, mock_send):
        light = PyCololight(device="strip", host="1.1.1.1", dynamic_effects=True)

        assert light.effect == None

        light.effect = "Graffiti"

        mock_send.assert_called_with(
            [
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\xfe\xfe\xfe",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\x05\x08\x8c",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\xf0\xa0\x03",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\xfa\x00\xff",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\xff\xaf\x00",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\x00\xc3\xff",
                b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x93\xff\x00\x91",
            ]
        )

        assert light.effect == "Graffiti"
