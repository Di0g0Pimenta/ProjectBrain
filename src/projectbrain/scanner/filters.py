from pathlib import Path
from typing import List, Optional

import pathspec


class PathFilter:
    """
    Evaluates whether a given path should be included or excluded based on
    ignore rules (e.g., .gitignore, default rules).
    """

    DEFAULT_IGNORES = [
        ".git/",
        ".projectbrain/",
        "__pycache__/",
        "node_modules/",
        "*.pyc",
        ".venv/",
        "venv/",
    ]

    def __init__(self, root_path: Path, additional_rules: Optional[List[str]] = None):
        self.root_path = root_path
        
        rules = list(self.DEFAULT_IGNORES)
        if additional_rules:
            rules.extend(additional_rules)
            
        gitignore_path = root_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                rules.extend(f.readlines())
                
        self._spec = pathspec.PathSpec.from_lines("gitignore", rules)

    def is_ignored(self, relative_path: Path) -> bool:
        """
        Check if a relative path matches the ignore rules.
        """
        return self._spec.match_file(relative_path.as_posix())
