from pathlib import Path


class ProjectInitializer:
    """Initializes a ProjectBrain workspace."""

    ROOT_DIR = ".projectbrain"

    DIRECTORIES = (
        "memory",
        "graph",
        "cache",
        "sessions",
    )

    FILES = (
        "project.toml",
        "state.db",
    )

    def initialize(self, project_root: Path | None = None) -> Path:
        """
        Initialize a ProjectBrain workspace.

        Parameters
        ----------
        project_root
            Directory where the workspace will be created.
            Defaults to the current working directory.

        Returns
        -------
        Path
            Path to the created `.projectbrain` directory.
        """

        root = (project_root or Path.cwd()) / self.ROOT_DIR

        root.mkdir(exist_ok=True)

        for directory in self.DIRECTORIES:
            (root / directory).mkdir(exist_ok=True)

        for filename in self.FILES:
            (root / filename).touch(exist_ok=True)

        return root