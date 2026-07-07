class ParserError(Exception):
    """Base exception for the parsers module."""
    pass


class UnsupportedFileTypeError(ParserError):
    """Raised when a file type is not supported by any available parser."""
    pass


class SyntaxParseError(ParserError):
    """Raised when a file contains invalid syntax and cannot be parsed."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        super().__init__(f"Syntax error in '{path}': {message}")
