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


from os.path import dirname, join

import subprocess

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

logger = getLogger(__name__)

__author__ = 'ryanleesipes'


class IPSkill(MycroftSkill):
    SEC_PER_LETTER = 4.0 / 7.0
    LETTERS_PER_SCREEN = 9.0

    def __init__(self):
        super(IPSkill, self).__init__(name="IPSkill")

    def initialize(self):
        self.load_vocab_files(join(dirname(__file__), 'vocab', 'en-us'))

        intent = IntentBuilder("IPIntent").require("IPCommand").build()
        self.register_intent(intent, self.handle_intent)

    @staticmethod
    def get_ip(iface):
        command = "ifconfig %s | sed -n 's/.*inet addr:\\([0-9.]*\\).*/\\1/p'" % iface
        line = subprocess.check_output(command, shell=True)
        return line[:-1]

    def handle_intent(self, message):
        address = self.get_ip('apcli0') 
        self.speak("My I.P. address is %s." % address)

    def stop(self):
        pass


def create_skill():
    return IPSkill()
