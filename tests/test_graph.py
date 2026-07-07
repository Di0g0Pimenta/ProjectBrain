from pathlib import Path
import pytest
from projectbrain.graph import (
    KnowledgeGraph,
    NodeData,
    EdgeData,
    NodeType,
    EdgeType,
    NodeNotFoundError,
    DuplicateNodeError,
    GraphBuilder,
)
from projectbrain.parsers import ParsedModule, ClassDef, FunctionDef, ImportDef, ArgumentDef


def test_knowledge_graph_basic_ops() -> None:
    graph = KnowledgeGraph()

    # Add nodes
    n1 = NodeData(node_id="src/main.py", node_type=NodeType.MODULE, name="main")
    n2 = NodeData(node_id="src/main.py::greet", node_type=NodeType.FUNCTION, name="greet")
    
    graph.add_node(n1)
    graph.add_node(n2)
    
    assert graph.node_count() == 2
    assert graph.has_node("src/main.py")
    assert graph.get_node("src/main.py").name == "main"
    
    # Duplicate node raises
    with pytest.raises(DuplicateNodeError):
        graph.add_node(n1)
        
    # Add edge
    edge = EdgeData(edge_type=EdgeType.CONTAINS, label="contains")
    graph.add_edge("src/main.py", "src/main.py::greet", edge)
    
    assert graph.edge_count() == 1
    
    # Query edges
    edges = list(graph.edges())
    assert len(edges) == 1
    src, dst, data = edges[0]
    assert src.node_id == "src/main.py"
    assert dst.node_id == "src/main.py::greet"
    assert data.edge_type == EdgeType.CONTAINS
    
    # Successors and predecessors
    succs = list(graph.successors("src/main.py"))
    assert len(succs) == 1
    assert succs[0].node_id == "src/main.py::greet"
    
    preds = list(graph.predecessors("src/main.py::greet"))
    assert len(preds) == 1
    assert preds[0].node_id == "src/main.py"


def test_knowledge_graph_missing_nodes() -> None:
    graph = KnowledgeGraph()
    with pytest.raises(NodeNotFoundError):
        graph.get_node("non_existent")
        
    with pytest.raises(NodeNotFoundError):
        graph.add_edge("src/main.py", "src/main.py::greet", EdgeData(edge_type=EdgeType.CONTAINS))


def test_graph_builder() -> None:
    graph = KnowledgeGraph()
    builder = GraphBuilder(graph)
    
    # Mock a ParsedModule
    module = ParsedModule(
        path=Path("/workspace/project/src/core.py"),
        relative_path=Path("src/core.py"),
        docstring="Core utilities",
        imports=(
            ImportDef(name="os"),
            ImportDef(name="Path", module="pathlib", is_from_import=True),
        ),
        classes=(
            ClassDef(
                name="Config",
                line=5,
                bases=("Base",),
                docstring="Config class",
                methods=(
                    FunctionDef(
                        name="load",
                        line=7,
                        args=(ArgumentDef(name="self"),),
                        return_annotation="None",
                        is_method=True,
                    ),
                ),
            ),
        ),
        functions=(
            FunctionDef(
                name="init_app",
                line=12,
                args=(ArgumentDef(name="verbose", annotation="bool"),),
                return_annotation="bool",
            ),
        ),
    )
    
    module_id = builder.add_module(module)
    assert module_id == "src/core.py"
    
    # Assert nodes created
    assert graph.has_node("src/core.py")
    assert graph.has_node("src/core.py::import::os")
    assert graph.has_node("src/core.py::import::Path")
    assert graph.has_node("src/core.py::Config")
    assert graph.has_node("src/core.py::Config::load")
    assert graph.has_node("src/core.py::init_app")
    assert graph.has_node("__unresolved__::Base")
    
    # Verify module node data
    mod_node = graph.get_node("src/core.py")
    assert mod_node.node_type == NodeType.MODULE
    assert mod_node.docstring == "Core utilities"
    assert mod_node.path == Path("/workspace/project/src/core.py")
    
    # Verify class node
    cls_node = graph.get_node("src/core.py::Config")
    assert cls_node.node_type == NodeType.CLASS
    assert cls_node.line == 5
    assert cls_node.meta["bases"] == ["Base"]
    
    # Verify relationships
    # MODULE -CONTAINS-> CLASS
    successors = {n.node_id for n in graph.successors("src/core.py")}
    assert "src/core.py::Config" in successors
    assert "src/core.py::init_app" in successors
    assert "src/core.py::import::os" in successors
    
    # CLASS -INHERITS-> Base
    cls_successors = {n.node_id for n in graph.successors("src/core.py::Config")}
    assert "__unresolved__::Base" in cls_successors
    assert "src/core.py::Config::load" in cls_successors
