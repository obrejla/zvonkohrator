class LCD1602Mock:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows

    def clear(self):
        pass

    def setCursor(self, col, row):
        pass

    def printout(self, string):
        print(string)
