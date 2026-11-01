import unittest

from members import AccountError, Accounts


class AccountsTest(unittest.TestCase):
    def setUp(self):
        self.accounts = Accounts()
        self.accounts.signup("ana@example.com", "correct horse")

    def test_login_with_right_password(self):
        self.assertTrue(self.accounts.login("ana@example.com", "correct horse"))

    def test_login_with_wrong_password(self):
        self.assertFalse(self.accounts.login("ana@example.com", "wrong horse"))

    def test_unknown_email(self):
        self.assertFalse(self.accounts.login("bob@example.com", "correct horse"))

    def test_duplicate_signup(self):
        with self.assertRaises(AccountError):
            self.accounts.signup("ana@example.com", "another one")


if __name__ == "__main__":
    unittest.main()
