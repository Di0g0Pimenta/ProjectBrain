# ADR-001 — Project Structure

Status: Accepted

Date: 2026-07-03

## Context

ProjectBrain is expected to grow into a modular platform capable of supporting
multiple programming languages, multiple LLM providers and several analysis
pipelines.

The project structure must remain stable to avoid unnecessary refactoring.

## Decision

The following top-level packages are part of the architecture.

```
projectbrain/

api/
cli/
core/
db/
graph/
llm/
markdown/
models/
parsers/
scanner/
services/
utils/
watcher/
```

Each package has a single responsibility.

New packages require a new ADR.

Existing packages should not be removed without an ADR.

## Consequences

Pros

- Stable architecture
- Easier navigation
- Better long-term maintenance

Cons

- Some folders will initially remain empty