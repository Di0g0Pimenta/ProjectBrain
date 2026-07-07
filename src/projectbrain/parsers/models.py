"""
Domain models for parsed source code entities.

These dataclasses represent the semantic output of any parser implementation.
They are consumed by the Knowledge Graph (PB-004) and are intentionally
decoupled from any specific parsing library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ImportDef:
    """Represents a single import statement."""

    # The name being imported (e.g. 'os', 'Path', 'dataclass')
    name: str
    # The module it comes from, if any (e.g. 'pathlib' in 'from pathlib import Path')
    module: str | None = None
    # The local alias, if any (e.g. 'np' in 'import numpy as np')
    alias: str | None = None
    # True when it's a 'from X import Y' statement
    is_from_import: bool = False


@dataclass(frozen=True)
class ArgumentDef:
    """Represents a single function/method argument."""

    name: str
    # Type annotation as a source string (e.g. 'int', 'str | None', 'Path')
    annotation: str | None = None
    # Default value as a source string, if any
    default: str | None = None


@dataclass(frozen=True)
class FunctionDef:
    """Represents a function or method definition."""

    name: str
    line: int
    args: tuple[ArgumentDef, ...] = field(default_factory=tuple)
    # Return type annotation as a source string (e.g. 'None', 'list[str]')
    return_annotation: str | None = None
    docstring: str | None = None
    is_async: bool = False
    # True when defined inside a class body
    is_method: bool = False


@dataclass(frozen=True)
class ClassDef:
    """Represents a class definition."""

    name: str
    line: int
    # Base class names as strings (e.g. ['BaseModel', 'Exception'])
    bases: tuple[str, ...] = field(default_factory=tuple)
    docstring: str | None = None
    methods: tuple[FunctionDef, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ParsedModule:
    """
    Top-level entity representing a fully parsed source file.
    This is the primary output of any Parser implementation.
    """

    path: Path
    relative_path: Path
    docstring: str | None = None
    imports: tuple[ImportDef, ...] = field(default_factory=tuple)
    classes: tuple[ClassDef, ...] = field(default_factory=tuple)
    # Module-level functions (not methods)
    functions: tuple[FunctionDef, ...] = field(default_factory=tuple)
