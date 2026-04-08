# Architecture

## Layer overview

```
Copilot CLI / MCP client
        │
        │  HTTPS  (remote machine)
        ▼
┌─────────────────────────────────────────────────────┐
│  docmost-mcp container  (same server as Docmost)    │
│                                                     │
│  FastAPI app  (app/main.py)                         │
│    ├── /health          → routers/health.py         │
│    ├── /spaces/*        → routers/spaces.py         │
│    ├── /spaces/*/pages* → routers/pages.py          │
│    ├── /replica/*       → routers/replica.py        │
│    └── /mcp             → FastMCP sub-app           │
│                                                     │
│  MCP layer  (app/mcp_server.py)                     │
│    ├── read tools (list, get, tree, replica)        │
│    └── write tools (create, update, delete)         │
│                                                     │
│  Query logic  (app/query/docmost.py)                │
│    └── space + page queries, tree builder           │
│                                                     │
│  Write logic  (app/write/docmost.py)                │
│    └── create, update, delete via Docmost REST API  │
│                                                     │
│  Replica logic  (app/query/replica.py)              │
│    └── standards, name resolver, structure builder  │
│                                                     │
│  DB layer  (app/query/db.py)                        │
│    └── psycopg2 + RealDictCursor, context manager   │
└──────────────┬──────────────────────────────────────┘
               │  TCP / PostgreSQL  (Docker network)
               ▼
        Docmost PostgreSQL container
```

## Module responsibilities

| Module | Responsibility |
|---|---|
| `app/main.py` | FastAPI app factory, router registration, MCP session lifespan |
| `app/mcp_server.py` | FastMCP instance, MCP tool definitions, transport security config |
| `app/models.py` | All Pydantic input and output models |
| `app/query/docmost.py` | SQL queries for spaces and pages, tree builder, error types |
| `app/query/replica.py` | Replica standards, directory name resolver, replica structure builder |
| `app/query/db.py` | Database DSN construction, `get_conn()` context manager |
| `app/query/text_utils.py` | `reformat_text()` - collapses Docmost storage noise in raw content |
| `app/query/prosemirror.py` | ProseMirror JSON to markdown conversion |
| `app/write/docmost.py` | Docmost REST API client for create, update, delete operations |
| `app/query/routers/health.py` | `GET /health` |
| `app/query/routers/spaces.py` | `GET /spaces`, `/spaces/{id}`, `/spaces/{id}/tree` |
| `app/query/routers/pages.py` | `GET /spaces/{id}/pages`, `/spaces/{id}/pages/{page_id}` |
| `app/query/routers/replica.py` | `GET /replica/standards`, `/replica/resolve-directory-name`, `/spaces/{id}/replica-structure` |
| `app/write/routers/spaces.py` | `POST /spaces`, `DELETE /spaces/{id}` |
| `app/write/routers/pages.py` | `POST /spaces/{id}/pages`, `PUT /spaces/{id}/pages/{id}`, `DELETE /spaces/{id}/pages/{id}` |

## Request flow (REST)

1. FastAPI router handler receives request
2. Read handlers call the corresponding function in `app/query/docmost.py` (or `app/query/replica.py` for replica routes)
3. `docmost.py` opens a DB connection via `app/query/db.get_conn()`, executes SQL, closes connection
4. Row data is mapped to Pydantic models
5. Text content passes through `app/query/text_utils.reformat_text()` before model construction
6. Write handlers call `app/write/docmost.py` which authenticates and forwards to the Docmost REST API
7. Pydantic model is returned as JSON

## Request flow (MCP)

1. MCP client calls a tool on the `/mcp` endpoint
2. FastMCP dispatches to the matching tool function in `app/mcp_server.py`
3. Read tools delegate to `app/query/docmost.py` / `app/query/replica.py`
4. Write tools delegate to `app/write/docmost.py` via the Docmost REST API
5. Database errors become `ToolError`, not-found errors become `ToolError`
6. Result is returned as a JSON MCP response

## Networking

The container must be on the same Docker network as Docmost (`docmost_default`). The PostgreSQL container is reachable inside that network at the hostname set by `DOCMOST_DB_HOST`.

The MCP endpoint is exposed externally (via `EXTERNAL_PORT`, default 8099). Copilot CLI on a remote machine connects to `https://<host>:<port>/mcp`.
