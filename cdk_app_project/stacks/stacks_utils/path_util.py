from pathlib import Path

class PathResolver:
    """
    Utility to resolve asset paths relative to the project root.
    """

    def __init__(self, current_file: str, marker_file: str = "cdk.json"):
        self.base_path = self.find_project_root(Path(current_file).resolve(), marker_file)

    def find_project_root(self, start_path: Path, marker_file: str) -> Path:
        current = start_path
        while not (current / marker_file).exists():
            if current.parent == current:
                raise FileNotFoundError(f"Could not find project root containing '{marker_file}'")
            current = current.parent
        return current

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
