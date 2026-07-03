from pathlib import Path
from typing import Iterator

from projectbrain.scanner.discovery import FileDiscoverer
from projectbrain.scanner.filters import PathFilter
from projectbrain.scanner.models import ScannedFile


class ProjectScanner:
    """
    Facade that coordinates FileDiscoverer and PathFilter to discover relevant files.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.filter = PathFilter(root_path)
        self.discoverer = FileDiscoverer(root_path)

    def scan(self) -> Iterator[ScannedFile]:
        """
        Scans the project and yields ScannedFile objects for relevant files.
        """
        def ignore_dir(rel_path: Path) -> bool:
            # pathspec needs a trailing slash to correctly match directory rules
            dir_posix = rel_path.as_posix() + "/"
            return self.filter.is_ignored(Path(dir_posix))

        for absolute_path, relative_path in self.discoverer.discover(ignore_dir):
            if not self.filter.is_ignored(relative_path):
                yield ScannedFile(path=absolute_path, relative_path=relative_path)
