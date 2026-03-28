from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Optional

from dlo.adapters.adapter import Adapter
from dlo.core.compiler.graph import Graph
from dlo.core.config import Project
from dlo.core.constants import COMPILED_GRAPH_FIG_PATH_RUN
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Model, ModelType

if TYPE_CHECKING:
    from dlo.core.models.graph import NodeId


class Runner:
    def __init__(self, manifest: Manifest, adapter: Adapter, project: Project):
        self.manifest: Manifest = manifest
        self.adapter: Adapter = adapter
        self.project: Project = project

        self._graph: Optional[Graph] = None

        # It is as only models other than ephemeral need to be ran not for sources
        self.nodes: Mapping[NodeId, Model] = {
            _id: model
            for _id, model in manifest.models.items()
            if model.type != ModelType.ephemeral
        }

        self.project_root_path = Path(self.project.project_root)

    @property
    def graph(self):
        if self._graph is not None:
            return self._graph
        graph = Graph()

        for node in self.nodes.values():
            node_unique_id = node.unique_id
            graph.add_node(node_unique_id)
            graph.add_edges_from((dep, node_unique_id) for dep in node.depends_on.nodes)

        # Remove extra node and edges, caused by source nodes
        extra_nodes = [node for node in graph.nodes if node not in self.nodes]
        graph.remove_nodes_from(extra_nodes)

        self._graph = graph
        return self._graph

    def draw_layer(self):
        graph = self.graph
        figure_name = self.project_root_path / COMPILED_GRAPH_FIG_PATH_RUN

        graph.draw_layer(nodes=self.nodes, figure_name=figure_name)

    def run_node(self, node_unique_id):
        node = self.nodes.get(node_unique_id)
        self.adapter.create(node)

    def run(self):
        self.draw_layer()

        for node_unique_id in self.graph.topoligical_sort:
            self.run_node(node_unique_id)
