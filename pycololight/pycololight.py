import socket

from .constants import (
    COMMAND_PREFIX,
    CUSTOM_EFFECT_COLOURS,
    CUSTOM_EFFECT_MODES,
    DEFAULT_EFFECTS,
)


class ColourSchemeException(Exception):
    pass


class ColourException(Exception):
    pass


class CycleSpeedException(Exception):
    pass


class ModeExecption(Exception):
    pass


class DefaultEffectExecption(Exception):
    pass


class BrightnessException(Exception):
    pass


class UnavailableException(Exception):
    pass


class PyCololight:
    """
    Cololight wrapper
    """

    def __init__(self, host, port=8900, default_effects=True):
        self.host = host
        self.port = port
        self._counter = 1
        self._on = False
        self._brightness = None
        self._colour = None
        self._effect = None
        self._effects = DEFAULT_EFFECTS.copy() if default_effects else {}
        self._sock = None

    def _toggle_counter(self):
        self._counter = 2 if self._counter == 1 else 1

    def _get_counter(self):
        count = f"000000000000000000000000000000000{self._counter}0000000000000000000"
        self._toggle_counter()
        return count

    def _socket_connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(4)

    def _socket_close(self):
        self._sock.close()

    def _send(self, command, response=False):
        self._socket_connect()
        self._sock.sendto(command, (self.host, self.port))

        if not response:
            self._socket_close()

    def _receive(self):
        try:
            data = self._sock.recvfrom(4096)[0]
            self._socket_close()
            return data
        except socket.timeout:
            self._socket_close()
            raise UnavailableException

    def _get_config(self, config_type):
        if config_type == "command":
            config = f"{COMMAND_PREFIX}20{self._get_counter()}4010301c"
        elif config_type == "effect":
            config = f"{COMMAND_PREFIX}23{self._get_counter()}4010602ff"
        elif config_type == "state":
            config = f"{COMMAND_PREFIX}1e{self._get_counter()}3020101"

        return config

    def _cycle_speed_hex(self, cycle_speed, mode):
        if not 1 <= cycle_speed <= 32:
            raise CycleSpeedException
        if mode in [2]:
            # Mode 2 only has speeds 1, 2, 3, which are mapped differently to other modes
            cycle_speed_values = [3, 11, 19]
            cycle_speed_value = cycle_speed_values[min(3, cycle_speed) - 1]
        else:
            cycle_speed_value = list(reversed(range(33)))[cycle_speed - 1]

        cycle_speed_hex = "{:02x}".format(cycle_speed_value)
        return cycle_speed_hex

    def _colour_hex(self, colour_scheme, colour, mode):
        if colour_scheme not in self.custom_effect_colour_schemes():
            raise ColourSchemeException
        if colour not in self.custom_effect_colour_scheme_colours(colour_scheme):
            raise ColourException

        starting_decimal = CUSTOM_EFFECT_COLOURS[colour_scheme]["decimal"]
        colour_key = CUSTOM_EFFECT_COLOURS[colour_scheme]["colours"].index(colour)
        if mode in [13, 14, 15, 22, 23, 24]:
            # These modes have a lower starting decimal of 128
            starting_decimal = starting_decimal - 128
        colour_decimal = starting_decimal + colour_key
        colour_hex = "{:02x}".format(colour_decimal)
        return colour_hex

    def _mode_hex(self, mode):
        if not 1 <= mode <= len(CUSTOM_EFFECT_MODES):
            raise ModeExecption

        return CUSTOM_EFFECT_MODES[mode - 1]

    @property
    def state(self):
        """
        Gets state (on/off) and brightness from device, and updates local state.
        """
        self._send(
            bytes.fromhex(f"{self._get_config('state')}"),
            response=True,
        )
        data = self._receive()
        if data[40] == 207:
            self._on = True
            self._brightness = data[41]
        elif data[40] == 206:
            self._on = False
        else:
            return

    @property
    def on(self) -> bool:
        """
        Returns the current on state.
        """
        return self._on

    @on.setter
    def on(self, brightness: int):
        """
        Turns the device on with desired brightness, or turns the device off if brightness is 0.
        """
        if brightness:
            self._on = True
            self.brightness = brightness
        else:
            self._on = False
            command = bytes.fromhex("{}{}".format(self._get_config("command"), "e1e"))
            self._send(command)

    @property
    def brightness(self) -> int:
        """
        Returns the current set brightness.
        """
        return self._brightness

    @brightness.setter
    def brightness(self, brightness: int):
        """
        Sets the brightness of the device.
        """
        if not 0 <= brightness <= 100:
            raise BrightnessException
        brightness_prefix = "f"
        command = bytes.fromhex(
            "{}{}{:02x}".format(
                self._get_config("command"),
                brightness_prefix,
                int(brightness),
            )
        )
        self._brightness = brightness
        self._send(command)

    @property
    def colour(self) -> tuple:
        """
        Returns the current set colour hue.
        """
        return self._colour

    @colour.setter
    def colour(self, colour: tuple):
        """
        Sets the colour of the device.
        """
        colour_prefix = "00"
        command = bytes.fromhex(
            "{}{}{:02x}{:02x}{:02x}".format(
                self._get_config("effect"), colour_prefix, *colour
            )
        )
        self._colour = colour
        self._send(command)

    @property
    def effect(self) -> str:
        """
        Returns the current set effect name.
        """
        return self._effect

    @effect.setter
    def effect(self, effect: str):
        """
        Set the effect of the device.
        """
        command = bytes.fromhex(
            "{}{}".format(
                self._get_config("effect"),
                self._effects[effect],
            )
        )
        self._effect = effect
        self._send(command)

    @property
    def default_effects(self) -> list:
        """
        Returns a list of names of the default effects for the device.
        """
        return list(DEFAULT_EFFECTS.keys())

    @property
    def effects(self) -> list:
        """
        Returns a list of names of the effects saved for the device.
        """
        return list(self._effects.keys())

    def restore_default_effects(self, effects: list):
        """
        Restors the given default effects, to the saved effects of the device.
        """
        for effect in effects:
            if effect not in DEFAULT_EFFECTS:
                raise DefaultEffectExecption

            self._effects[effect] = DEFAULT_EFFECTS[effect]

    def add_custom_effect(
        self, name: str, colour_scheme: str, colour: str, cycle_speed: int, mode: int
    ):
        """
        Adds a custom effect, to the saved effects of the device.
        """
        cycle_speed_hex = self._cycle_speed_hex(int(cycle_speed), int(mode))
        colour_hex = self._colour_hex(colour_scheme, colour, int(mode))
        mode_hex = self._mode_hex(int(mode))

        if mode in [2]:
            # Mode 2 has bytes arranged differently to other modes
            custom_effect_hex = (
                f"{mode_hex[0]}{cycle_speed_hex}{colour_hex}{mode_hex[1]}"
            )
        else:
            custom_effect_hex = (
                f"{mode_hex[0]}{colour_hex}{cycle_speed_hex}{mode_hex[1]}"
            )

        self._effects[name] = custom_effect_hex

    def custom_effect_colour_schemes(self) -> list:
        """
        Returns a list of the available colour schemes for custom efects.
        """
        return list(CUSTOM_EFFECT_COLOURS.keys())

    def custom_effect_colour_scheme_colours(self, colour_scheme) -> list:
        """
        Returns a list of the available colours for a given colour schemes for custom efects.
        """
        return list(filter(None, CUSTOM_EFFECT_COLOURS[colour_scheme]["colours"]))
