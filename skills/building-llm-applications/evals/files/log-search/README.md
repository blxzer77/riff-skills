# oncall-agent

An agent that helps on-call engineers investigate incidents. `assistant/tools.py` is
the tool registry, `assistant/logstore.py` reads the application log (typically a few
hundred thousand lines per day), and `assistant/llm.py` is the model client
interface. Run tests with `python3 -m unittest`.

Register new tools by calling `tools.register(definition, handler)` at import time of
the module that defines them.
