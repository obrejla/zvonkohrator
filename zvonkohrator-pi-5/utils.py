from contextlib import contextmanager
from threading import Lock


@contextmanager
def non_blocking_lock(lock: Lock):
    locked = lock.acquire(blocking=False)
    try:
        yield locked
    finally:
        if locked:
            lock.release()
