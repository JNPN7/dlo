from dataclasses import dataclass, field

import yaml

from dlo.common.schema import SchemaMixin
from dlo.core.config import Project
from dlo.core.constants import MANIFEST_FILE_NAME, TARGET_DIR
from dlo.core.models.resources import Code, Metric, Model, Relationship, Source


@dataclass
class Manifest(SchemaMixin):
    sources: dict[str, Source] = field(default_factory=dict)
    models: dict[str, Model] = field(default_factory=dict)
    relationships: dict[str, Relationship] = field(default_factory=dict)
    metrics: dict[str, Metric] = field(default_factory=dict)
    code: dict[str, Code] = field(default_factory=dict)

    def save(self, project: Project):
        target_path = project.project_root_path / TARGET_DIR
        target_path.mkdir(parents=True, exist_ok=True)

        manifest_path = target_path / MANIFEST_FILE_NAME

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def __from_project__(cls, project: Project):
        target_path = project.project_root_path / TARGET_DIR
        target_path.mkdir(parents=True, exist_ok=True)

        manifest_path = target_path / MANIFEST_FILE_NAME

        if not manifest_path.exists():
            return None

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        return cls.from_dict(manifest)
