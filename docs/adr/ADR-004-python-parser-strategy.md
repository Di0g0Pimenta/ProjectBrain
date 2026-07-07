# ADR-004 — Python Parser Strategy

Status: Accepted

Date: 2026-07-07

## Context

PB-003 requires extracting semantic entities from Python source files (modules,
classes, functions, imports, type annotations) to feed the Knowledge Graph.

Three options were evaluated:

1. **`ast` (stdlib)** — Zero dependencies. Operates on the AST (Abstract Syntax
   Tree). Python-only. Sufficient for semantic extraction.

2. **`libcst`** — Concrete Syntax Tree. Preserves formatting and comments.
   Allows code rewriting. Python-only. Heavyweight for our use case.

3. **`tree-sitter`** — Universal parser supporting 50+ languages via native C
   extensions. Used by GitHub, Neovim, and Helix. Higher initial complexity.

## Decision

We adopt a **two-part strategy**:

1. **Use Python's `ast` stdlib** as the parsing engine for `PythonParser`.
   It is zero-dependency, battle-tested, and fully sufficient for semantic
   extraction (names, docstrings, imports, type annotations, line numbers).

2. **Define a language-agnostic `Parser` Protocol** in `parsers/protocols.py`.
   All parser implementations must satisfy this protocol. The Knowledge Graph
   and all downstream consumers depend only on the protocol, never on a
   specific parser implementation.

This means the parsing engine is an internal implementation detail. If a future
sprint requires multi-language support, a `tree-sitter`-backed parser can be
introduced without modifying the Knowledge Graph or any other domain component.

## Type Annotations

Type annotations (`ast.arg.annotation`, `ast.FunctionDef.returns`) are included
in the domain models from the start. They are available for free via `ast` and
will be essential for the Knowledge Graph to represent typed relationships.

## Consequences

Pros

- Zero new dependencies.
- The Parser Protocol ensures plugin-oriented extensibility (Architecture Principle 5).
- Downstream consumers are fully decoupled from the parsing library.
- Type annotations enrich the Knowledge Graph from the first sprint.

Cons

- `ast` is Python-only. Multi-language support will require a new parser
  implementation (e.g., `tree-sitter`) in a future sprint.
- `ast` does not preserve source formatting (acceptable, as we only need semantics).
