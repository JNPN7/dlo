from pathlib import Path

from dlo.adapters.factory import AdapterFactory
from dlo.core.compiler.compiler import GraphCompiler
from dlo.core.compiler.runner import Runner
from dlo.core.config import Profile, Project
from dlo.core.constants import MANIFEST_FILE_NAME, TARGET_DIR
from dlo.core.models.manifest import Manifest
from dlo.core.parser.manifest import ManifestLoader


class Runtime:
    def __init__(self, project: Project, profile: Profile):
        self.project = project
        self.profile = profile
        self._manifest = None
        self._adapter = None

        self.project_root_path = Path(self.project.project_root)

    @property
    def manifest(self) -> Manifest:
        if self._manifest is None:
            manifest = ManifestLoader(self.project).load()
            self._manifest = manifest
        return self._manifest

    @property
    def adapter(self):
        if self._adapter is None:
            # Initialize adapter
            AdapterFactory()

            engine = self.profile.engine
            self._adapter = AdapterFactory.create(
                **engine.to_dict(),
                runtime_config=self.project.runtime_config
            )

        return self._adapter

    def write_manifest(self):
        path = self.project_root_path

        target_path = path / TARGET_DIR
        target_path.mkdir(parents=True, exist_ok=True)

        manifest_path = target_path / MANIFEST_FILE_NAME

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(self.manifest.to_json())

    def compile(self):
        compiler = GraphCompiler(manifest=self.manifest, project=self.project)
        compiler.compile()

        self.write_manifest()

    def run(self):
        self.compile()

        runner = Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)
        runner.run()

    def schedule(self):
        self.compile()

        runner = Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)
        runner.schedule()

        self.write_manifest()
