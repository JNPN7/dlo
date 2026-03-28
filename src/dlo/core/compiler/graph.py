from typing import Iterable, Optional

import networkx as nx

from dlo.core.models.graph import Node, NodeId, NodeMap
from dlo.core.models.resources import (
    ResourceTypes,
)


class Graph:
    def __init__(self, graph: Optional[nx.DiGraph] = None):
        if graph is None:
            graph = nx.DiGraph()

        self.graph: nx.DiGraph = graph

    def add_node(self, node_id: NodeId):
        self.graph.add_node(node_id)

    def add_edge(self, from_node: NodeId, to_node: NodeId):
        self.graph.add_edge(from_node, to_node)

    def add_edges_from(self, edges, **kwargs):
        self.graph.add_edges_from(edges, **kwargs)

    def remove_node(self, node_id: NodeId):
        self.graph.remove_node(node_id)

    def remove_nodes_from(self, nodes, **kwargs):
        self.graph.remove_nodes_from(nodes, **kwargs)

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
        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt
        import matplotlib.transforms as transforms
        import networkx as nx

        layers = self.layers
        pos = {}

        max_layer_size = max(len(layer) for layer in layers) if layers else 0
        num_layers = len(layers)

        width = max(12, num_layers * 2.5)
        height = max(8, max_layer_size * 1.2)

        fig, ax = plt.subplots(figsize=(width, height))

        # ------------------------
        # Calculate positions
        # ------------------------
        for layer_idx, layer in enumerate(layers):
            x = layer_idx * x_gap
            layer_height = (len(layer) - 1) * y_gap
            y_start = layer_height / 2

            for i, node in enumerate(layer):
                y = y_start - i * y_gap
                pos[node] = (x, y)

        # ------------------------
        # Node Colors
        # ------------------------
        NODE_COLOR_MAP = {
            "source": "#60A5FA",
            "ephemeral": "#22D3EE",
            "view": "#10B981",
            "materialized": "#FBBF24",
        }

        def get_node_type(node: Node):
            if node.resource_type == ResourceTypes.source:
                return "source"
            return str(node.type)

        node_color = []
        for node in self.graph.nodes:
            node_detail = nodes.get(node)
            if node_detail:
                node_type = get_node_type(node_detail)
                node_color.append(NODE_COLOR_MAP.get(node_type, "#cccccc"))
            else:
                node_color.append("#cccccc")

        # ------------------------
        # Draw edges & nodes
        # ------------------------
        nx.draw_networkx_edges(
            self.graph,
            pos,
            ax=ax,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
            edge_color="#aaaaaa",
            connectionstyle="arc3,rad=0.1",
        )

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            ax=ax,
            node_color=node_color,
            node_size=2000,
            edgecolors="white",
            linewidths=2,
        )

        # ------------------------
        # Draw Labels (Pixel-based offset)
        # ------------------------
        labels = {unique_id: node.name for unique_id, node in nodes.items()}

        for node, (x, y) in pos.items():
            if node in labels:
                # Offset 15 pixels downward
                text_transform = transforms.offset_copy(
                    ax.transData, fig=fig, x=0, y=-25, units='points'
                )

                ax.text(
                    x,
                    y,
                    labels[node],
                    transform=text_transform,
                    ha="center",
                    va="top",
                    fontsize=9,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
                )

        # ------------------------
        # Legend
        # ------------------------
        legend_handles = [
            mpatches.Patch(color=color, label=node_type.capitalize())
            for node_type, color in NODE_COLOR_MAP.items()
        ]

        ax.legend(
            handles=legend_handles,
            loc="upper right",
            frameon=True,
            title="Node Types",
        )

        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(figure_name, dpi=300, bbox_inches="tight")
        plt.close()

    def subgraph(self, nodes: Iterable[NodeId]) -> "Graph":
        # Take the original networkx graph and return a subgraph containing only
        # the selected unique_id nodes.
        return Graph(self.graph.subgraph(nodes))
