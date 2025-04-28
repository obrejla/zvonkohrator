from queue import Queue
from threading import Event, Lock, RLock, Thread
from time import sleep

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController
from zvonkohrator_pi_5.LCD import LCD
from zvonkohrator_pi_5.LCD1602.LCD1602 import (
    LCD1602,
)


class LCDImpl(LCD):
    def __init__(self, energy_controller: EnergyController):
        self.energy_controller = energy_controller
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
        Thread(
            target=self.__display_worker, daemon=True, name="LCDDisplayWorker"
        ).start()
        self.energy_controller.add_energy_flow_listener(self.__energy_flow_listener)

    def __display_worker(self):
        while True:
            if self.__current_display_differs():
                self.energy_controller.wait_for_energy()
                if (
                    self.energy_controller.is_energy_flowing()
                    and self.__current_display_differs()
                ):  # energy_flows could have been cleared after the `self.energy_controller.wait_for_energy()` check and display could be modified as well
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

    def __energy_flow_listener(self, energy: Energy):
        if energy == Energy.NONE:
            self.__show_not_enough_energy()

    def __show_not_enough_energy(self):
        with self.lcd_lock:
            if (
                not self.energy_controller.is_energy_flowing()
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
