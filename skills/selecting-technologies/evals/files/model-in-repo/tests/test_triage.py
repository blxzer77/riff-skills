import types
import unittest

from helpdesk import sample_ticket, triage


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=self.reply)])


class TriageTest(unittest.TestCase):
    def test_known_label(self):
        self.assertEqual(triage(sample_ticket(), llm=FakeLLM("Billing")), "billing")

    def test_unknown_label(self):
        self.assertEqual(triage(sample_ticket(), llm=FakeLLM("refund")), "other")
