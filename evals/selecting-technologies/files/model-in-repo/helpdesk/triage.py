from .llm import complete

LABELS = ("billing", "bug", "account", "other")


def triage(ticket, llm=None) -> str:
    prompt = ("Classify this support ticket as one of " + ", ".join(LABELS)
              + ". Answer with the label only.\n\n" + ticket.transcript())
    answer = complete(prompt, max_tokens=5, llm=llm).strip().lower()
    return answer if answer in LABELS else "other"
