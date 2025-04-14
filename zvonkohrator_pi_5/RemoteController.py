from bluedot import BlueDot


class RemoteController:
    def __init__(self):
        bd = BlueDot(cols=7, rows=1)

        self.prev_buton = bd[0, 0]
        self.prev_buton.color = "yellow"
        bd[1, 0].visible = False
        self.stop_button = bd[2, 0]
        self.stop_button.color = "red"
        bd[3, 0].visible = False
        self.play_pause_button = bd[4, 0]
        self.play_pause_button.color = "green"
        bd[5, 0].visible = False
        self.next_button = bd[6, 0]
        self.next_button.color = "yellow"
