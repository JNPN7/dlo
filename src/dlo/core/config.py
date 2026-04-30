from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Literal, Optional, get_args

import yaml

from dlo.common.exceptions import errors
from dlo.common.schema import SchemaMixin

Scope = Literal["name", "description", "tags"]


@dataclass
class VectorCollectionConfig(SchemaMixin):
    distance: Optional[str] = field(default=None)
    collection: str = field(default="dlo_vector_search")


@dataclass
class Aggregation(SchemaMixin):
    type: Literal["max", "avg"] = field(default="avg")
    min_match: int = field(default=1)
    top_k: int = field(default=3)


@dataclass
class VectorScopeConfig(SchemaMixin):
    weight: float = field(default=1)
    aggregation: Aggregation = field(default_factory=Aggregation)

    def __post_init__(self):
        if not isinstance(self.weight, (int, float)):
            raise TypeError("Weight must be a number")

        if not 0 <= self.weight <= 1:
            raise errors.DloConfigError("Weight must be between 0 and 1")


@dataclass
class VectorSearchConfig(SchemaMixin):
    embedding: str
    vector_store: str
    collection: VectorCollectionConfig = field(default_factory=VectorCollectionConfig)
    scope: dict[Scope, VectorScopeConfig] = field(
        default_factory=lambda: {s: VectorScopeConfig() for s in get_args(Scope)}
    )
    aggregation: Aggregation = field(default_factory=Aggregation)
    top_k: int = field(default=5)


@dataclass
class Project(SchemaMixin):
    name: str
    project_root: str
    version: str
    profile: str
    memory: Optional[list[str]] = field(default=None)
    runtime_config: dict = field(default_factory=dict)
    vector_search: Optional[VectorSearchConfig] = field(default=None)

    @cached_property
    def project_root_path(self):
        return Path(self.project_root).absolute()

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

        config["project_root"] = project_root_path

        return cls.from_dict(config)


@dataclass
class Engine(SchemaMixin):
    type: str
    config: dict


@dataclass
class Connection(SchemaMixin):
    type: str


@dataclass
class Embeddings(SchemaMixin):
    provider: str
    config: dict = field(default_factory=dict)


@dataclass
class VectorStore(SchemaMixin):
    type: str
    config: dict = field(default_factory=dict)


@dataclass
class Profile(SchemaMixin):
    engine: Engine
    connections: Optional[dict[str, Connection]] = field(default=None)
    embeddings: Optional[dict[str, Embeddings]] = field(default=None)
    vector_store: Optional[dict[str, VectorStore]] = field(default=None)

    @classmethod
    def __from_project__(cls, project: Project):
        # read of profile if profile.yaml exists else from ~/.config/dlo/profile.yml
        project_root_path = project.project_root_path

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
