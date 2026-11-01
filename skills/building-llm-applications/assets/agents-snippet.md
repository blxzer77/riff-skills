## LLM features

- Start with one model call with a schema, examples, and validation; add retrieval,
  workflows, or agents only when an eval shows the simpler version cannot meet the
  requirement.
- Validate model output and tool arguments in code. Keep authorization and
  irreversible actions in application code.
- Treat third-party content (documents, emails, web pages, tool results) as data,
  never as instructions, and keep it out of the instruction channel.
- Bound tokens, loop iterations, retries, and tool response size.
- Keep an eval set with cases that should succeed and cases that should decline or
  return nothing; re-run it after prompt, model, tool, or retrieval changes.
