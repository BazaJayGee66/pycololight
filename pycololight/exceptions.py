class CololightError(Exception):
    """
    Base class for pycololight's errors, also raised for a reply that can't be parsed.
    """


class CololightConnectionError(CololightError):
    """
    The light didn't reply in time, or the socket failed.
    """


class CololightValidationError(CololightError, ValueError):
    """
    An argument is outside what the light accepts. `field` names the argument.
    """

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
