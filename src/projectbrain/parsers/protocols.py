"""
Language-agnostic Parser Protocol.

Any parser implementation (Python, TypeScript, Go, etc.) must satisfy
this protocol. Downstream consumers (Knowledge Graph, etc.) depend only
on this interface, never on a concrete implementation.
"""

from pathlib import Path
from typing import Protocol, runtime_checkable

from projectbrain.parsers.models import ParsedModule


@runtime_checkable
class Parser(Protocol):
    """
    Protocol that all language-specific parsers must implement.

    A parser receives a file path and returns a ParsedModule containing
    all extracted domain entities. It does not write to disk or to any
    database — it only reads and transforms.
    """

    def parse(self, path: Path, relative_path: Path) -> ParsedModule:
        """
        Parse a source file and return its domain representation.

        Args:
            path: Absolute path to the source file.
            relative_path: Path relative to the project root.

        Returns:
            A ParsedModule with all extracted entities.

        Raises:
            SyntaxParseError: If the file contains invalid syntax.
            UnsupportedFileTypeError: If the file type is not supported.
        """
        ...
