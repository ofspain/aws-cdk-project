from pathlib import Path

class PathResolver:
    """
    Utility to resolve asset paths relative to the project root.
    """

    def __init__(self, current_file: str, levels_up: int = 2):
        # Resolve up to the desired project root (default: 2 levels up)
        self.base_path = Path(current_file).resolve()
        for _ in range(levels_up):
            self.base_path = self.base_path.parent

    def path_from_root(self, *subpaths: str) -> Path:
        """
        Join subpaths to the base project root.
        Example: resolver.path_from_root('lambdas', 'db_initializer')
        """
        return self.base_path.joinpath(*subpaths)

    def as_str(self, *subpaths: str) -> str:
        """
        Returns the full resolved path as string.
        """
        return str(self.path_from_root(*subpaths))
