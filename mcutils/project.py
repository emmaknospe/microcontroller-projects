import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass
class Project:
    path: Path
    name: str
    engine: str

    @staticmethod
    def from_path(path: Path) -> 'Project':
        if not path.exists():
            raise FileNotFoundError(f"Project path {path} does not exist")
        if not (path / "project.json").exists():
            raise FileNotFoundError(f"Project path {path} does not contain a project.json file")
        with open(path / "project.json") as f:
            project_data = json.load(f)
        return Project(path=path, **project_data)