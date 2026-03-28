import json

from itertools import chain
from pathlib import Path
from typing import Literal, Mapping, Optional

from dlo.common.exceptions import errors
from dlo.core.compiler.graph import Graph
from dlo.core.config import Project
from dlo.core.constants import COMPILED_GRAPH_FIG_PATH_NODES, MANIFEST_FILE_NAME, TARGET_DIR
from dlo.core.models.graph import NodeId, NodeMap
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import (
    CompiledResourceMixin,
    InjectedCTE,
    Model,
    ModelType,
    Source,
)
from dlo.core.parser.sql_parser import SqlParser


class GraphCompiler:
    def __init__(self, manifest: Manifest, project: Project):
        self.manifest: Manifest = manifest
        self.project: Project = project

        self._graph: Optional[Graph] = None

        # Nodes with mapping
        collections = [
            manifest.sources.values(),
            manifest.models.values(),
        ]
        self.nodes: NodeMap = {node.unique_id: node for node in chain(*collections)}

        self.project_root_path = Path(self.project.project_root)

    @property
    def graph(self):
        if self._graph is not None:
            return self._graph
        graph = Graph()

        for node in self.nodes.keys():
            graph.add_node(node)

        dependents = self.get_dependents_of_nodes()
        graph.add_edges_from((dep, node) for node, deps in dependents.items() for dep in deps)

        self._graph = graph
        return self._graph

    # NOTE: Replace file-based dependency loading with proper SQL parsing logic.
    # At the moment, dependencies are loaded directly from the file.
    # Future updates will introduce proper SQL parsing to accurately extract dependencies.
    # Replaced not remoded for backup
    def get_dependents_of_nodes_bak(self):
        dependents = {}

        dependents_path = self.project_root_path / "dependents.json"

        with open(dependents_path, "r") as f:
            dependents = json.load(f)
            dependents = dependents["dependents"]

        formatted_dependents = {}

        def _get_unique_id(type_: Literal["source", "model"], name: str) -> str:
            collections = {
                "source": self.manifest.sources,
                "model": self.manifest.models,
            }

            collection = collections.get(type_)
            if collection is None:
                raise errors.DloCompilationError(f"Unsupported type '{type_}'")

            node = collection.get(name)
            if node is None:
                raise errors.DloCompilationError(f"{name} not found in {type_}")

            return node.unique_id

        # First resolve all unique_ids once
        resolved = {
            idx: _get_unique_id(node["type"], node["name"]) for idx, node in dependents.items()
        }

        # Then build formatted_dependents directly
        formatted_dependents = {
            node_unique_id: [resolved[dep_idx] for dep_idx in node["dependents"]]
            for idx, node in dependents.items()
            for node_unique_id in [resolved[idx]]
        }

        return formatted_dependents

    def get_dependents_of_nodes(self):
        dependents: Mapping[NodeId, list[str]] = {}
        for node_unique_id, node in self.nodes.items():
            # We requires dependent of model only as source don't have dependents
            if not isinstance(node, Model):
                continue

            sql_parser = SqlParser(node.raw_code)
            dependent = sql_parser.extract_table()

            dependents[node_unique_id] = dependent

        return dependents

    def draw_layer(self):
        graph = self.graph
        figure_name = self.project_root_path / COMPILED_GRAPH_FIG_PATH_NODES

        graph.draw_layer(nodes=self.nodes, figure_name=figure_name)

    def _get_extra_ctes_of_predecessor(
        self, node_unique_id: NodeId, successor_node: CompiledResourceMixin
    ) -> list[InjectedCTE]:
        node = self.nodes[node_unique_id]

        # For sources, view model, materialized model
        def build_select_star_cte() -> InjectedCTE:
            if node.details is None:
                raise errors.DloCompilationError("Details is required for non-ephemeral model")
            successor_node.depends_on.add_node(node.unique_id)
            return InjectedCTE(
                id=node.unique_id,
                sql=f"{node.name} as (\n\tSELECT * FROM {node.details.full_name}\n)",
            )

        # Handle Compiled resources which is model rn
        if isinstance(node, CompiledResourceMixin):
            if not node.compiled:
                self.compile_node(node.unique_id)

            # Ephemeral model
            if node.type == ModelType.ephemeral:
                for node_id in node.depends_on.nodes:
                    successor_node.depends_on.add_node(node_id)
                return [
                    *node.extra_ctes,
                    InjectedCTE(
                        id=node.unique_id,
                        sql=f"{node.name} as (\n\t{node.raw_code}\n)",
                    ),
                ]

            # Handle non-ephemeral model
            return [build_select_star_cte()]

        # Handle sources
        if isinstance(node, Source):
            return [build_select_star_cte()]

        # Fallback
        return []

    def compile_node(self, node_unique_id: NodeId) -> None:
        node = self.nodes[node_unique_id]

        # Only compiled resources need compilation
        if not isinstance(node, CompiledResourceMixin):
            return

        # Collect predecessor CTEs
        extra_ctes = [
            cte
            for predecessor_id in self.graph.predecessors(node_unique_id)
            for cte in self._get_extra_ctes_of_predecessor(predecessor_id, node)
        ]

        # Mark compiled
        node.compiled = True
        node.extra_ctes = extra_ctes

        # Build compiled SQL
        if extra_ctes:
            node.compiled_code = (
                "WITH " + ", \n".join(cte.sql for cte in extra_ctes) + f"\n\n{node.raw_code}"
            )
        else:
            node.compiled_code = node.raw_code

        # write compiled code
        node.compiled_path = self.write_compiled_code_node(node).absolute().as_posix()

    def write_compiled_code_node(self, model: CompiledResourceMixin) -> Path:
        code_path = Path(model.code_path)
        relative_path = code_path.relative_to(self.project_root_path)

        compiled_path = self.project_root_path / TARGET_DIR / relative_path
        compiled_path.parent.mkdir(parents=True, exist_ok=True)

        with open(compiled_path, "w", encoding="utf-8") as f:
            f.write(model.compiled_code)
        return compiled_path

    def write_manifest(self):
        path = self.project_root_path

        target_path = path / TARGET_DIR
        target_path.mkdir(parents=True, exist_ok=True)

        manifest_path = target_path / MANIFEST_FILE_NAME

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(self.manifest.to_json())

    def compile(self):
        self.draw_layer()

        for node_unique_id in self.graph.topoligical_sort:
            self.compile_node(node_unique_id)

        self.write_manifest()
