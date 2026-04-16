# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Dependency and environment management goes through `uv`:

```bash
# First-time setup
uv venv && source .venv/bin/activate
uv pip install -e .

# Start the MCP server (stdio transport — exits immediately if no client is attached to stdin)
uv run main.py

# Run all tests
uv run pytest

# Run a single test file / class / test
uv run pytest tests/test_document.py
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf
```

## Architecture

This is a FastMCP server that exposes document/utility functions as MCP tools to AI assistants. The structure is intentionally thin:

- `main.py` — constructs the `FastMCP("docs")` instance and registers tools via `mcp.tool()(fn)`. This is the single wiring point; a tool is NOT exposed to MCP clients until it is registered here, even if it exists in `tools/`.
- `tools/` — plain Python functions, one concern per module (`math.py`, `document.py`). Functions are written as regular callables (not decorated in place) so they can be imported for direct testing and registered separately in `main.py`.
- `tests/` — pytest suite that imports from `tools/` directly, bypassing MCP. Binary fixtures live in `tests/fixtures/` (e.g. `mcp_docs.docx`, `mcp_docs.pdf`).

Note: `tools/document.binary_document_to_markdown` exists and is tested but is **not currently registered** in `main.py`. Registering a new tool requires adding both the import and the `mcp.tool()(fn)` call.

## Conventions

- **Type annotations are required on every function parameter.** Also annotate return types where non-trivial. These types feed the pydantic/MCP tool schema (see `tools/math.py:add`), so missing annotations degrade what MCP clients see.

## Defining MCP Tools

From `README.md`, tools follow these conventions (see `tools/math.py:add` as the reference implementation):

- **Registration**: functions are registered in `main.py` via `mcp.tool()(my_function)` — do not use `@mcp.tool()` decorators at the definition site; keep tool functions decoupled from the server instance.
- **Parameter descriptions**: use `pydantic.Field(description=...)` on every parameter. These descriptions become part of the MCP tool schema shown to the client LLM, so they should explain the parameter's purpose, not just restate its name.
- **Docstrings** are the tool description surfaced to clients. They should include, in this order:
  1. A one-line summary as the first line.
  2. A detailed explanation of functionality.
  3. A "When to use" (and when not to use) section so the client LLM can decide whether the tool is appropriate.
  4. Usage examples showing expected input/output (doctest-style is the established pattern).
- Type-annotate return values — they participate in the generated tool schema.

## Runtime Behavior

The server uses stdio transport (`mcp.run()` with FastMCP defaults). Running `uv run main.py` without a connected MCP client produces no output and exits when stdin closes — this is expected and is not a failure. To exercise the server interactively, launch it from an MCP client (Claude Desktop, Claude Code via `claude mcp add`, etc.) rather than standalone.
