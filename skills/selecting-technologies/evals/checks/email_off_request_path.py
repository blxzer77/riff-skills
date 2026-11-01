#!/usr/bin/env python3
"""Pass when no request-path function in app/ sends mail synchronously any more.

Request path: `signup` and every function in app/web.py. A direct call such as
`mailer.send(...)` or `SmtpMailer().send(...)` inside them fails, unless it sits in a
nested function or lambda handed elsewhere. Handing the send to a thread, an
executor, or a job table is fine; so is a job that a separate worker function runs.
The welcome email must still be sent: some code outside mailer.py must still call or
reference a mailer's `send`, and the welcome subject must still exist in app/.
"""

import ast

from tech_lib import WORKDIR, fail, ok, python_files

APP = WORKDIR / "app"


def mail_send(node: ast.AST) -> bool:
    """`<mail-ish>.send` as an attribute (called or passed as a reference)."""
    if not (isinstance(node, ast.Attribute) and node.attr in {"send", "send_message", "sendmail"}):
        return False
    target = node.value
    while isinstance(target, (ast.Attribute, ast.Call)):
        target = target.func if isinstance(target, ast.Call) else target.value
    if isinstance(target, ast.Name):
        name = target.id.lower()
        return "mail" in name or "smtp" in name
    return False


request_path, send_sites = [], []
welcome = False
for path in python_files(APP):
    source = path.read_text(encoding="utf-8")
    welcome |= "Welcome to Tidepool" in source
    tree = ast.parse(source, filename=str(path))
    if path.name != "mailer.py":
        send_sites += [f"{path.relative_to(WORKDIR)}:{n.lineno}" for n in ast.walk(tree) if mail_send(n)]
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not (fn.name == "signup" or path.name == "web.py"):
            continue
        nested = {id(n) for inner in ast.walk(fn) if inner is not fn
                  and isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
                  for n in ast.walk(inner)}
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and mail_send(node.func) and id(node) not in nested:
                request_path.append(f"{path.relative_to(WORKDIR)}:{node.lineno} in {fn.name}")

if request_path:
    fail(f"mail is still sent synchronously on the request path: {request_path}")
if not send_sites or not welcome:
    fail("the welcome email is no longer sent by any code in app/")
ok(f"email sent off the request path (send sites: {sorted(set(send_sites))})")
