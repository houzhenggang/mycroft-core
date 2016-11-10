
from pyee import EventEmitter


class Bus(object):
    def __init__(self):
        self.emitter = EventEmitter()

    def emit(self, message):
        self.emitter.emit(message.type, message)

    def on(self, event_name, func):
        self.emitter.on(event_name, func)

    def once(self, event_name, func):
        self.emitter.once(event_name, func)

    def remove(self, event_name, func):
        self.emitter.remove_listener(event_name, func)


bus = Bus()

