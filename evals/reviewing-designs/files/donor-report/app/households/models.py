from dataclasses import dataclass


@dataclass
class Household:
    id: int
    customer_ref: str
    name: str
    email: str | None
    size: int
