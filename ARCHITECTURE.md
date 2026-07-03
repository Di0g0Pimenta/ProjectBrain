# ProjectBrain Architecture

## Purpose

This document records the architectural decisions of ProjectBrain.

Every significant technical decision must be documented here before or immediately after implementation.

---

## Architecture Principles

### 1. Local First

ProjectBrain must work completely offline.

Cloud services are optional.

---

### 2. LLM Agnostic

ProjectBrain must support any OpenAI-compatible provider.

Examples:

- LM Studio
- Ollama
- OpenAI
- vLLM
- OpenRouter

---

### 3. Database as Source of Truth

SQLite is the canonical data source.

Markdown files are generated artifacts.

---

### 4. Incremental Analysis

Never analyze the whole project if only one file changed.

---

### 5. Plugin-Oriented

Parsers, providers and analyzers must be replaceable.

---

### 6. Human Readable Memory

Generated documentation should always be understandable by humans.

---

### 7. Production Quality

Every feature should include:

- tests
- typing
- documentation
- logging