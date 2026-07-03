from pathlib import Path

from projectbrain.services.project_initializer import ProjectInitializer


def test_initializer(tmp_path: Path) -> None:
    initializer = ProjectInitializer()

    root = initializer.initialize(tmp_path)

    assert (root / "memory").exists()
    assert (root / "graph").exists()
    assert (root / "cache").exists()
    assert (root / "sessions").exists()

    assert (root / "project.toml").exists()
    assert (root / "state.db").exists()