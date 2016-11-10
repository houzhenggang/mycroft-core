import sys
import time
from threading import Thread, Event
import logging

from respeaker import Microphone, Player
from respeaker.bing_speech_api import BingSpeechAPI

from mycroft.messagebus.bus import bus as client
from mycroft.messagebus.message import Message
from mycroft.session import SessionManager

from mycroft.skills.core import load_skills

logger = logging.getLogger(__file__)


try:
    from creds import BING_KEY
except ImportError:
    print(
        'Get a key from https://www.microsoft.com/cognitive-services/en-us/speech-api and create creds.py with the key')
    sys.exit(-1)


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

    client.on('speak', handle_speak)
    client.on(
        'multi_utterance_intent_failure',
        handle_multi_utterance_intent_failure
    )

    load_skills(client)

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
                client.emit(Message('recognizer_loop:utterance', payload))
                # tts_data = bing.synthesize('you said ' + text)
                # player.play_raw(tts_data)

    mic.close()
    client.emit(Message('mycroft.stop'))


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
