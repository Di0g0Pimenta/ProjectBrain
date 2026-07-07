class GraphError(Exception):
    """Base exception for the graph module."""
    pass


class NodeNotFoundError(GraphError):
    """Raised when a requested node does not exist in the graph."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        super().__init__(f"Node not found in graph: '{node_id}'")


class DuplicateNodeError(GraphError):
    """Raised when attempting to add a node that already exists."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        super().__init__(f"Node already exists in graph: '{node_id}'")
