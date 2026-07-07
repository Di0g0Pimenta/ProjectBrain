"""
Python source file parser using Python's built-in ast module.

Responsibilities:
- Read a .py file
- Parse it into an ast.Module
- Extract domain entities (imports, classes, functions, type annotations)
- Return a ParsedModule

This class does NOT write to disk, database, or any external system.
"""

from __future__ import annotations

import ast
from pathlib import Path

from projectbrain.parsers.exceptions import SyntaxParseError, UnsupportedFileTypeError
from projectbrain.parsers.models import (
    ArgumentDef,
    ClassDef,
    FunctionDef,
    ImportDef,
    ParsedModule,
)


class PythonParser:
    """
    Parser for Python source files.

    Satisfies the Parser protocol defined in parsers/protocols.py.
    Uses Python's built-in `ast` module — zero external dependencies.
    """

    SUPPORTED_EXTENSION = ".py"

    def parse(self, path: Path, relative_path: Path) -> ParsedModule:
        """
        Parse a Python source file and return its domain representation.

        Args:
            path: Absolute path to the .py file.
            relative_path: Path relative to the project root.

        Returns:
            A ParsedModule with all extracted entities.

        Raises:
            UnsupportedFileTypeError: If the file is not a .py file.
            SyntaxParseError: If the file contains a syntax error.
        """
        if path.suffix != self.SUPPORTED_EXTENSION:
            raise UnsupportedFileTypeError(
                f"PythonParser only supports .py files, got: '{path.suffix}'"
            )

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            raise SyntaxParseError(str(path), str(exc)) from exc

        return ParsedModule(
            path=path,
            relative_path=relative_path,
            docstring=ast.get_docstring(tree),
            imports=tuple(self._extract_imports(tree)),
            classes=tuple(self._extract_classes(tree)),
            functions=tuple(self._extract_functions(tree, is_method=False)),
        )

    # -------------------------------------------------------------------------
    # Private extraction helpers
    # -------------------------------------------------------------------------

    def _extract_imports(self, tree: ast.Module) -> list[ImportDef]:
        imports: list[ImportDef] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportDef(
                            name=alias.name,
                            alias=alias.asname,
                            is_from_import=False,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        ImportDef(
                            name=alias.name,
                            module=module,
                            alias=alias.asname,
                            is_from_import=True,
                        )
                    )

        return imports

    def _extract_functions(
        self,
        node: ast.Module | ast.ClassDef,
        is_method: bool,
    ) -> list[FunctionDef]:
        functions: list[FunctionDef] = []

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(
                    FunctionDef(
                        name=child.name,
                        line=child.lineno,
                        args=tuple(self._extract_args(child.args)),
                        return_annotation=self._annotation_to_str(child.returns),
                        docstring=ast.get_docstring(child),
                        is_async=isinstance(child, ast.AsyncFunctionDef),
                        is_method=is_method,
                    )
                )

        return functions

    def _extract_classes(self, tree: ast.Module) -> list[ClassDef]:
        classes: list[ClassDef] = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    ClassDef(
                        name=node.name,
                        line=node.lineno,
                        bases=tuple(self._base_to_str(b) for b in node.bases),
                        docstring=ast.get_docstring(node),
                        methods=tuple(
                            self._extract_functions(node, is_method=True)
                        ),
                    )
                )

        return classes

    def _extract_args(self, args: ast.arguments) -> list[ArgumentDef]:
        result: list[ArgumentDef] = []

        # Compute defaults aligned to the end of the args list
        n_args = len(args.args)
        n_defaults = len(args.defaults)
        defaults: list[str | None] = [None] * (n_args - n_defaults) + [
            self._annotation_to_str(d) for d in args.defaults
        ]

        for i, arg in enumerate(args.args):
            result.append(
                ArgumentDef(
                    name=arg.arg,
                    annotation=self._annotation_to_str(arg.annotation),
                    default=defaults[i],
                )
            )

        return result

    def _annotation_to_str(self, node: ast.expr | None) -> str | None:
        """Convert an AST annotation node to a readable string."""
        if node is None:
            return None
        try:
            return ast.unparse(node)
        except Exception:
            return None

    def _base_to_str(self, node: ast.expr) -> str:
        """Convert a base class AST node to a string."""
        try:
            return ast.unparse(node)
        except Exception:
            return ""
