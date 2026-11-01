# Auth notes (2026-10)

- Today: express-session with a Postgres session store, cookie `rw.sid`.
- Problem: the Lambda api has to hit Postgres on every request to load the session.
- Idea: short-lived JWT access tokens (15 min) plus a refresh token in an
  httpOnly cookie; revoke by rotating refresh tokens.
- Open question: how do we log someone out everywhere?
