from dataclasses import dataclass, field


@dataclass
class Ticket:
    id: int
    subject: str
    messages: list[str] = field(default_factory=list)

    def transcript(self) -> str:
        return "\n\n".join(self.messages)


def sample_ticket() -> Ticket:
    return Ticket(
        id=4182,
        subject="Charged twice for March",
        messages=[
            "Hi, my card was charged twice for the March plan. Can you refund one?",
            "Thanks for reaching out. I can see two charges on 3 March; one is a pending "
            "authorization that should drop off in 5 business days.",
            "It has been 8 days and it is still there.",
        ],
    )
