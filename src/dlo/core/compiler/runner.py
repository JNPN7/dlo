import logging

from pathlib import Path
from typing import Mapping, Optional, TypeAlias

from dlo.adapters.adapter import Adapter
from dlo.core.compiler.graph import Graph
from dlo.core.config import Project
from dlo.core.constants import COMPILED_GRAPH_FIG_PATH_RUN
from dlo.core.models.graph import NodeId
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Model, ModelType

log = logging.getLogger(__name__)


NodeMap: TypeAlias = Mapping[NodeId, Model]


class Runner:
    def __init__(self, manifest: Manifest, adapter: Adapter, project: Project):
        self.manifest: Manifest = manifest
        self.adapter: Adapter = adapter
        self.project: Project = project

        self._graph: Optional[Graph] = None

        # It is as only models other than ephemeral need to be ran not for sources
        self.nodes: NodeMap = {
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
        self.adapter.create_table(node)

    def run(self):
        self.draw_layer()

        for node_unique_id in self.graph.topoligical_sort:
            self.run_node(node_unique_id)

    def draw_cron_dependents_graph(self, graph: Graph, cron: str):
        figure_name = self.project_root_path / f"{cron}.png"
        nodes = {_id: node for _id, node in self.nodes.items() if _id in graph.nodes}

        graph.draw_layer(nodes, figure_name=figure_name)

    def schedule(self, draw: bool = True):
        # TODO: Implement storing jobs info in file and use it to update job, pause and resume
        schedule_cron = {}
        scheduled_jobs = {}

        for node in self.nodes.values():
            if node.schedule is None or node.schedule == "":
                continue

            if node.schedule not in schedule_cron:
                schedule_cron[node.schedule] = []

            schedule_cron[node.schedule].append(node.unique_id)

        for cron, node_unique_ids in schedule_cron.items():
            job_name = f"DLO-{cron}"
            cron_graph = self.graph.subgraph(node_unique_ids)

            if draw:
                self.draw_cron_dependents_graph(cron_graph, cron)

            for node_unique_id in node_unique_ids:
                node = self.nodes[node_unique_id]

                for predecessor_node_unique_id in cron_graph.predecessors(node.unique_id):
                    node.schedule_depends_on.nodes.append(predecessor_node_unique_id)

            job_info = self.adapter.create_job(
                node_map=self.nodes,
                nodes=list(cron_graph.topoligical_sort),
                job_name=job_name,
                cron=cron,
            )

            scheduled_jobs[cron] = job_info

        log.info("Schedule cron nodes: %s", schedule_cron)
