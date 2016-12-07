import sys
import time
from threading import Thread, Event
import logging
import pkg_resources

from respeaker import Microphone, Player
from respeaker.bing_speech_api import BingSpeechAPI

from mycroft.messagebus.message import Message
from mycroft.session import SessionManager
from mycroft.skills.core import load_skills as load_mycroft_skills

from mycroft.messagebus.bus import bus


logger = logging.getLogger(__file__)


try:
    from creds import BING_KEY
except ImportError:
    print(
        'Get a key from https://www.microsoft.com/cognitive-services/en-us/speech-api and create creds.py with the key')
    sys.exit(-1)


def load_extension_skills(bus):
    """Find all installed skills.

    :returns: list of installed skills
    """

    installed_skills = []

    for entry_point in pkg_resources.iter_entry_points('hallo.skill'):
        logger.debug('Loading entry point: %s', entry_point)
        try:
            skill_create_function = entry_point.load(require=False)
        except Exception as e:
            logger.exception("Failed to load skill %s: %s" % (
                entry_point.name, e))
            continue

        try:
            skill = skill_create_function()
            skill.bind(bus)
            skill.initialize()
        except Exception:
            logger.exception('Setup of skill from entry point %s failed, '
                             'ignoring extension.', entry_point.name)
            continue

        installed_skills.append(skill)

        logger.debug(
            'Loaded skill: %s %s', skill.name, skill.version)

    names = (skill.name for skill in installed_skills)
    logger.debug('Discovered skill: %s', ', '.join(names))


def task(quit_event):
    mic = Microphone(quit_event=quit_event)
    player = Player(mic.pyaudio_instance)
    bing = BingSpeechAPI(BING_KEY)

    def speak(text):
        try:
            tts_data = bing.synthesize(text)
            player.play_raw(tts_data)
        except:
            logger.warning('Failed to convert text to speech')
            pass

    def handle_speak(event):
        utterance = event.data['utterance']
        logger.info("Utterance: " + utterance)
        speak(utterance)

    def handle_multi_utterance_intent_failure(event):
        logger.info("Failed to find intent on multiple intents.")
        speak("Sorry, I didn't catch that. Please rephrase your request.")

    bus.on('speak', handle_speak)
    bus.on(
        'multi_utterance_intent_failure',
        handle_multi_utterance_intent_failure
    )

    load_mycroft_skills(bus)
    load_extension_skills(bus)

    while not quit_event.is_set():
        if mic.wakeup(keyword='respeaker'):
            data = mic.listen()
            if data:
                # recognize speech using Microsoft Bing Voice Recognition
                try:
                    text = bing.recognize(data, language='en-US')
                except Exception as e:
                    logger.warning(e.message)
                    continue

                utterance = [text]
                payload = {
                    'utterances': utterance,
                    'session': SessionManager.get().session_id
                }

                print('Bing:' + text.encode('utf-8'))
                bus.emit(Message('recognizer_loop:utterance', payload))
                # tts_data = bing.synthesize('you said ' + text)
                # player.play_raw(tts_data)

    mic.close()
    bus.emit(Message('mycroft.stop'))


def main():
    logging.basicConfig(level=logging.DEBUG)
    quit_event = Event()
    thread = Thread(target=task, args=(quit_event,))
    thread.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('Quit')
            quit_event.set()
            break

    thread.join()


if __name__ == '__main__':
    main()
