import threading

from billing import sync


def test_concurrent_writes():
    sync._store.clear()
    threads = [threading.Thread(target=sync.write, args=("k", 1)) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sync._store["k"] == 50
