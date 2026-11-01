import unittest

from helpdesk import sample_ticket


class TicketTest(unittest.TestCase):
    def test_transcript_joins_messages(self):
        ticket = sample_ticket()
        self.assertIn("charged twice", ticket.transcript())
        self.assertEqual(ticket.transcript().count("\n\n"), 2)


if __name__ == "__main__":
    unittest.main()
