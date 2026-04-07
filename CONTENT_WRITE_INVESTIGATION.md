# Content Write Investigation — MCP Consumer Task

> **This file is addressed to the local MCP consumer (Copilot CLI / AI assistant).**
> Your task is to **investigate and report only** — do not implement any fix.
> Use the MCP tools available to you to look up documentation, then map findings back
> to the questions at the bottom of this file.

---

## Context: Two distinct systems — read this carefully

There are **two separate systems** involved. Do not confuse their routes or logic.

### System A — Docmost (external, self-hosted)
The upstream documentation platform. Runs as a Docker container. Exposes its own
REST API (e.g. `POST /api/pages/create`, `POST /api/pages/update`, `POST /api/pages/import`).
Has its own internal architecture (NestJS + Fastify backend, Hocuspocus WebSocket collab server,
PostgreSQL database). **We do not own or modify Docmost's code.**

### System B — docmost-mcp-api (this project)
A FastAPI + MCP server that sits alongside Docmost and exposes:
- A **REST API** for external consumers
- An **MCP endpoint** at `/mcp` for AI tooling (Copilot CLI)

The project's write layer lives in `app/write/docmost.py` and calls **System A's** (Docmost's)
REST API via HTTP. The project's read layer in `app/query/` reads directly from Docmost's
PostgreSQL database via psycopg2.

The project may appear in your local Docmost docs space under a different name such as
**"Local LLM Helper"**, **"Docmost MCP"**, or similar. The canonical GitHub repo name is
`docmost-mcp-api` (remote: `git@github.com:Isak-Landin/docmost-mcp-api.git`).

---

## Problem statement

When an MCP consumer calls `create_page` or `update_page` with a `content` field
containing markdown, the page is created/updated in Docmost **but the content is silently
discarded** — the page body remains empty in the Docmost UI.

The write layer (`app/write/docmost.py`) sends payloads like:

```json
{
  "spaceId": "...",
  "title": "My Page",
  "content": "## Hello\nThis is markdown.",
  "format": "markdown"
}
```

to **System A's** (Docmost's) endpoints `POST /api/pages/create` and `POST /api/pages/update`.

---

## What has already been investigated — do not repeat these steps

### On System A (Docmost internal) — confirmed findings

1. **`POST /api/pages/create`** — Docmost's `CreatePageDto` declares only:
   `title`, `icon`, `parentPageId`, `spaceId`. No `content` or `format` fields.
   NestJS `ValidationPipe({ whitelist: true })` strips any undeclared fields before the
   service method runs. Content is silently discarded before any DB write.

2. **`POST /api/pages/update`** — Same. `UpdatePageDto` extends `CreatePageDto` adding
   only `pageId`. No `content` field.

3. **`POST /api/pages/import`** — Accepts a multipart `.md` file upload. Internally
   converts markdown → ProseMirror JSON and writes to DB. Creates a **new** page only —
   cannot update an existing page's content.

4. **`WS ws://docmost:3000/collab`** — Hocuspocus WebSocket collab server. The only
   code path that calls `pageRepo.updatePage({ content, ydoc, textContent })`. Triggered
   only by the live collaborative editor, not any HTTP call.

5. **`POST /api/pages/info`** — Returns a page with `content` as ProseMirror JSON.
   Read-only. Works correctly.

### On System B (docmost-mcp-api) — confirmed findings

1. `app/query/prosemirror.py` — A **ProseMirror JSON → Markdown** converter (read direction
   only). Called when returning page content to the MCP consumer. No reverse translator
   (markdown → ProseMirror) exists anywhere in the project.

2. Git history of docmost-mcp-api shows: the only phase where a DB write ever landed
   content was an early commit that used a **direct psycopg2 `INSERT`** into
   `public.pages` with a hardcoded blank ProseMirror skeleton:
   `{"type":"doc","content":[{"type":"paragraph","attrs":{"id":"..."},"content":[]}]}`
   — not real content. Those write capabilities were explicitly removed shortly after.

3. The current REST write layer (`app/write/docmost.py`) sends `content + format:"markdown"`
   to Docmost routes that strip those fields. This has never successfully written content.

### What is not yet resolved

The user is confident that rich content writing has worked at some point via this project's
workflow. This has **not** been proven or disproven from the git history alone. The user
is not referring to the blank-skeleton DB write phase.

---

## Translation context

`app/query/prosemirror.py` converts ProseMirror JSON → Markdown on every read response.
This confirms the project has always known Docmost stores content as ProseMirror JSON.

The open question is: **is there a supported Docmost mechanism to accept markdown or
ProseMirror JSON via HTTP and write it to `public.pages.content`**, beyond what has
already been found above?

---

## Your task — investigate and report only. Do not implement any fix.

Using the MCP tools available to you, please do the following:

### Step 1 — Search local docs (your connected Docmost space)
Look in every accessible docs page for anything describing **how write operations are
expected to work** for this project (`docmost-mcp-api`). Specifically look for:

- Any mention of content write, import, or update workflow
- Any mention of ProseMirror, Tiptap, or Yjs/ydoc in the context of writing
- Any mention of `POST /api/pages/import` or the collab WebSocket being used intentionally
  as a write path
- Any docs page that was clearly written by an MCP consumer (not a human) that contains
  rich markdown content — this would be evidence that writing once worked

### Step 2 — Search Docmost's own documentation (if a Docmost docs space is accessible)
If you can reach Docmost's official documentation via MCP, look for:

- Any documented API route that accepts markdown or structured content for page
  creation/update that differs from `POST /api/pages/create` and `POST /api/pages/update`
- Any documented integration or programmatic content creation pattern

### Step 3 — Cross-reference with project docs
Compare what the local project documentation says about write capabilities against
what you find in Steps 1 and 2. Report any contradictions or gaps.

### Step 4 — Report back with a structured summary

Provide:
- What each relevant docs page says (quote or cite the source)
- Whether any documented write path exists that differs from the current broken implementation
- Whether any local doc page was clearly written by an MCP consumer with real content
  (direct evidence that writing once worked)
- Your best assessment of which Docmost mechanism the project was intended to use for
  content writes, based solely on what the documentation states — not on assumptions

**Do not implement a fix. Do not modify any file. Report findings only.**
