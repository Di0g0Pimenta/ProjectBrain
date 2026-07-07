"""
GraphBuilder — converts ParsedModule entities into Knowledge Graph nodes and edges.

Single responsibility: receive a ParsedModule and populate a KnowledgeGraph.
It does not read files, it does not write to disk, it does not resolve
cross-module relationships (that is the job of a future pipeline service).
"""

from __future__ import annotations

from projectbrain.graph.knowledge_graph import KnowledgeGraph
from projectbrain.graph.models import EdgeData, EdgeType, NodeData, NodeType
from projectbrain.parsers.models import ClassDef, FunctionDef, ParsedModule


class GraphBuilder:
    """
    Builds graph nodes and edges from a ParsedModule.

    Usage:
        graph = KnowledgeGraph()
        builder = GraphBuilder(graph)
        builder.add_module(parsed_module)
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph

    def add_module(self, module: ParsedModule) -> str:
        """
        Add all entities from a ParsedModule to the graph.

        Returns the node_id of the MODULE node created.
        """
        module_id = module.relative_path.as_posix()

        self._graph.upsert_node(
            NodeData(
                node_id=module_id,
                node_type=NodeType.MODULE,
                name=module.relative_path.stem,
                path=module.path,
                docstring=module.docstring,
            )
        )

        for imp in module.imports:
            self._add_import(module_id, imp.name, imp.module)

        for cls in module.classes:
            self._add_class(module_id, cls)

        for fn in module.functions:
            self._add_function(module_id, fn, parent_type=NodeType.MODULE)

        return module_id

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _add_import(
        self,
        module_id: str,
        name: str,
        source_module: str | None,
    ) -> None:
        import_id = f"{module_id}::import::{name}"

        # Imports can appear multiple times (re-imports); use upsert
        self._graph.upsert_node(
            NodeData(
                node_id=import_id,
                node_type=NodeType.IMPORT,
                name=name,
                meta={"from_module": source_module or ""},
            )
        )
        self._graph.add_edge(
            module_id,
            import_id,
            EdgeData(edge_type=EdgeType.IMPORTS, label="imports"),
        )

    def _add_class(self, module_id: str, cls: ClassDef) -> None:
        class_id = f"{module_id}::{cls.name}"

        self._graph.upsert_node(
            NodeData(
                node_id=class_id,
                node_type=NodeType.CLASS,
                name=cls.name,
                line=cls.line,
                docstring=cls.docstring,
                meta={"bases": list(cls.bases)},
            )
        )
        self._graph.add_edge(
            module_id,
            class_id,
            EdgeData(edge_type=EdgeType.CONTAINS, label="contains"),
        )

        # Add inheritance edges for base classes that are already in the graph
        for base in cls.bases:
            # We store the base name; cross-module resolution happens later
            self._graph.upsert_node(
                NodeData(
                    node_id=f"__unresolved__::{base}",
                    node_type=NodeType.CLASS,
                    name=base,
                    meta={"unresolved": True},
                )
            )
            self._graph.add_edge(
                class_id,
                f"__unresolved__::{base}",
                EdgeData(edge_type=EdgeType.INHERITS, label="inherits"),
            )

        for method in cls.methods:
            self._add_function(class_id, method, parent_type=NodeType.CLASS)

    def _add_function(
        self,
        parent_id: str,
        fn: FunctionDef,
        parent_type: NodeType,
    ) -> None:
        fn_id = f"{parent_id}::{fn.name}"

        self._graph.upsert_node(
            NodeData(
                node_id=fn_id,
                node_type=NodeType.FUNCTION,
                name=fn.name,
                line=fn.line,
                docstring=fn.docstring,
                return_annotation=fn.return_annotation,
                meta={
                    "is_async": fn.is_async,
                    "is_method": fn.is_method,
                    "args": [
                        {"name": a.name, "annotation": a.annotation}
                        for a in fn.args
                    ],
                },
            )
        )
        self._graph.add_edge(
            parent_id,
            fn_id,
            EdgeData(edge_type=EdgeType.CONTAINS, label="contains"),
        )
