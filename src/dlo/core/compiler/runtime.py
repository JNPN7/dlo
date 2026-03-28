from functools import cached_property

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

    @cached_property
    def manifest(self) -> Manifest:
        return ManifestLoader(self.project).load()

    @cached_property
    def adapter(self):
        # Initialize adapter
        AdapterFactory()

        engine = self.profile.engine
        return AdapterFactory.create(
            **engine.to_dict(), runtime_config=self.project.runtime_config
        )

    def compile(self):
        compiler = GraphCompiler(manifest=self.manifest, project=self.project)
        compiler.compile()

    def run(self):
        self.compile()

        runner = Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)
        runner.run()

    def schedule(self):
        self.compile()

        runner = Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)
        runner.schedule()
