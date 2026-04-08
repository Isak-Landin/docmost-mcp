# Release

## v1.0.0

First stable release of Docmost MCP API.

### Distribution

The service is published as a Docker image on GitHub Container Registry:

```
ghcr.io/isak-landin/docmost-mcp-api:1.0.0
ghcr.io/isak-landin/docmost-mcp-api:latest
```

Pull and run using a `docker-compose.yml` pointing at the image - no clone or build step required.

Source is available at: https://github.com/Isak-Landin/docmost-mcp-api

### What is included

- REST API for Docmost: spaces, pages, children, create, update, delete
- MCP server exposing all REST operations as callable tools
- Markdown in, metadata out - write responses return page identity and metadata; content is not echoed back
- Auth handled transparently on every request
- Fully environment-driven - no hardcoded values
- Docker Compose setup with shared external network support
- GitHub Actions workflow publishing image to GHCR on release
- Hardened MCP server instructions: all write tool IDs must originate from live tool responses, never inferred or invented

### Known characteristics

Context window usage is high per session when used through an AI coding assistant. A full workflow (refactoring, re-analysing, local replica management, remote sync) typically consumes 80 KB to 200 KB of context for a tested case with 25 documentation files. Translated to approximately 3.2k - 8k tokens per documentation page.

### Limitations

- `update_page` write confirmation does not include content - the response returns metadata only. Use `get_page` if content verification is needed after an update.
- Space slugs must be alphanumeric, no dashes or spaces (Docmost constraint)
