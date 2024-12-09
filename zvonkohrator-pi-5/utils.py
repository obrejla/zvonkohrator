from contextlib import contextmanager
from threading import Lock
from time import time


@contextmanager
def non_blocking_lock(lock: Lock):
    locked = lock.acquire(blocking=False)
    try:
        yield locked
    finally:
        if locked:
            lock.release()


def throttle(callback, interval=0.3):
    """
    Useful for throttling events from pressed buttons, because sometimes one finger press generates more events.
    """
    last_time = time()

    def inner():
        nonlocal last_time
        current_time = time()
        if (current_time - last_time) > interval:
            last_time = time()
            callback()

    return inner
