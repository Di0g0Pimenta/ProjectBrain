from pathlib import Path
from typing import Callable, Iterator, Tuple

from projectbrain.scanner.exceptions import PathNotFoundError


class FileDiscoverer:
    """
    Discovers files in a directory tree recursively.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        if not self.root_path.exists() or not self.root_path.is_dir():
            raise PathNotFoundError(f"Directory not found: {self.root_path}")

    def discover(self, ignore_dir_func: Callable[[Path], bool]) -> Iterator[Tuple[Path, Path]]:
        """
        Yields (absolute_path, relative_path) for each file.
        Uses ignore_dir_func to prune directory traversal.
        """
        for absolute_path, relative_path in self._traverse(self.root_path, ignore_dir_func):
            yield absolute_path, relative_path

    def _traverse(self, current_dir: Path, ignore_dir_func: Callable[[Path], bool]) -> Iterator[Tuple[Path, Path]]:
        try:
            for item in current_dir.iterdir():
                relative_path = item.relative_to(self.root_path)
                
                if item.is_dir():
                    if not ignore_dir_func(relative_path):
                        yield from self._traverse(item, ignore_dir_func)
                elif item.is_file():
                    yield item, relative_path
        except PermissionError:
            # Skip directories we don't have permission to read
            pass
