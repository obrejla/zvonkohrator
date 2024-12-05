from MidiCommandHandler import MidiCommandHandler

class MidiCommandHandlers:

    def __init__(self):
        self.command_handlers: list[MidiCommandHandler] = []

    def handle(self, msg, dt: int):
        command = hex(msg[0])
        for command_handler in self.command_handlers:
            if command_handler.handles(command):
                command_handler.handle(msg, dt)
                break

    def register(self, command_handler: MidiCommandHandler):
        self.command_handlers.append(command_handler)
