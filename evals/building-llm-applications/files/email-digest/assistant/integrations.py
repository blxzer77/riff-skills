"""Mail and chat integrations available to the assistant service."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Email:
    sender: str
    subject: str
    body: str


class Mailbox:
    """The user's mailbox."""

    def __init__(self, messages: list[Email]):
        self._messages = messages
        self.sent: list[tuple[str, str, str]] = []

    def unread(self) -> list[Email]:
        return list(self._messages)

    def send_email(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject, body))


class Slack:
    def __init__(self):
        self.posts: list[tuple[str, str]] = []

    def post(self, channel: str, text: str) -> None:
        self.posts.append((channel, text))
