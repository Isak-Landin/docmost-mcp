# Docmost Database API

A FastAPI REST API that connects directly to the live Docmost PostgreSQL database
and exposes spaces and pages as stable, readable API responses.

This is a data API for downstream consumers such as documentation tooling,
AI models, or other integrations that need live Docmost content.

---

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/spaces` | List all spaces |
| `GET` | `/spaces/{space_id}` | Get a single space |
| `GET` | `/spaces/{space_id}/pages` | List all pages in a space |
| `POST` | `/spaces/{space_id}/pages` | Create a page in a space |
| `GET` | `/spaces/{space_id}/pages/{page_id}` | Get a single page |
| `PATCH` | `/spaces/{space_id}/pages/{page_id}` | Update a page |
| `DELETE` | `/spaces/{space_id}/pages/{page_id}` | Soft-delete a page |

Pages are always scoped to their space. A page endpoint always requires `space_id`
and verifies that the page belongs to that space.

Text content is returned normalized: repeated newline runs and repeated `+`
storage noise are collapsed before the response is sent.

Interactive API docs are available at `/docs` (Swagger UI) when the service is running.

---

## Data Model

**Spaces** — `public.spaces`

Columns exposed: `id`, `name`, `description`, `slug`, `visibility`, `default_role`,
`creator_id`, `workspace_id`, `created_at`, `updated_at`.

**Pages** — `public.pages`

Columns exposed: `id`, `slug_id`, `title`, `icon`, `position`, `parent_page_id`,
`creator_id`, `last_updated_by_id`, `space_id`, `workspace_id`, `is_locked`,
`text_content` (normalized), `created_at`, `updated_at`.

Pages carry a `parent_page_id` reference for reconstructing page hierarchy.
Deletion is soft: `deleted_at` is set; the row is not removed from the database.

---

## Configuration

Copy `env.example` to `.env` and fill in your Docmost database credentials.

```bash
cp env.example .env
# edit DOCMOST_DB_* values
```

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCMOST_DB_URL` | — | Full DSN (takes priority if set) |
| `DOCMOST_DB_HOST` | `db` | PostgreSQL host |
| `DOCMOST_DB_PORT` | `5432` | PostgreSQL port |
| `DOCMOST_DB_NAME` | `docmost` | Database name |
| `DOCMOST_DB_USER` | `docmost` | Database user |
| `DOCMOST_DB_PASSWORD` | — | Database password |
| `LISTEN_HOST` | `0.0.0.0` | Bind host |
| `LISTEN_PORT` | `8099` | Bind port |
| `EXTERNAL_PORT` | `8099` | Host-side exposed port |

---

## Running with Docker

The service joins the `docmost_default` external Docker network to reach
the Docmost PostgreSQL container directly.

```bash
docker compose up --build -d
```

---

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## License

See `LICENSE`.
