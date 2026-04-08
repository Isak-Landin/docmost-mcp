# Spaces

## `GET /spaces`

Returns all non-deleted spaces from the live Docmost database, ordered by creation date.

Use this first when you need to identify a space UUID before calling any page routes.

### Response model: `list[SpaceOut]`

### Errors

| Code | Reason |
|---|---|
| `503` | Database connection failed |

---

## `GET /spaces/{space_id}`

Returns a single space by its UUID.

### Path parameters

| Parameter | Type | Description |
|---|---|---|
| `space_id` | UUID | Space UUID from `GET /spaces` |

### Response model: `SpaceOut`

### Errors

| Code | Reason |
|---|---|
| `404` | Space not found or deleted |
| `503` | Database connection failed |

---

## `GET /spaces/{space_id}/tree`

Returns the page hierarchy for one space as a fully nested tree built from `parent_page_id`.

Use this when you need to understand documentation structure without reconstructing parent-child relationships client-side.

### Path parameters

| Parameter | Type | Description |
|---|---|---|
| `space_id` | UUID | Space UUID |

### Response model: `SpaceTreeOut`

The response contains:
- `space` - `SpaceSummaryOut` (id, name, slug)
- `root_pages` - top-level pages, each with fully nested `children`
- `orphan_pages` - pages whose parent is missing or otherwise unreachable

### Tree construction rules

- Pages with `parent_page_id = null` become root pages
- Pages whose `parent_page_id` does not match any page in the space become orphan root pages
- Cycle detection is applied; cyclic references are broken and the looping child is excluded
- Pages are sorted by `position` (positioned before un-positioned), then by `created_at`

### Errors

| Code | Reason |
|---|---|
| `404` | Space not found or deleted |
| `503` | Database connection failed |

### Implementation

`app/query/docmost.get_space_tree()` builds the tree in-memory after fetching all page rows for the space in a single SQL query.

---

## `POST /spaces`

Creates a new Docmost space. Authentication is handled transparently.

### Request body: `SpaceCreateIn`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Display name (2-100 characters) |
| `slug` | string | yes | Alphanumeric URL identifier, no spaces or dashes (2-100 chars) |
| `description` | string | no | Optional plain-text description |

### Response model: `SpaceOut`

### Errors

| Code | Reason |
|---|---|
| `400` | Validation error or slug/name already taken |
| `401` | Docmost credentials invalid |

---

## `DELETE /spaces/{space_id}`

Permanently deletes a space and all its pages. This is irreversible. Authentication is handled transparently.

### Path parameters

| Parameter | Type | Description |
|---|---|---|
| `space_id` | UUID | Space UUID |

### Response model: `DeletedOut`

### Errors

| Code | Reason |
|---|---|
| `401` | Docmost credentials invalid |
| `404` | Space not found |
