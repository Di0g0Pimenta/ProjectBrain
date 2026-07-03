from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ScannedFile:
    """
    Data Transfer Object (DTO) representing a discovered file.
    Contains only the minimum metadata required to identify a file.
    """
    path: Path
    relative_path: Path
