

import tornado.ioloop as ioloop
from threading import Thread, Event
import time

from mycroft.messagebus.service.main import main as service_task
from mycroft.skills.main import main as skill_task
from respeaker_client import task



service_thread = Thread(target=service_task)
service_thread.start()
time.sleep(1)

skills_thread = Thread(target=skill_task)
skills_thread.daemon = True
skills_thread.start()


quit_event = Event()
respeaker_thread = Thread(target=task, args=(quit_event,))
respeaker_thread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print('Quit')
        quit_event.set()
        break

ioloop.IOLoop.instance().stop()
respeaker_thread.join()
service_thread.join()
