from dlo.adapters.factory import AdapterFactory
from dlo.core.compiler.compiler import GraphCompiler
from dlo.core.compiler.runner import Runner
from dlo.core.config import Profile, Project
from dlo.core.models.manifest import Manifest
from dlo.core.parser.manifest import ManifestLoader


class Runtime:
    def __init__(self, project: Project, profile: Profile):
        self.project = project
        self.profile = profile
        self._manifest = None
        self._adapter = None

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
            self._adapter = AdapterFactory.create(**engine.to_dict())

        return self._adapter

    def compile(self):
        compiler = GraphCompiler(manifest=self.manifest, project=self.project)
        compiler.compile()

    def run(self):
        self.compile()

        runner = Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)
        runner.run()
