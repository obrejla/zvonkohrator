from LCD1602.LCD1602 import LCD1602


class LCD:
    def __init__(self):
        self.cols: int = 16
        self.rows: int = 2
        self.lcd_impl: LCD1602 = None

    def __get_lcd_impl(self):
        if self.lcd_impl is None:  # + check whether the instance can be created?
            self.lcd_impl = LCD1602(self.cols, self.rows)
        return self.lcd_impl

    def clear(self):
        if self.lcd_impl is not None:
            self.lcd_impl.clear()

    def set_cursor(self, col: int, row: int):
        self.__get_lcd_impl().setCursor(col, row)

    def printout(self, text: str):
        self.__get_lcd_impl().printout(text)
