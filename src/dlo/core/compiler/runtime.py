from dlo.core.compiler.graph import GraphCompiler
from dlo.core.config import Profile, Project
from dlo.core.parser.manifest import ManifestLoader


class Runtime():
    def __init__(self, project: Project, profile: Profile):
        self.project = project
        self.profie = profile
        self._manifest = None

    @property
    def manifest(self):
        if self._manifest is None:
            manifest = ManifestLoader(self.project).load()
            self._manifest = manifest
        return manifest

    def compile(self):
        compiler = GraphCompiler(manifest=self.manifest, project=self.project)
        compiler.compile()
