Mycroft on ReSpeaker
====================

Running Mycroft AI on ReSpeaker.

## Get started
1. find a sd card and [use it as extroot](https://github.com/respeaker/get_started_with_respeaker/blob/master/QuickStart.md#use-sd-card-to-extend-storage)
2. install git

  ```
  opkg update
  opkg install git git-http
  ```

3. download this repo and [a virtualenv instance](https://github.com/respeaker/respeaker_virtualenv) containing required python packages

  ```
  git clone https://github.com/respeaker/respeaker_virtualenv.git
  git clone https://github.com/respeaker/mycroft-core.git
  ```

4. get bing speech api key from [microsoft congnitive services](https://www.microsoft.com/cognitive-services/en-us/speech-api)
5. rename `mycroft-core/example_creds.py` to `mycroft-core/creds.py` and fill in `BING_KEY`
6. `. respeaker_virtualenv/bin/activate && python mycroft_on_respeaker.py`
