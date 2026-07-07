"""
KnowledgeGraph — the central domain object of ProjectBrain.

Wraps a NetworkX DiGraph and exposes a semantic API.
All callers interact with NodeData and EdgeData — never with raw
NetworkX internals. This ensures that the storage engine (NetworkX)
remains an implementation detail.
"""

from __future__ import annotations

from typing import Iterator

import networkx as nx

from projectbrain.graph.exceptions import DuplicateNodeError, NodeNotFoundError
from projectbrain.graph.models import EdgeData, EdgeType, NodeData, NodeType


class KnowledgeGraph:
    """
    In-memory Knowledge Graph backed by NetworkX DiGraph.

    Responsibilities:
    - Store nodes (MODULE, CLASS, FUNCTION, IMPORT) and typed edges.
    - Provide a semantic query API for downstream consumers.
    - Never read from or write to disk or any database.
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()

    # -------------------------------------------------------------------------
    # Mutation API
    # -------------------------------------------------------------------------

    def add_node(self, data: NodeData) -> None:
        """
        Add a node to the graph.

        Raises:
            DuplicateNodeError: If a node with the same node_id already exists.
        """
        if self._graph.has_node(data.node_id):
            raise DuplicateNodeError(data.node_id)
        self._graph.add_node(data.node_id, data=data)

    def add_edge(self, source_id: str, target_id: str, data: EdgeData) -> None:
        """
        Add a directed edge between two existing nodes.

        Raises:
            NodeNotFoundError: If either source or target node does not exist.
        """
        self._ensure_node_exists(source_id)
        self._ensure_node_exists(target_id)
        self._graph.add_edge(source_id, target_id, data=data)

    def upsert_node(self, data: NodeData) -> None:
        """
        Add or update a node. Does not raise if node already exists.
        Use sparingly — prefer add_node for cleaner semantics.
        """
        self._graph.add_node(data.node_id, data=data)

    # -------------------------------------------------------------------------
    # Query API
    # -------------------------------------------------------------------------

    def get_node(self, node_id: str) -> NodeData:
        """
        Retrieve node data by id.

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        self._ensure_node_exists(node_id)
        return self._graph.nodes[node_id]["data"]  # type: ignore[return-value]

    def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(node_id)

    def nodes(self, node_type: NodeType | None = None) -> Iterator[NodeData]:
        """
        Iterate over all nodes, optionally filtered by type.
        """
        for _, attrs in self._graph.nodes(data=True):
            node_data: NodeData = attrs["data"]
            if node_type is None or node_data.node_type == node_type:
                yield node_data

    def edges(self, edge_type: EdgeType | None = None) -> Iterator[tuple[NodeData, NodeData, EdgeData]]:
        """
        Iterate over all edges, optionally filtered by type.
        Yields (source_data, target_data, edge_data) tuples.
        """
        for src, dst, attrs in self._graph.edges(data=True):
            edge_data: EdgeData = attrs["data"]
            if edge_type is None or edge_data.edge_type == edge_type:
                yield (
                    self._graph.nodes[src]["data"],
                    self._graph.nodes[dst]["data"],
                    edge_data,
                )

    def successors(self, node_id: str) -> Iterator[NodeData]:
        """
        Yield all nodes that this node points to (outgoing edges).

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        self._ensure_node_exists(node_id)
        for neighbour in self._graph.successors(node_id):
            yield self._graph.nodes[neighbour]["data"]

    def predecessors(self, node_id: str) -> Iterator[NodeData]:
        """
        Yield all nodes that point to this node (incoming edges).

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        self._ensure_node_exists(node_id)
        for neighbour in self._graph.predecessors(node_id):
            yield self._graph.nodes[neighbour]["data"]

    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _ensure_node_exists(self, node_id: str) -> None:
        if not self._graph.has_node(node_id):
            raise NodeNotFoundError(node_id)
