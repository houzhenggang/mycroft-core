# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from adapt.intent import IntentBuilder
from os.path import dirname
from pyowm import OWM

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jdorleans'

LOG = getLogger(__name__)


class WeatherSkill(MycroftSkill):
    def __init__(self):
        super(WeatherSkill, self).__init__("WeatherSkill")
        self.temperature = self.config.get('temperature')
        self.__init_owm()

    def __init_owm(self):
        key = self.config.get('api_key')
        self.owm = OWM(key)

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.__build_current_intent()
        self.__build_next_hour_intent()
        self.__build_next_day_intent()

    def __build_current_intent(self):
        intent = IntentBuilder("CurrentWeatherIntent").require(
            "WeatherKeyword").optionally("Location").build()
        self.register_intent(intent, self.handle_current_intent)

    def __build_next_hour_intent(self):
        intent = IntentBuilder("NextHoursWeatherIntent").require(
            "WeatherKeyword").optionally("Location") \
            .require("NextHours").build()
        self.register_intent(intent, self.handle_next_hour_intent)

    def __build_next_day_intent(self):
        intent = IntentBuilder("NextDayWeatherIntent").require(
            "WeatherKeyword").optionally("Location") \
            .require("NextDay").build()
        self.register_intent(intent, self.handle_next_day_intent)

    def handle_current_intent(self, message):
        try:
            location = message.data.get("Location", self.location)
            weather = self.owm.weather_at_place(location).get_weather()
            data = self.__build_data_condition(location, weather)
            self.speak_dialog('current.weather', data)
        except Exception as e:
            LOG.debug(e)
            LOG.error("Error: {0}".format(e))

    def handle_next_hour_intent(self, message):
        try:
            location = message.data.get("Location", self.location)
            weather = self.owm.three_hours_forecast(
                location).get_forecast().get_weathers()[0]
            data = self.__build_data_condition(location, weather)
            self.speak_dialog('hour.weather', data)
        except Exception as e:
            LOG.error("Error: {0}".format(e))

    def handle_next_day_intent(self, message):
        try:
            location = message.data.get("Location", self.location)
            weather = self.owm.daily_forecast(
                location).get_forecast().get_weathers()[1]
            data = self.__build_data_condition(
                location, weather, 'day', 'min', 'max')
            self.speak_dialog('tomorrow.weather', data)
        except Exception as e:
            LOG.error("Error: {0}".format(e))

    def __build_data_condition(
            self, location, weather, temp='temp', temp_min='temp_min',
            temp_max='temp_max'):
        data = {
            'location': location,
            'scale': self.temperature,
            'condition': weather.get_detailed_status(),
            'temp_current': self.__get_temperature(weather, temp),
            'temp_min': self.__get_temperature(weather, temp_min),
            'temp_max': self.__get_temperature(weather, temp_max)
        }
        return data

    def __get_temperature(self, weather, key):
        return str(int(round(weather.get_temperature(self.temperature)[key])))

    def stop(self):
        pass


def create_skill():
    return WeatherSkill()
