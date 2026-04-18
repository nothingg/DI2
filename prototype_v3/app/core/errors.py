class AppError(Exception):
    """Base application exception."""


class ConfigurationError(AppError):
    """Raised when required configuration is missing."""


class BrowserError(AppError):
    """Raised when a browser session cannot be created or used."""


class LoginError(AppError):
    """Raised when a login flow fails."""


class DownloadError(AppError):
    """Raised when a file download fails."""


class ValidationError(AppError):
    """Raised when downloaded output does not match expectations."""


class NoDataError(AppError):
    """Raised when the selected run has no data available from the source."""


class PartialDataError(AppError):
    """Raised when only part of the expected data is available."""
