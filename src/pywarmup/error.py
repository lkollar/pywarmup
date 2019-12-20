class PyWarmupError(Exception):
    """Base exception class for all errors in the library."""


class InvalidToken(PyWarmupError):
    """Invalid token received."""


class APIError(PyWarmupError):
    """API error."""


class TemperatureChangeFailure(PyWarmupError):
    """Failed to set temperature."""


class LocationModeChangeFailure(PyWarmupError):
    """Failed to change mode of location."""
