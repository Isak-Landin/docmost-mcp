# Docmost Read-Only API and MCP Server

This service connects directly to the live Docmost PostgreSQL database and exposes
the data through two read-only integration surfaces:

| Surface | Path | Purpose |
|--------|------|---------|
| REST API | `/health`, `/spaces`, `/spaces/{space_id}`, `/spaces/{space_id}/pages`, `/spaces/{space_id}/pages/{page_id}` | Conventional HTTP access for spaces and pages |
| MCP | `/mcp` | Remote Model Context Protocol endpoint for Copilot and other MCP clients |

It is intended to run as a container on the same server/network as the live
Docmost stack while remaining reachable from remote Copilot clients.

## Read-only contract

- No create, update, move, or delete operations are exposed.
- Pages are always scoped to their space.
- `text_content` is returned as normalized plain text.
- Repeated newline runs and repeated `+` storage noise are collapsed before data is returned.

Interactive REST API docs are available at `/docs` when the service is running.

## REST routes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/spaces` | List all non-deleted spaces |
| `GET` | `/spaces/{space_id}` | Get one non-deleted space |
| `GET` | `/spaces/{space_id}/pages` | List all non-deleted pages in a space |
| `GET` | `/spaces/{space_id}/pages/{page_id}` | Get one non-deleted page in its space |

## MCP endpoint

The service exposes a remote streamable HTTP MCP endpoint at:

```text
/mcp
```

The MCP server is container-owned and ships with built-in read-only instructions.
It exposes these tools:

| Tool | Description |
|------|-------------|
| `list_spaces` | List all non-deleted spaces |
| `get_space` | Get one space by UUID |
| `list_pages` | List pages in a space |
| `get_page` | Get one page by UUID inside a space |

The MCP instructions enforced by the server are:

```text
This server is strictly read-only.
Never create, update, move, or delete spaces or pages.
Only use the provided Docmost tools to inspect spaces and pages.
Pages are always space-scoped: use space_id together with page_id.
Treat text_content as normalized plain text, not authoritative rich formatting.
If requested data is missing, report that explicitly instead of inferring it.
```

## Copilot CLI setup

Because the MCP endpoint is hosted by the deployed container, your Copilot CLI
machine does not need local wrapper logic. It only needs network access to the
published `/mcp` URL.

### Interactive setup

In Copilot CLI, run:

```text
/mcp add
```

Configure a remote HTTP MCP server that points at your deployed service, for example:

```text
https://your-docmost-host.example.com/mcp
```

Allow only these tools:

```text
list_spaces
get_space
list_pages
get_page
```

### Manual `mcp-config.json` example

Copilot CLI stores MCP configuration in `~/.copilot/mcp-config.json`.

```json
{
  "mcpServers": {
    "docmost-readonly": {
      "type": "http",
      "url": "https://your-docmost-host.example.com/mcp",
      "tools": ["list_spaces", "get_space", "list_pages", "get_page"]
    }
  }
}
```

If your Copilot CLI runs on a different machine than the Docmost host, make sure
the service is reachable from that machine through your chosen port, proxy, and TLS setup.

## Data model

**Spaces** - `public.spaces`

Columns exposed: `id`, `name`, `description`, `slug`, `visibility`, `default_role`,
`creator_id`, `workspace_id`, `created_at`, `updated_at`.

**Pages** - `public.pages`

Columns exposed: `id`, `slug_id`, `title`, `icon`, `position`, `parent_page_id`,
`creator_id`, `last_updated_by_id`, `space_id`, `workspace_id`, `is_locked`,
`text_content` (normalized), `created_at`, `updated_at`.

Pages carry a `parent_page_id` reference for reconstructing hierarchy.
Deletion is soft in Docmost: `deleted_at` is set and deleted rows are excluded.

## Configuration

Copy `env.example` to `.env` and fill in your Docmost database credentials.

```bash
cp env.example .env
# edit DOCMOST_DB_* values
```

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCMOST_DB_URL` | - | Full DSN, takes priority if set |
| `DOCMOST_DB_HOST` | `db` | PostgreSQL host reachable from the container |
| `DOCMOST_DB_PORT` | `5432` | PostgreSQL port |
| `DOCMOST_DB_NAME` | `docmost` | Database name |
| `DOCMOST_DB_USER` | `docmost` | Database user |
| `DOCMOST_DB_PASSWORD` | - | Database password |
| `LISTEN_HOST` | `0.0.0.0` | Bind host for both REST and MCP |
| `LISTEN_PORT` | `8099` | Container bind port for both REST and MCP |
| `EXTERNAL_PORT` | `8099` | Published host port |

## Running with Docker

The service joins the `docmost_default` external Docker network to reach the
live Docmost PostgreSQL container directly.

```bash
docker compose up --build -d
```

After startup:

- REST health check: `http://HOST:8099/health`
- REST docs: `http://HOST:8099/docs`
- MCP endpoint: `http://HOST:8099/mcp`

## Running locally

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## License

See `LICENSE`.
