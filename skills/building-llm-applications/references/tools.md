# Designing tools for a model

Verified on 2026-11-01. Adapted from the tool-design guidance in `sources.md`.

A tool is an interface for a non-deterministic caller. Design it the way you would
for a capable new colleague who reads only the description.

## Which tools to build

- Start from the tasks users bring, not from the API. A `search_contacts(query)` or
  `send_message(contact, text)` tool beats wrapping `list_contacts` and making the
  model page through everyone.
- Consolidate related operations. One tool with an `action` parameter, or one tool
  that performs a common multi-step task, is easier to choose correctly than many
  near-duplicates. Overlapping tools are a common cause of wrong calls.
- Group tools by service or resource in their names (`billing_refund`,
  `billing_lookup`) so similar tools are distinguishable.

## Descriptions and parameters

- Write a detailed description: what the tool does, when to use it and when not to,
  what each parameter means and its format, side effects, and what it returns.
  Several sentences per tool is normal; a one-line description is the most common
  cause of misuse.
- Name parameters unambiguously (`user_id`, not `user`; `start_date_iso`, not
  `date`). Make wrong calls hard: absolute paths instead of relative, enums instead
  of free text, required fields for anything the tool cannot guess.
- Validate arguments in code before executing, and authorize the action there.

## Responses

- Return what the model needs to decide its next step, in words it can use: names,
  titles, and short excerpts rather than opaque internal identifiers, image URLs, or
  MIME types. Keep an identifier only when a later call needs it.
- Bound response size by default: paginate, filter, or truncate, and say in the
  response when results were cut and how to get more. Offer a concise and a detailed
  format if both are useful.
- Make errors specific and actionable ("`start_date_iso` must be YYYY-MM-DD; got
  `03/04`") rather than stack traces or bare status codes.

## Checking tools

Run realistic multi-step tasks against the tools and read the transcripts. Repeated
redundant calls suggest weak pagination or filtering; repeated invalid-argument
errors suggest an unclear description. Fix the tool before adding prompt rules.
