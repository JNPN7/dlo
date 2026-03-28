from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from dlo.common.exceptions import errors
from dlo.common.schema import SchemaMixin


@dataclass
class Project(SchemaMixin):
    name: str
    project_root: str
    version: str
    profile: str
    memory: Optional[list[str]] = None

    @classmethod
    def __from_project_root__(cls, project_root: str):
        project_root_path = Path(project_root).absolute()

        def find_config_file(project_root_path: Path) -> Path:
            candidates = [
                project_root_path / "config.yaml",
                project_root_path / "config.yml",
            ]

            for path in candidates:
                if path.exists():
                    return path

            raise errors.DloConfigError(
                "Project config file not found.\n"
                "Add `config.yaml` or `config.yml` to the project root directory."
            )

        config_file = find_config_file(project_root_path)

        with open(config_file) as f:
            config = yaml.safe_load(f)

        return cls.from_dict({"project_root": project_root_path, **config})


@dataclass
class Engine(SchemaMixin):
    type: str
    config: dict


@dataclass
class Connection(SchemaMixin):
    type: str


@dataclass
class Profile(SchemaMixin):
    engine: Engine
    connections: Optional[dict[str, Connection]] = field(default=None)

    @classmethod
    def __from_project__(cls, project: Project):
        # read of profile if profile.yaml exists else from ~/.config/dlo/profile.yml
        project_root_path = Path(project.project_root).absolute()

        def find_profile_file(project_root_path: Path) -> Path:
            candidates = [
                project_root_path / "profile.yaml",
                project_root_path / "profile.yml",
                Path("~/.config/dlo/profile.yaml").expanduser(),
                Path("~/.config/dlo/profile.yml").expanduser(),
            ]

            for path in candidates:
                if path.exists():
                    return path

            raise errors.DloConfigError(
                "Profile config file not found.\n"
                "Add `~/.config/dlo/profile.yaml` (recommended) "
                "or add `profile.yaml` / `profile.yml` to the project root directory."
            )

        profile_file = find_profile_file(project_root_path)

        with open(profile_file) as f:
            profile_config = yaml.safe_load(f)

        if profile_config is None:
            raise errors.DloConfigError("Profile config file is empty")
        profile_config_of_name = profile_config.get(project.profile)

        if profile_config_of_name is None:
            raise errors.DloConfigError(f"Profile config for {project.profile} doesn't exists")

        return cls.from_dict(profile_config_of_name)
