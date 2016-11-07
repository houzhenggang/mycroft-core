import sys
import time
from threading import Thread, Event

from respeaker import Microphone, Player
from respeaker.bing_speech_api import BingSpeechAPI, UnknownValueError

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.session import SessionManager
from mycroft.util.log import getLogger

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

    logger = getLogger("SpeechClient")
    client = WebsocketClient()
    done_event = Event()

    def speak(text):
        try:
            tts_data = bing.synthesize(text)
            player.play_raw(tts_data)
        except UnknownValueError:
            pass

    def handle_speak(event):
        utterance = event.data['utterance']
        logger.info("Utterance: " + utterance)
        speak(utterance)
        done_event.set()

    def handle_multi_utterance_intent_failure(event):
        logger.info("Failed to find intent on multiple intents.")
        speak("Sorry, I didn't catch that. Please rephrase your request.")
        done_event.set()

    def connect():
        client.run_forever()

    client.on('speak', handle_speak)
    client.on(
        'multi_utterance_intent_failure',
        handle_multi_utterance_intent_failure
    )
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    while not quit_event.is_set():
        if mic.wakeup(keyword='respeaker'):
            data = mic.listen()
            if data:
                # recognize speech using Microsoft Bing Voice Recognition
                try:
                    text = bing.recognize(data, language='en-US')
                except UnknownValueError as e:
                    logger.warn(e.message)
                    continue

                utterance = [text]
                payload = {
                    'utterances': utterance,
                    'session': SessionManager.get().session_id
                }
                client.emit(Message('recognizer_loop:utterance', payload))
                print('Bing:' + text.encode('utf-8'))
                # tts_data = bing.synthesize('you said ' + text)
                # player.play_raw(tts_data)

                done_event.clear()
                done_event.wait(15)

    mic.close()


def main():
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
