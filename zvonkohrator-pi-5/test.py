from gpiozero import Button
from signal import pause

prev_button = Button(26)
stop_button = Button(19)
play_pause_button = Button(13)
next_button = Button(6)


prev_button.when_pressed = lambda : print("PREV button pressed")
stop_button.when_pressed = lambda : print("STOP button pressed")
play_pause_button.when_pressed = lambda : print("PLAY/PAUSE button pressed")
next_button.when_pressed = lambda : print("NEXT button pressed")

pause()
