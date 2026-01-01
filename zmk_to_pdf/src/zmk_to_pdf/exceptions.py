"""Custom exceptions for ZMK Layout PDF Generator."""


class ZMKToPDFError(Exception):
    """Base exception for all ZMK to PDF errors."""

    pass


class ConfigurationError(ZMKToPDFError):
    """Raised when there's an error in configuration file or parsing."""

    pass


class LayerError(ZMKToPDFError):
    """Raised when there's an error with layer definitions or processing."""

    pass


class FileNotFoundError(ZMKToPDFError):
    """Raised when a required file cannot be found."""

    pass


class InvalidArgumentError(ZMKToPDFError):
    """Raised when invalid command-line arguments are provided."""

    pass
