# Not findings

Verified on 2026-11-01. Consolidated from the false-positive lists in the review
designs in `sources.md`. Drop a candidate that falls into one of these categories
unless a project rule that applies to the file explicitly requires otherwise.

## Any review

- Defects whose source, sink, and guards are unchanged by this diff. List them as
  pre-existing, never as findings.
- Code that looks wrong but is correct once the caller, type, or invariant is read.
- Style, naming, formatting, and refactoring preferences.
- Issues a linter or type checker in the project's CI would report.
- General quality concerns such as missing tests or missing documentation, unless a
  project rule requires them.
- A project rule that the code explicitly silences, for example with an ignore
  comment, where the silencing is visible in the diff.
- Problems that need inputs, state, or configuration the change does not create.
- Pedantic points a senior engineer on the project would not raise.

## Security reviews

- Denial of service, resource exhaustion, missing rate limits, and regular
  expression denial of service.
- Missing hardening or defense in depth, when no concrete exploit path exists.
- Theoretical races or timing attacks that are not concretely exploitable.
- Outdated dependencies; those belong to dependency scanning.
- Memory-safety issues in memory-safe languages.
- Code that only runs in tests.
- Unsanitized user input written to logs (log spoofing). Logging secrets, passwords,
  or personal data is still a finding.
- Server-side request forgery where the attacker controls only the path. It is a
  finding when they control the host or protocol.
- User content included in model prompts.
- Untrusted content compiled into a regular expression.
- Findings in documentation files.
- Missing audit logs.
- Values from environment variables, CLI flags, or deployment configuration; an
  attacker who can set those already controls the process.
- Missing authorization in client-side code; the server must enforce it.
- Cross-site scripting in frameworks that escape by default, unless the code uses
  the framework's raw-HTML escape hatch.
- Unguessable random identifiers (for example UUIDv4) treated as guessable.
- Low-impact web issues (tabnabbing, cross-site leaks, prototype pollution, open
  redirect) unless the impact is concrete and confidence is very high.
