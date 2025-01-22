from queue import Queue
from threading import Event, Lock, RLock, Thread
from time import sleep

from LCD1602.LCD1602 import (
    LCD1602,
)


class LCD:
    def __init__(self, energy_flows: Event):
        self.energy_flows = energy_flows
        self.cols: int = 16
        self.rows: int = 2
        self.lcd_impl: LCD1602 = None
        self.current_state = [" " * 16, " " * 16]
        self.last_col = 0
        self.last_row = 0
        self.last_rendered_state = [" " * 16, " " * 16]
        self.lcd_lock = Lock()
        self.modify_lock = RLock()
        self.in_bulk = Event()
        self.rerender_queue = Queue()
        self.display_thread = Thread(
            target=self.__display_worker, daemon=True, name="LCDDisplayWorker"
        ).start()

    def __display_worker(self):
        while True:
            if self.__current_display_differs():
                self.energy_flows.wait()
                if (
                    self.energy_flows.is_set() and self.__current_display_differs()
                ):  # energy_flows could have been cleared after the `self.energy_flows.wait()` check and display could be modified as well
                    with self.lcd_lock:
                        self.__get_lcd_impl().setCursor(0, 0)
                        self.__get_lcd_impl().printout(self.current_state[0])
                        self.last_rendered_state[0] = self.current_state[0]
                        self.__get_lcd_impl().setCursor(0, 1)
                        self.__get_lcd_impl().printout(self.current_state[1])
                        self.last_rendered_state[1] = self.current_state[1]
                else:
                    sleep(0.1)

    def __current_display_differs(self):
        return (
            self.current_state[0] != self.last_rendered_state[0]
            or self.current_state[1] != self.last_rendered_state[1]
        )

    def show_not_enough_energy(self):
        with self.lcd_lock:
            if (
                not self.energy_flows.is_set()
            ):  # it could have been set after the before entering the lock section
                # directly modify LCD, do not modify current_state - let bulk_modify to change current_state in the meantime
                self.__get_lcd_impl().setCursor(0, 0)
                first_row = " ! NEDOSTATEK ! "
                self.__get_lcd_impl().printout(first_row)
                self.last_rendered_state[0] = first_row
                self.__get_lcd_impl().setCursor(0, 1)
                second_row = " !!! ENERGY !!! "
                self.__get_lcd_impl().printout(second_row)
                self.last_rendered_state[1] = second_row

    def __get_lcd_impl(self):
        if self.lcd_impl is None:  # + check whether the instance can be created?
            self.lcd_impl = LCD1602(self.cols, self.rows)
        return self.lcd_impl

    def clear(self):
        with self.modify_lock:
            if self.in_bulk.is_set():
                self.current_state = [" " * 16, " " * 16]
            else:
                raise Exception("Method 'clear' must be called inside 'bulk_modify'!")

    def set_cursor(self, col: int, row: int):
        with self.modify_lock:
            if self.in_bulk.is_set():
                self.last_col = col
                self.last_row = row
            else:
                raise Exception(
                    "Method 'set_cursor' must be called inside 'bulk_modify'!"
                )

    def printout(self, text: str):
        with self.modify_lock:
            if self.in_bulk.is_set():
                current_state_row = self.current_state[self.last_row]
                self.current_state[self.last_row] = (
                    current_state_row[0 : self.last_col]
                    + text
                    + current_state_row[self.last_col + len(text) :]
                )
            else:
                raise Exception(
                    "Method 'printout' must be called inside 'bulk_modify'!"
                )

    def bulk_modify(self, callback):
        with self.modify_lock:
            self.in_bulk.set()
            callback()
            self.in_bulk.clear()
