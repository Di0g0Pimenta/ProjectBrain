from pathlib import Path

from projectbrain.scanner.filters import PathFilter


def test_path_filter_default_ignores(tmp_path: Path) -> None:
    filter_obj = PathFilter(tmp_path)
    assert filter_obj.is_ignored(Path(".git/config"))
    assert filter_obj.is_ignored(Path("__pycache__/main.cpython-310.pyc"))
    assert filter_obj.is_ignored(Path("node_modules/package.json"))
    assert not filter_obj.is_ignored(Path("src/main.py"))


def test_path_filter_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("*.txt\nbuild/")
    filter_obj = PathFilter(tmp_path)
    assert filter_obj.is_ignored(Path("test.txt"))
    assert filter_obj.is_ignored(Path("build/output.bin"))
    assert not filter_obj.is_ignored(Path("test.md"))
