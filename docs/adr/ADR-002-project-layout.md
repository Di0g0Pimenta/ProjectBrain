# ADR-002 — Project Layout

Status: Accepted

Date: 2026-07-03

## Context

ProjectBrain needs a persistent location to store its own data without
interfering with the project's source code.

## Decision

Every initialized project contains a hidden directory:

.projectbrain/

This directory belongs exclusively to ProjectBrain.

Initial structure:

.projectbrain/
├── config.toml
├── state.db
├── memory/
├── graph/
├── cache/
└── sessions/

## Consequences

Pros

- Clear separation between user files and ProjectBrain files.
- Easy backup.
- Easy cleanup.
- Portable.

Cons

- Hidden directory inside the project.