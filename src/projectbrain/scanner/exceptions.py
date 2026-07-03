class ScannerError(Exception):
    """Base exception for scanner module."""
    pass

class PathNotFoundError(ScannerError):
    """Raised when the specified path does not exist."""
    pass
