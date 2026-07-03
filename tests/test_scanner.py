from pathlib import Path

import pytest

from projectbrain.scanner import PathNotFoundError, ProjectScanner


def test_scanner_discovers_files(tmp_path: Path) -> None:
    (tmp_path / "main.py").touch()
    (tmp_path / "README.md").touch()
    
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").touch()
    
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "lib.js").touch()
    
    (tmp_path / ".gitignore").write_text("*.log\nsecret/")
    (tmp_path / "test.log").touch()
    secret_dir = tmp_path / "secret"
    secret_dir.mkdir()
    (secret_dir / "key.txt").touch()

    scanner = ProjectScanner(tmp_path)
    scanned_files = list(scanner.scan())
    
    relative_paths = {f.relative_path.as_posix() for f in scanned_files}
    
    assert "main.py" in relative_paths
    assert "README.md" in relative_paths
    assert ".gitignore" in relative_paths
    
    assert ".git/config" not in relative_paths
    assert "node_modules/lib.js" not in relative_paths
    assert "test.log" not in relative_paths
    assert "secret/key.txt" not in relative_paths


def test_scanner_invalid_path() -> None:
    with pytest.raises(PathNotFoundError):
        ProjectScanner(Path("/non/existent/path/123456"))
