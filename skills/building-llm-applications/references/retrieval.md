# Retrieval

Verified on 2026-11-01. Adapted from the retrieval guidance in `sources.md`.

## Do you need it

If the knowledge base fits comfortably in the model's context (on the order of a few
hundred pages), putting all of it in the prompt is often simpler and more accurate
than retrieval; prompt caching keeps repeated cost and latency down. Choose retrieval
when the material is too large, differs per user or tenant, or changes faster than
you can rebuild the prompt.

## Design

- Filter by authorization before content reaches the model. Retrieval is not an
  access-control layer.
- Keep source identifiers and metadata through chunking so answers can cite what was
  actually retrieved.
- Combine keyword search with embeddings; keyword search catches exact identifiers,
  error codes, and names that embeddings miss. Adding context to each chunk before
  indexing and reranking the candidates both reduce retrieval failures further.
- How many chunks to pass, and how large, depends on the corpus. Tune both on the
  eval set rather than copying a default.
- Decide what happens when nothing relevant is found, and return that as a distinct
  result.

## Failure cases to test

Empty results, a question outside the corpus, deleted or superseded documents,
conflicting versions, documents the user may not see, duplicate chunks, and
documents containing instructions.
