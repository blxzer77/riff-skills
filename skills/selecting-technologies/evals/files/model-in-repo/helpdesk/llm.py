import anthropic

# Model used for every helpdesk LLM feature.
MODEL = "claude-sonnet-4-5-20250929"


def client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def complete(prompt: str, max_tokens: int = 300, llm=None) -> str:
    llm = llm or client()
    msg = llm.messages.create(model=MODEL, max_tokens=max_tokens,
                              messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text
