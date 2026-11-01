import threading

_lock = threading.Lock()
_store: dict[str, int] = {}


def write(key: str, value: int) -> None:
    current = _store.get(key, 0)
    _store[key] = current + value
