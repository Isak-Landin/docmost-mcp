# Content Write Debug — Local Iterative Test

> **This file is addressed to the local MCP consumer (Copilot CLI / AI assistant).**
> Follow each step in order. **Halt after every step and wait for explicit user
> confirmation before proceeding.** Do not skip ahead. Do not modify any project
> file unless a step explicitly asks you to.

---

## Background: the known problem

The project (`docmost-mcp-api`) has a write layer (`app/write/docmost.py`) that calls
the Docmost REST API to create and update pages. It sends `content` and `format: "markdown"`
in the request body. Pages are created/updated successfully — but the content body is always
empty in the Docmost UI.

Two explanations have been tested against the live remote Docmost instance and neither resolved it:
1. ValidationPipe in Docmost stripping undeclared fields from the DTO — suspected but not fully proven
2. Collab gateway debounce (10–45 s) causing a stale read-back — tested with 45 s wait, still blank

The goal of this session is to reproduce the problem against a **fresh isolated local Docmost
instance** and identify exactly where content is lost, so we can fix it.

---

## Step 1 — Spin up a local isolated Docmost instance

Create a `docker-compose.local-test.yml` file **in the project root** of `docmost-mcp-api`
with a fresh Docmost stack on ports that do not conflict with the production stack.
Use port **3100** for the Docmost app and **5533** for its PostgreSQL.
Use an isolated Docker network named `docmost_local_test_net`.

The compose file must include:
- `docmost` service (image: `docmost/docmost:latest`, port 3100:3000)
- `db` service (image: `postgres:16-alpine`, port 5533:5432)
- `redis` service (image: `redis:7.2-alpine`, internal only)
- A named network `docmost_local_test_net` (bridge, not external)

Use these fixed values for the local test database:
- DB name: `docmost`
- DB user: `docmost`
- DB password: `localtestpass`
- Docmost `APP_SECRET`: `local-test-secret-not-for-production`
- Docmost `DATABASE_URL`: `postgresql://docmost:localtestpass@db:5432/docmost`
- Docmost `REDIS_URL`: `redis://redis:6379`

Start the stack with:
```
docker compose -f docker-compose.local-test.yml up -d
```

Then report:
- Whether all three containers started successfully
- The URL where the Docmost UI is reachable from localhost (should be `http://localhost:3100`)

**HALT. Wait for user to confirm they can reach the Docmost UI at http://localhost:3100 before proceeding.**

---

## Step 2 — User creates account

Ask the user to:
1. Open `http://localhost:3100` in a browser
2. Complete the Docmost setup wizard (create workspace and admin account)
3. Confirm the email address and password they used

**HALT. Do not proceed until user explicitly confirms the account is created and they are logged in.**

---

## Step 3 — Configure the MCP container to point at the local test instance

Create a `.env.local-test` file in the project root by copying `.env` and changing
only the values that must differ for the local test. The following values must be set
to target the local test instance:

```
DOCMOST_APP_URL=http://docmost:3000
DOCMOST_DB_HOST=db
DOCMOST_DB_PORT=5432
DOCMOST_DB_NAME=docmost
DOCMOST_DB_USER=docmost
DOCMOST_DB_PASSWORD=localtestpass
DOCMOST_NETWORK_NAME=docmost_local_test_net
EXTERNAL_PORT=8198
LISTEN_PORT=8198
```

For `DOCMOST_USER_EMAIL` and `DOCMOST_USER_PASSWORD`: ask the user to provide the
credentials they just created in Step 2, then write them into `.env.local-test`.

Do **not** set `DOCMOST_DB_URL` — let it derive from the individual components above.

Then start the MCP container against the local test instance:
```
docker compose -f docker-compose.local-test.yml \
  -f docker-compose.yml \
  --env-file .env.local-test \
  --project-name docmost-mcp-local-test \
  up -d docmost-mcp
```

Verify the MCP container started and is reachable:
```
curl -s http://localhost:8198/health
```

Report the health check response.

**HALT. Wait for user to confirm they want to proceed with write tests.**

---

## Step 4 — Test: create a space

Using the MCP tool `create_space` (or direct REST call to `POST /spaces` on
`http://localhost:8198`), create a test space:
- name: `Write Test`
- slug: `write-test`

Report:
- The full response from the API
- Whether the space appears in the Docmost UI at `http://localhost:3100`

**HALT. Wait for user to confirm whether the space is visible in the UI.**

---

## Step 5 — Test: create a page with content

Using the MCP tool `create_page` (or direct REST call to `POST /spaces/{space_id}/pages`
on `http://localhost:8198`), create a page with:
- title: `Write Test Page`
- content: `## Hello\n\nThis is a test paragraph.\n\n- item one\n- item two`

Report:
- The full raw response from the API including the `content` field value
- Whether the page appears in the Docmost UI
- Whether the page body shows any content in the Docmost UI, or is blank

**HALT. Wait for user to confirm what they see in the Docmost UI for this page.**

---

## Step 6 — Test: update the page with content

Using `update_page` (or direct REST call to `PUT /spaces/{space_id}/pages/{page_id}`),
update the page created in Step 5 with:
- content: `## Updated\n\nThis content was written by an update call.`
- operation: `replace`

After the call:
1. Immediately read back the page via `get_page` and report the `content` field value
2. Wait 60 seconds
3. Read back the page again and report the `content` field value
4. Ask the user to check the Docmost UI and report what they see

Report all four data points together.

**HALT. Wait for user to report what they see and confirm whether content is present.**

---

## Step 7 — Diagnose and report

Based on the results of Steps 5 and 6, report the following:

1. **Create path**: did `content` survive the create call? (Check the create response body
   and what the UI shows immediately after creation.)

2. **Update path**: did `content` survive the update call after 60 s?

3. **If content is missing in both**: this confirms ValidationPipe is stripping the fields.
   Check the running local Docmost container's compiled source directly:
   ```
   docker exec <docmost-container-name> \
     node -e "const f=require('/app/apps/server/dist/core/page/dto/create-page.dto.js'); \
     const keys=Object.getOwnPropertyNames(f.CreatePageDto.prototype); \
     console.log(JSON.stringify(keys));"
   ```
   Report the full output. This will confirm which fields the DTO declares.

4. **If content is present**: report the exact payload that succeeded, so the production
   write path can be aligned to match.

5. **Propose the fix**: based only on what you have observed and confirmed above —
   not from assumptions — state the single most targeted change needed to make content
   writes work, or confirm that a different mechanism (e.g., `POST /api/pages/import`)
   is required.

**HALT. Present findings to user and await decision on next action.**

---

## Cleanup (only when user instructs)

When the user says to clean up:
```
docker compose -f docker-compose.local-test.yml \
  --project-name docmost-mcp-local-test down -v
```
Then delete `docker-compose.local-test.yml` and `.env.local-test`.
