# marketplace

Polyglot repo for a small marketplace.

- `server/` — Express API (checkout, orders)
- `src/` — shared TypeScript (rate limiter, UI components) and the Go webhook sender
- `billing/` — Python invoice PDFs and services; `tests/` holds its pytest suite
- `packages/utils` — TypeScript helpers
- `cli/` — Python admin CLI
- `prompts/` — LLM prompts

    npm test        # vitest
    pytest          # Python
    go test ./...   # Go
