from functools import cached_property
from typing import Optional

from dlo.adapters.factory import AdapterFactory
from dlo.core.compiler.compiler import GraphCompiler
from dlo.core.compiler.runner import Runner
from dlo.core.config import Profile, Project
from dlo.core.models.manifest import Manifest
from dlo.core.parser.manifest import ManifestLoader


class Runtime:
    def __init__(self, project: Project, profile: Profile, manifest: Optional[Manifest] = None):
        self.project = project
        self.profile = profile
        self._manifest = manifest

    @property
    def manifest(self) -> Manifest:
        if self._manifest is None:
            self._manifest = ManifestLoader(self.project).load()
        return self._manifest

    @cached_property
    def adapter(self):
        # Initialize adapter
        AdapterFactory()

        engine = self.profile.engine
        return AdapterFactory.create(
            **engine.to_dict(), runtime_config=self.project.runtime_config
        )

    @cached_property
    def graph_compiler(self):
        return GraphCompiler(manifest=self.manifest, project=self.project)

    @cached_property
    def runner(self):
        return Runner(manifest=self.manifest, adapter=self.adapter, project=self.project)

    def compile(self):
        self.graph_compiler.compile()

    def run(self):
        self.compile()

        self.runner.run()

    def schedule(self):
        self.compile()

        self.runner.schedule()

    def execute_query(self, query: str):
        result = self.runner.execute_query(query=query, graph_compiler=self.graph_compiler)
        return result

    def vector_search_init(self):
        from dlo.core.search.vector_search import VectorSearch

        vector_search = VectorSearch(
            manifest=self.manifest, project=self.project, profile=self.profile
        )
        vector_search.initialize()

    def vector_search_run(self, query: str):
        from dlo.core.search.vector_search import VectorSearch

        vector_search = VectorSearch(
            manifest=self.manifest, project=self.project, profile=self.profile
        )
        return vector_search.search(query=query)
