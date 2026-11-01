import hashlib


class AccountError(Exception):
    pass


class Accounts:
    def __init__(self):
        self._users = {}

    def signup(self, email: str, password: str) -> None:
        if email in self._users:
            raise AccountError("email already registered")
        if len(password) < 8:
            raise AccountError("password too short")
        self._users[email] = hashlib.sha256(password.encode()).hexdigest()

    def login(self, email: str, password: str) -> bool:
        stored = self._users.get(email)
        if stored is None:
            return False
        return stored == hashlib.sha256(password.encode()).hexdigest()

    def stored_hash(self, email: str) -> str:
        return self._users[email]
