from threading import Event, RLock

from LCD1602.LCD1602 import (
    LCD1602,
)


class LCD:
    def __init__(self):
        self.cols: int = 16
        self.rows: int = 2
        self.lcd_impl: LCD1602 = None
        self.lock = RLock()
        self.in_bulk = Event()

    def __get_lcd_impl(self):
        if self.lcd_impl is None:  # + check whether the instance can be created?
            self.lcd_impl = LCD1602(self.cols, self.rows)
        return self.lcd_impl

    def clear(self):
        with self.lock:
            if self.in_bulk.is_set():
                self.__get_lcd_impl().clear()
            else:
                raise Exception("Method 'clear' must be called inside 'bulk_modify'!")

    def set_cursor(self, col: int, row: int):
        with self.lock:
            if self.in_bulk.is_set():
                self.__get_lcd_impl().setCursor(col, row)
            else:
                raise Exception(
                    "Method 'set_cursor' must be called inside 'bulk_modify'!"
                )

    def printout(self, text: str):
        with self.lock:
            if self.in_bulk.is_set():
                self.__get_lcd_impl().printout(text)
            else:
                raise Exception(
                    "Method 'printout' must be called inside 'bulk_modify'!"
                )

    def bulk_modify(self, callback):
        with self.lock:
            self.in_bulk.set()
            callback()
            self.in_bulk.clear()
