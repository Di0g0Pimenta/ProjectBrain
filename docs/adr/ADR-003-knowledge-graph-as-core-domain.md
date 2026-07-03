# ADR-003 — Knowledge Graph as the Core Domain

Status: Accepted

Date: 2026-07-03

## Context

Originally, the architecture was implicitly designed around SQLite as the central data entity. However, ProjectBrain is an application oriented towards knowledge extraction, not a traditional CRUD system. Continuing with a database-centric approach creates tightly coupled components and violates Domain-Driven Design (DDD) principles where the core domain should dictate the rules, independent of infrastructure.

## Decision

We adopt the **Knowledge Graph** as the Core Domain of ProjectBrain.

- SQLite and other storage mechanisms are demoted to infrastructure details (Persistence Layer).
- The core domain model consists exclusively of Graph entities (`Node`, `Edge`, etc.) and rules for code analysis.
- Input modules (e.g., `Scanner`, `Parser`) act as producers that extract information from the file system to feed the Graph.
- Output modules (e.g., `Markdown Exporter`, `LLM Integration`) act as consumers that read from the Graph.
- Each component will strictly adhere to the Single Responsibility Principle.

## Consequences

Pros

- True adherence to Domain-Driven Design.
- Flexibility: The database can be swapped or modified without touching the business rules.
- Testability: The Knowledge Graph can be tested entirely in memory without hitting the disk.
- Decoupling of the File System logic from the Database logic.

Cons

- Requires an additional layer of mapping (Repositories) to translate Domain Models into Persistence Models.
