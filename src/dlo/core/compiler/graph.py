import json

from itertools import chain
from pathlib import Path
from typing import Literal, Optional

import networkx as nx

from dlo.common.exceptions import errors
from dlo.core.config import Project
from dlo.core.constants import MANIFEST_FILE_NAME, TARGET_DIR
from dlo.core.models.graph import Node, NodeId, NodeMap
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import (
    CompiledResourceMixin,
    InjectedCTE,
    ModelType,
    ResourceTypes,
    Source,
)


class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: NodeId):
        self.graph.add_node(node_id)

    def add_edge(self, from_node: NodeId, to_node: NodeId):
        self.graph.add_edge(from_node, to_node)

    def add_edges_from(self, edges, **kwargs):
        self.graph.add_edges_from(edges, **kwargs)

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def edges(self):
        return self.graph.edges

    @property
    def layers(self):
        layers = list(nx.topological_generations(self.graph))
        return layers

    @property
    def topoligical_sort(self):
        return nx.topological_sort(self.graph)

    def predecessors(self, node_id: NodeId):
        return self.graph.predecessors(node_id)

    def draw_layer(self, nodes: NodeMap, x_gap=2.0, y_gap=2.0, figure_name="dag_layered.png"):
        layers = self.layers
        pos = {}

        # Calculate dynamic figure size based on graph structure
        max_layer_size = max(len(layer) for layer in layers) if layers else 0
        num_layers = len(layers)

        # Heuristic for figure size (in inches)
        width = max(12, num_layers * 2.5)
        height = max(8, max_layer_size * 1.2)

        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt

        plt.figure(figsize=(width, height))

        # Calculate positions centering each layer vertically
        for layer_idx, layer in enumerate(layers):
            x = layer_idx * x_gap
            layer_height = (len(layer) - 1) * y_gap
            y_start = layer_height / 2

            for i, node in enumerate(layer):
                y = y_start - i * y_gap
                pos[node] = (x, y)

        NODE_COLOR_MAP = {
            "source": "#60A5FA",
            "ephemeral": "#22D3EE",
            "view": "#10B981",
            "materialized": "#FBBF24",
        }

        def get_node_type(node: Node):

            if node.resource_type == ResourceTypes.source:
                return ResourceTypes.source
            return node.type

        node_color = []
        for node in self.graph.nodes:
            node_detail = nodes.get(node)
            if node_detail:
                node_type = get_node_type(node_detail)
                node_color.append(NODE_COLOR_MAP.get(node_type, "#cccccc"))
            else:
                node_color.append("#cccccc")

        # Draw edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
            edge_color="#aaaaaa",
            connectionstyle="arc3,rad=0.1",
            node_size=2000,
        )

        labels = {unique_id: node.name for unique_id, node in nodes.items()}
        labels = {
            unique_id: f"{node.name}\n{unique_id.split('-')[0]}"
            for unique_id, node in nodes.items()
        }

        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color=node_color,
            node_size=2000,
            edgecolors="white",
            linewidths=2,
        )

        # Draw labels below nodes to avoid center placement
        # Offset depends on y scale, 0.25 is heuristic based on y_gap=1.5
        label_pos = {
            node: (coords[0], coords[1] - 0.25) for node, coords in pos.items()
        }

        nx.draw_networkx_labels(
            self.graph,
            label_pos,
            labels=labels,
            font_size=9,
            font_family="sans-serif",
            font_weight="bold",
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
        )

        # ------------------------
        # Add Legend
        # ------------------------
        legend_handles = [
            mpatches.Patch(
                color=NODE_COLOR_MAP[node_type],
                label=str(node_type).capitalize(),
            )
            for node_type in NODE_COLOR_MAP
        ]

        if legend_handles:
            plt.legend(
                handles=legend_handles,
                loc="upper right",
                frameon=True,
                title="Node Types",
            )

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(figure_name, dpi=300, bbox_inches="tight")
        plt.close()


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
        graph.add_edges_from(
            (dep, node)
            for node, deps in dependents.items()
            for dep in deps
        )

        self._graph = graph
        return self._graph

    # FIXME: Replace file-based dependency loading with proper SQL parsing logic.
    # At the moment, dependencies are loaded directly from the file.
    # Future updates will introduce proper SQL parsing to accurately extract dependencies.
    def get_dependents_of_nodes(self):

        dependents_path = self.project_root_path / "dependents.json"

        with open(dependents_path, 'r') as f:
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
            idx: _get_unique_id(node["type"], node["name"])
            for idx, node in dependents.items()
        }

        # Then build formatted_dependents directly
        formatted_dependents = {
            node_unique_id: [resolved[dep_idx] for dep_idx in node["dependents"]]
            for idx, node in dependents.items()
            for node_unique_id in [resolved[idx]]
        }

        return formatted_dependents

    def draw_layer(self):
        graph = self.graph
        figure_name = self.project_root_path / "dag_layered.png"

        graph.draw_layer(nodes=self.nodes, figure_name=figure_name)

    def _get_extra_ctes_of_predecessor(
        self, node_unique_id: NodeId, successor_node: CompiledResourceMixin
    ) -> list[InjectedCTE]:
        node = self.nodes[node_unique_id]

        # For sources, view model, materialized model
        def build_select_star_cte() -> InjectedCTE:
            if node.details is None:
                raise errors.DloCompilationError(
                    "Details is required for non-ephemeral model"
                )
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
                "WITH "
                + ", \n".join(cte.sql for cte in extra_ctes)
                + f"\n\n{node.raw_code}"
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

        for model in self.manifest.models.values():
            print(model.name, model.compiled_code)

        self.write_manifest()
