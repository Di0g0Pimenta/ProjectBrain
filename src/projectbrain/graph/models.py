"""
Domain models for the Knowledge Graph.

Defines the types of nodes and edges, and the data they carry.
These models are the vocabulary of the Knowledge Graph — they are
intentionally decoupled from any storage or serialisation format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class NodeType(Enum):
    """Types of nodes in the Knowledge Graph."""
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    IMPORT = auto()


class EdgeType(Enum):
    """Types of directed edges in the Knowledge Graph."""
    # A module/class contains a class, function, or method
    CONTAINS = auto()
    # A module imports a symbol or module
    IMPORTS = auto()
    # A class inherits from another class
    INHERITS = auto()


@dataclass(frozen=True)
class NodeData:
    """
    Data attached to every node in the graph.

    The `node_id` is the unique identifier used as the graph key.
    Convention:
        MODULE   → relative path as posix string (e.g. "src/projectbrain/core/config.py")
        CLASS    → "<module_id>::<ClassName>"
        FUNCTION → "<module_id>::<function_name>" or "<class_id>::<method_name>"
        IMPORT   → "<module_id>::import::<name>"
    """
    node_id: str
    node_type: NodeType
    name: str
    # Line number in the source file (None for MODULE and IMPORT nodes)
    line: int | None = None
    # Docstring extracted from the source
    docstring: str | None = None
    # Absolute path — only set for MODULE nodes
    path: Path | None = None
    # Type annotation strings — used by FUNCTION nodes
    return_annotation: str | None = None
    # Extra metadata (e.g. is_async, is_method, bases)
    meta: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EdgeData:
    """Data attached to every edge in the graph."""
    edge_type: EdgeType
    # Optional label for human-readable export
    label: str = ""
