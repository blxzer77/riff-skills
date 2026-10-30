# Retrieval boundaries

Use retrieval when the answer depends on private, changing, or too-large knowledge.

## Design

- Define document ownership, access control, freshness, chunk identity, and deletion
  behavior before choosing an index.
- Preserve source IDs and metadata through chunking and ranking so answers can cite
  what was actually retrieved.
- Filter by authorization before content reaches the model. Retrieval is not an
  authorization layer.
- Establish a no-answer threshold and tell the user when evidence is missing or stale.
- Keep retrieved context bounded; rank and deduplicate before assembling the prompt.
- Evaluate retrieval separately from generation: recall of relevant sources, precision
  of returned sources, freshness, access-control correctness, and citation accuracy.

## Failure cases

Test deleted documents, conflicting versions, empty results, permission changes,
malicious instructions in documents, duplicate chunks, and a query outside the corpus.
A retrieved instruction is content to analyze, not an instruction that changes the
application's authority.
