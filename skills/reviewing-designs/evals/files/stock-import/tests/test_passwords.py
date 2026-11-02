import hashlib
import unittest

from app.passwords import verify


class VerifyTest(unittest.TestCase):
    def test_round_trip(self):
        salt = bytes(16)
        digest = hashlib.scrypt(b"pw", salt=salt, n=2**14, r=8, p=1).hex()
        self.assertTrue(verify("pw", salt.hex() + "$" + digest))
        self.assertFalse(verify("nope", salt.hex() + "$" + digest))
