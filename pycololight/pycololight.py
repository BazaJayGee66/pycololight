import socket

from pycololight.effects import Effects

from .constants import (
    COMMAND_PREFIX,
)


class DefaultEffectExecption(Exception):
    pass


class BrightnessException(Exception):
    pass


class UnavailableException(Exception):
    pass


class UnsupportedDeviceException(Exception):
    pass


class PyCololight:
    """
    Cololight wrapper
    """

    def __init__(
        self,
        device,
        host,
        port=8900,
        timeout=4,
        default_effects=True,
        dynamic_effects=False,
    ):
        self.supported_devices = ["hexagon", "strip"]
        self.device = self._check_supported_devices(device)
        self.host = host
        self.port = port
        self.timeout = timeout
        self._counter = 1
        self._on = False
        self._brightness = None
        self._colour = None
        self._effect = None
        self._device_effects = Effects(device)
        self._effects = self._initial_effects(default_effects, dynamic_effects)
        self._sock = None

    def _check_supported_devices(self, device):
        if device not in self.supported_devices:
            raise UnsupportedDeviceException
        else:
            return device

    def _initial_effects(self, default_effects, dynamic_effects):
        initial_effects = {}

        if default_effects:
            initial_effects.update(self._device_effects.default_effects)
        if dynamic_effects:
            initial_effects.update(self._device_effects.dynamic_effects)

        return initial_effects

    def _toggle_counter(self):
        self._counter = 2 if self._counter == 1 else 1

    def _get_counter(self):
        count = f"000000000000000000000000000000000{self._counter}0000000000000000000"
        self._toggle_counter()
        return count

    def _socket_connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(self.timeout)

    def _socket_close(self):
        self._sock.close()

    def _send(self, commands, response=False):
        self._socket_connect()
        for command in commands:
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

    @property
    def state(self):
        """
        Gets state (on/off) and brightness from device, and updates local state.
        """
        self._send(
            [bytes.fromhex(f"{self._get_config('state')}")],
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
            self._send([command])

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
        self._send([command])

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
        self._send([command])

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
        effect_commands = self._effects[effect]
        commands = []
        for effect_command in effect_commands:
            command = bytes.fromhex(
                "{}{}".format(
                    self._get_config("effect"),
                    effect_command,
                )
            )
            commands.append(command)
        self._effect = effect
        self._send(commands)

    @property
    def default_effects(self) -> list:
        """
        Returns a list of names of the default effects for the device.
        """
        return list(self._device_effects.default_effects.keys())

    @property
    def dynamic_effects(self) -> list:
        """
        Returns a list of names of the dynamic effects for the device.
        """
        return list(self._device_effects.dynamic_effects.keys())

    @property
    def effects(self) -> list:
        """
        Returns a list of names of the effects saved for the device.
        """
        return list(self._effects.keys())

    def restore_effects(self, effects: list):
        """
        Restors the given default/dynamic effects, to the saved effects of the device.
        """
        for effect in effects:
            if effect not in self._device_effects.effects.keys():
                raise DefaultEffectExecption

            self._effects[effect] = self._device_effects.effects[effect]

    def add_custom_effect(
        self, name: str, colour_scheme: str, colour: str, cycle_speed: int, mode: int
    ):
        """
        Adds a custom effect, to the saved effects of the device.
        """
        custom_effect_hex = self._device_effects.custom_effect_command(
            colour_scheme, colour, cycle_speed, mode
        )

        self._effects[name] = [custom_effect_hex]

    def custom_effect_colour_schemes(self) -> list:
        """
        Returns a list of the available colour schemes for custom efects.
        """
        return self._device_effects.custom_effect_colour_schemes()

    def custom_effect_colour_scheme_colours(self, colour_scheme) -> list:
        """
        Returns a list of the available colours for a given colour schemes for custom efects.
        """
        return self._device_effects.custom_effect_colour_scheme_colours(colour_scheme)
