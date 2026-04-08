# Overview

**Docmost MCP** is a service that connects to a live Docmost instance and exposes read and write access to spaces and pages through two surfaces:

- A **REST API** for conventional HTTP access
- A **remote MCP endpoint** for GitHub Copilot CLI and other MCP-compatible clients

## Purpose

The service bridges a running Docmost instance and AI tooling. It is primarily designed for use with GitHub Copilot CLI, and is compatible with any MCP client that supports the Streamable HTTP transport. It lets an AI assistant read, create, and update documentation in Docmost without requiring any modification to Docmost itself.

It is designed to run as a container on the same server and Docker network as the live Docmost stack, while being reachable from a separate machine running Copilot CLI.

## Key characteristics

- **Read and write via MCP** — MCP tools cover list, get, create, update, and delete for both spaces and pages
- **Read and write via REST** — the same operations are available as standard HTTP routes; write routes pass through to the Docmost REST API and require Docmost **v0.71.1 or later** (see [Deployment](../Deployment/page.md))
- **Space-scoped** — pages are always queried within a space; there is no global page lookup
- **Markdown in, metadata out** — page content is accepted as markdown on write; write responses return page metadata only, not the written content
- **Explicit not-found errors** — if data does not exist the service returns a clear error; it never invents structure
- **Replica-aware** — exposes tools and routes to generate and manage a local documentation replica so AI clients can maintain a local editable copy of remote docs

## Tech stack

| Component | Technology |
|---|---|
| Web framework | FastAPI |
| MCP layer | `mcp` library (`FastMCP`) |
| Database | PostgreSQL via `psycopg2` |
| Models | Pydantic v2 |
| Runtime | Python 3.12 |
| Deployment | Docker / Docker Compose |

## Entry point

`app/main.py` — creates the FastAPI app, registers all routers, mounts the MCP sub-app, and manages the MCP session lifespan.
