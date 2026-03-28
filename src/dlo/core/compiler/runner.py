import logging

from functools import cached_property
from typing import Mapping, TypeAlias

from dlo.adapters.adapter import Adapter
from dlo.core.compiler.graph import Graph
from dlo.core.config import Project
from dlo.core.constants import COMPILED_GRAPH_FIG_PATH_RUN
from dlo.core.models.graph import NodeId
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Model, ModelType
from dlo.core.models.schedule import Schedule, ScheduleNode
from dlo.core.utils.cron import clean_cron

log = logging.getLogger(__name__)


NodeMap: TypeAlias = Mapping[NodeId, Model]


class Runner:
    def __init__(self, manifest: Manifest, adapter: Adapter, project: Project):
        self.manifest: Manifest = manifest
        self.adapter: Adapter = adapter
        self.project: Project = project

        # It is as only models other than ephemeral need to be ran not for sources
        self.nodes: NodeMap = {
            _id: model
            for _id, model in manifest.models.items()
            if model.type != ModelType.ephemeral
        }

    @cached_property
    def graph(self):
        graph = Graph()

        for node in self.nodes.values():
            node_unique_id = node.unique_id
            graph.add_node(node_unique_id)
            graph.add_edges_from((dep, node_unique_id) for dep in node.depends_on.nodes)

        # Remove extra node and edges, caused by source nodes
        extra_nodes = [node for node in graph.nodes if node not in self.nodes]
        graph.remove_nodes_from(extra_nodes)

        return graph

    def draw_layer(self):
        graph = self.graph
        figure_name = self.project.project_root_path / COMPILED_GRAPH_FIG_PATH_RUN

        graph.draw_layer(nodes=self.nodes, figure_name=figure_name)

    def run_node(self, node_unique_id):
        node = self.nodes.get(node_unique_id)
        self.adapter.create_table(node)

    def run(self):
        self.draw_layer()

        for node_unique_id in self.graph.topoligical_sort:
            self.run_node(node_unique_id)

    # TODO: Duplicate Scheduling
    def draw_cron_dependents_graph(self, graph: Graph, cron: str):
        figure_name = self.project.project_root_path / f"{cron}.png"
        nodes = {_id: node for _id, node in self.nodes.items() if _id in graph.nodes}

        graph.draw_layer(nodes, figure_name=figure_name)

    def schedule(self, draw: bool = True):
        # TODO: Implement storing jobs info in file and use it to update job, pause and resume
        # TODO: Duplicate Scheduling
        schedule_cron = {}
        scheduled_jobs: Schedule = Schedule.__from_project__(self.project)

        for node in self.nodes.values():
            if node.schedule is None or node.schedule == "":
                continue

            if node.schedule not in schedule_cron:
                schedule_cron[node.schedule] = []

            schedule_cron[node.schedule].append(node.unique_id)

        for cron, node_unique_ids in schedule_cron.items():
            job_name = f"DLO-{clean_cron(cron)}"
            schedule_node = scheduled_jobs.schedules.get(cron, ScheduleNode(cron=cron))

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
                job_info=schedule_node.job_info,
            )

            # updating the schedule nodes
            schedule_node.job_info = job_info
            schedule_node.nodes = node_unique_ids

            scheduled_jobs.schedules[cron] = schedule_node

        # Pause jobs if not scheduled
        extra_crons = [
            cron for cron in scheduled_jobs.schedules.keys() if cron not in schedule_cron.keys()
        ]
        for extra_cron in extra_crons:
            schedule_node = scheduled_jobs.schedules.get(extra_cron, ScheduleNode(cron=extra_cron))
            if schedule_node.job_info is None:
                log.warning("Job info not found for `%s`", extra_cron)
                continue
            job_info = self.adapter.pause_job(job_info=schedule_node.job_info, cron=extra_cron)

            # updating the schedule nodes
            schedule_node.nodes = []
            schedule_node.job_info = job_info

        scheduled_jobs.save()

        log.info("Schedule cron nodes: %s", schedule_cron)
