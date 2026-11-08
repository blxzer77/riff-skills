# assistant-service

Internal assistant for the support team. `assistant/llm.py` is the model client
interface; `assistant/integrations.py` has the mailbox and Slack integrations. Tests
use fake clients; run them with `python3 -m unittest`.

Conventions: application code lives in `assistant/`, one module per feature, and each
feature exposes a plain function that takes its dependencies as arguments so tests can
pass fakes.
