from contextlib import contextmanager
from threading import Event, Lock
from time import sleep, time

from zvonkohrator_pi_5.LCD import LCD


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


def show_loading(lcd: LCD, time_in_seconds: int, row: int, in_loading: Event):
    sleep_time = time_in_seconds / 15
    lcd.set_cursor(0, row)
    lcd.printout("[              ]")
    sleep(sleep_time)
    for i in range(14):
        lcd.set_cursor(i + 1, 1)
        lcd.printout("|")
        sleep(sleep_time)
        if in_loading is not None and not in_loading.is_set():
            break
