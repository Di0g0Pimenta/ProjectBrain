"""
Tests for PythonParser.

Uses in-memory source strings written to tmp_path files to keep tests
hermetic and fast. No real project files are read.
"""

from pathlib import Path

import pytest

from projectbrain.parsers import (
    Parser,
    PythonParser,
    SyntaxParseError,
    UnsupportedFileTypeError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_py(tmp_path: Path, name: str, source: str) -> Path:
    """Write a Python source string to a temp file and return its path."""
    p = tmp_path / name
    p.write_text(source, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_python_parser_satisfies_protocol() -> None:
    """PythonParser must satisfy the Parser protocol."""
    assert isinstance(PythonParser(), Parser)


# ---------------------------------------------------------------------------
# Unsupported file type
# ---------------------------------------------------------------------------

def test_rejects_non_python_files(tmp_path: Path) -> None:
    p = tmp_path / "notes.md"
    p.touch()
    with pytest.raises(UnsupportedFileTypeError):
        PythonParser().parse(p, p)


# ---------------------------------------------------------------------------
# Syntax errors
# ---------------------------------------------------------------------------

def test_raises_syntax_error_on_invalid_python(tmp_path: Path) -> None:
    p = write_py(tmp_path, "bad.py", "def foo(:\n    pass\n")
    with pytest.raises(SyntaxParseError):
        PythonParser().parse(p, Path("bad.py"))


# ---------------------------------------------------------------------------
# Empty file
# ---------------------------------------------------------------------------

def test_parses_empty_file(tmp_path: Path) -> None:
    p = write_py(tmp_path, "empty.py", "")
    result = PythonParser().parse(p, Path("empty.py"))
    assert result.docstring is None
    assert result.imports == ()
    assert result.classes == ()
    assert result.functions == ()


# ---------------------------------------------------------------------------
# Module docstring
# ---------------------------------------------------------------------------

def test_extracts_module_docstring(tmp_path: Path) -> None:
    source = '"""This is the module docstring."""\n'
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.docstring == "This is the module docstring."


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

def test_extracts_plain_import(tmp_path: Path) -> None:
    p = write_py(tmp_path, "mod.py", "import os\n")
    result = PythonParser().parse(p, Path("mod.py"))
    assert len(result.imports) == 1
    imp = result.imports[0]
    assert imp.name == "os"
    assert imp.is_from_import is False
    assert imp.module is None


def test_extracts_from_import(tmp_path: Path) -> None:
    p = write_py(tmp_path, "mod.py", "from pathlib import Path\n")
    result = PythonParser().parse(p, Path("mod.py"))
    assert len(result.imports) == 1
    imp = result.imports[0]
    assert imp.name == "Path"
    assert imp.module == "pathlib"
    assert imp.is_from_import is True


def test_extracts_import_alias(tmp_path: Path) -> None:
    p = write_py(tmp_path, "mod.py", "import numpy as np\n")
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.imports[0].alias == "np"


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def test_extracts_function(tmp_path: Path) -> None:
    source = "def greet(name: str) -> str:\n    return name\n"
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert len(result.functions) == 1
    fn = result.functions[0]
    assert fn.name == "greet"
    assert fn.return_annotation == "str"
    assert fn.is_async is False
    assert fn.is_method is False


def test_extracts_async_function(tmp_path: Path) -> None:
    source = "async def fetch() -> None:\n    pass\n"
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.functions[0].is_async is True


def test_extracts_function_args(tmp_path: Path) -> None:
    source = "def add(x: int, y: int = 0) -> int:\n    return x + y\n"
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    fn = result.functions[0]
    assert len(fn.args) == 2
    assert fn.args[0].name == "x"
    assert fn.args[0].annotation == "int"
    assert fn.args[0].default is None
    assert fn.args[1].name == "y"
    assert fn.args[1].annotation == "int"


def test_extracts_function_docstring(tmp_path: Path) -> None:
    source = 'def foo():\n    """Does foo."""\n    pass\n'
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.functions[0].docstring == "Does foo."


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

def test_extracts_class(tmp_path: Path) -> None:
    source = "class Animal:\n    pass\n"
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert len(result.classes) == 1
    cls = result.classes[0]
    assert cls.name == "Animal"
    assert cls.bases == ()


def test_extracts_class_with_base(tmp_path: Path) -> None:
    source = "class Dog(Animal):\n    pass\n"
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.classes[0].bases == ("Animal",)


def test_extracts_class_methods(tmp_path: Path) -> None:
    source = (
        "class Greeter:\n"
        "    def hello(self, name: str) -> str:\n"
        "        return name\n"
    )
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    cls = result.classes[0]
    assert len(cls.methods) == 1
    method = cls.methods[0]
    assert method.name == "hello"
    assert method.is_method is True
    assert method.return_annotation == "str"


def test_class_methods_not_in_module_functions(tmp_path: Path) -> None:
    source = (
        "class Foo:\n"
        "    def bar(self) -> None:\n"
        "        pass\n"
        "\n"
        "def baz() -> None:\n"
        "    pass\n"
    )
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert len(result.functions) == 1
    assert result.functions[0].name == "baz"


def test_extracts_class_docstring(tmp_path: Path) -> None:
    source = 'class Foo:\n    """Foo class."""\n    pass\n'
    p = write_py(tmp_path, "mod.py", source)
    result = PythonParser().parse(p, Path("mod.py"))
    assert result.classes[0].docstring == "Foo class."
