from pathlib import Path

from projectbrain.scanner.discovery import FileDiscoverer


def test_file_discoverer_basic(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").touch()
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "file2.txt").touch()

    discoverer = FileDiscoverer(tmp_path)
    files = list(discoverer.discover(lambda path: False))
    
    relative_paths = {f[1].as_posix() for f in files}
    assert "file1.txt" in relative_paths
    assert "subdir/file2.txt" in relative_paths


def test_file_discoverer_ignore_dir(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").touch()
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "file2.txt").touch()

    discoverer = FileDiscoverer(tmp_path)
    
    def ignore_subdir(path: Path) -> bool:
        return path.as_posix() == "subdir"
        
    files = list(discoverer.discover(ignore_subdir))
    
    relative_paths = {f[1].as_posix() for f in files}
    assert "file1.txt" in relative_paths
    assert "subdir/file2.txt" not in relative_paths
