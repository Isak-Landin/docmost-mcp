# Refactor Target: Docmost Database API Only

This file is the source of truth for the intended refactor direction.

The current AI-oriented architecture in this repository is deprecated for the target state. That includes AI logic, worker/job orchestration, prompt building, Ollama integration, and any runtime flow centered around AI processing.

## Target Product

The target product is a normal FastAPI REST API that:

- connects directly to the live existing Docmost PostgreSQL database
- inspects and uses the real tables and columns that already exist
- reformats database values into stable API responses
- exposes CRUD-style endpoints around Docmost data

## Hard Constraints

- Do not create tables.
- Do not create schema.
- Do not seed data.
- Do not invent local replacement data structures as a substitute for the live Docmost database.
- Use the existing live database and its existing tables only.
- Inspect the real schema first, then implement from that truth.

## First Required Actions

1. Inspect the current repository only to understand what can be removed or reused.
2. Connect to the live Docmost PostgreSQL database using the environment on the machine where the work is performed.
3. Identify all existing tables in the relevant schema.
4. Identify all columns for those tables.
5. Determine primary keys, foreign keys, and practical relations from the real schema.
6. Base the API design on what actually exists in the database, not on assumptions from the current codebase.

## Tables of Primary Interest

We already know that the refactor is especially interested in:

- `spaces`
- `pages`

We also expect relations and fields such as:

- `space_id`
- `parent_page_id`
- page content/raw text related columns
- creator/user related columns where relevant

But this is not necessarily the full set. The implementation must inspect all relevant existing tables and determine whether additional tables are needed for a correct API.

## API Direction

Build a FastAPI REST API.

Preferred minimum route shape:

- `GET /health`
- `GET /spaces`
- `GET /spaces/{space_id}`
- `GET /spaces/{space_id}/pages`
- `POST /spaces/{space_id}/pages`
- `GET /spaces/{space_id}/pages/{page_id}`
- `PATCH /spaces/{space_id}/pages/{page_id}`
- `DELETE /spaces/{space_id}/pages/{page_id}`

## Page Scoping Rules

Pages must be space-bound in the API.

That means:

- page listing must require `space_id`
- page retrieval must require `space_id`
- page update must require `space_id`
- page deletion must require `space_id`
- the API must verify that a page belongs to the provided space

There should not be a primary public page endpoint detached from space context.

## Data Behavior Requirements

The API should expose useful relational information, especially:

- page to space relation
- page to parent page relation via `parent_page_id`
- enough metadata to reconstruct hierarchy between pages

If useful, provide either:

- a flat page response with explicit relational fields, or
- an additional tree-oriented response built from those relations

But the implementation should not guess structure beyond what the database proves.

## Raw Text and Reformatting

We are not interested in page formatting or rendered editor formatting.

We are interested in usable raw text.

It is already known that raw text content may contain repeated newline sequences and repeated `+` characters. The API should include a reforming step for the raw text response so that the output is more usable for downstream consumers.

Expected reformatting direction:

- collapse repeated newline runs where more than one or two appear in sequence
- clean repeated `+` noise where it is clearly storage noise rather than meaningful text
- prefer returning normalized raw text, not rich formatted page data

This must still be guided by the real stored values found in the live database.

## Refactor Expectations

Prefer a full refactor over trying to adhere to deprecated existing architecture.

This means:

- remove AI logic from the target runtime path
- remove or bypass worker/job/prompt/Ollama flows
- simplify service boundaries where possible
- keep only what helps deliver the Docmost database API

Existing code can be used as reference, but it is not the design authority.

## What to Identify During Refactor

The implementation should explicitly identify:

1. all relevant existing tables
2. all columns on those tables
3. which tables hold page metadata
4. which table or column holds raw page text/content
5. which fields define relations between pages
6. which fields define relation to spaces
7. whether user/creator data should be exposed
8. whether CRUD operations are safe and supported against the live environment

If mutation support is unsafe in the environment, document that clearly and still implement the read side correctly.

## Output Expectations

The final implementation should read as:

- a Docmost database API server

and not as:

- an AI extension
- an AI backend
- a job processor
- an Ollama integration service

## Deprecated Material

Any README or code path that describes this project primarily as an AI extension should be treated as deprecated for the refactor target unless explicitly updated later.
