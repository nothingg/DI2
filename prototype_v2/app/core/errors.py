class PrototypeError(Exception):
    """Base exception for the rewrite prototype."""


class ConfigurationError(PrototypeError):
    """Raised when required configuration is missing."""


class LoginError(PrototypeError):
    """Raised when a login step fails."""


class DownloadError(PrototypeError):
    """Raised when expected files cannot be downloaded."""


class ValidationError(PrototypeError):
    """Raised when outputs do not pass validation."""
