"""Tests for custom exceptions."""

import pytest

from zmk_to_pdf.exceptions import (
    ZMKToPDFError,
    ConfigurationError,
    LayerError,
    FileNotFoundError,
    InvalidArgumentError,
)


class TestExceptionHierarchy:
    """Test custom exception hierarchy."""

    def test_zmk_to_pdf_error_is_exception(self) -> None:
        """Test that ZMKToPDFError is an Exception."""
        assert issubclass(ZMKToPDFError, Exception)

    def test_configuration_error_inherits_from_base(self) -> None:
        """Test that ConfigurationError inherits from ZMKToPDFError."""
        assert issubclass(ConfigurationError, ZMKToPDFError)

    def test_layer_error_inherits_from_base(self) -> None:
        """Test that LayerError inherits from ZMKToPDFError."""
        assert issubclass(LayerError, ZMKToPDFError)

    def test_file_not_found_error_inherits_from_base(self) -> None:
        """Test that FileNotFoundError inherits from ZMKToPDFError."""
        assert issubclass(FileNotFoundError, ZMKToPDFError)

    def test_invalid_argument_error_inherits_from_base(self) -> None:
        """Test that InvalidArgumentError inherits from ZMKToPDFError."""
        assert issubclass(InvalidArgumentError, ZMKToPDFError)

    def test_can_raise_and_catch_base_exception(self) -> None:
        """Test raising and catching ZMKToPDFError."""
        with pytest.raises(ZMKToPDFError):
            raise ZMKToPDFError("Test error")

    def test_can_raise_and_catch_configuration_error(self) -> None:
        """Test raising and catching ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Configuration failed")

    def test_can_raise_and_catch_layer_error(self) -> None:
        """Test raising and catching LayerError."""
        with pytest.raises(LayerError):
            raise LayerError("Layer processing failed")

    def test_can_raise_and_catch_file_not_found_error(self) -> None:
        """Test raising and catching FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            raise FileNotFoundError("File not found")

    def test_can_raise_and_catch_invalid_argument_error(self) -> None:
        """Test raising and catching InvalidArgumentError."""
        with pytest.raises(InvalidArgumentError):
            raise InvalidArgumentError("Invalid argument")

    def test_catch_derived_with_base_exception(self) -> None:
        """Test catching derived exception with base exception handler."""
        with pytest.raises(ZMKToPDFError):
            raise ConfigurationError("Configuration error")

    def test_exception_message(self) -> None:
        """Test exception messages are preserved."""
        message = "Test error message"
        exc = ConfigurationError(message)
        assert str(exc) == message
