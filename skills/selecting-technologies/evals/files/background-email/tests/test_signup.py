import unittest

from app.signup import SignupError, signup


class FakeDb:
    def __init__(self):
        self.users = []

    def insert_user(self, email, name):
        self.users.append((email, name))
        return len(self.users)


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))


class SignupTest(unittest.TestCase):
    def test_creates_user(self):
        db = FakeDb()
        user_id = signup(db, FakeMailer(), "ana@example.com", "Ana")
        self.assertEqual(user_id, 1)
        self.assertEqual(db.users, [("ana@example.com", "Ana")])

    def test_rejects_invalid_email(self):
        with self.assertRaises(SignupError):
            signup(FakeDb(), FakeMailer(), "not-an-email", "Ana")


if __name__ == "__main__":
    unittest.main()
