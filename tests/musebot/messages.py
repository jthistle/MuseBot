#!/usr/bin/env python3

from ..testbase import TestBase
from ..testLib.musebot import MuseBot
from random import randint

class MessagesTest(TestBase):
    def mockMessage(self, msg):
        self.counter += 1
        return {
            "text": msg,
            "from": {
                "id": randint(-34313, 18429),
            },
            "message_id": self.counter,
            "chat": {
                "id": self.channel,
            }
        }

    def test(self):
        messages = [
            "/help",
            "See #278023 for more details :)",
            "check out my pr #2452",
            "oops that should be PR#2453",
            "<?>/integrate <huh>",
            "/mute",
            "/unmute",
            "pr #2030203203",
            "#    478237492374892",
            "/delete",
        ]

        self.counter = randint(2, 50000)
        self.channel = randint(-3284222, 2844382)

        for i in range(len(messages)):
            messages[i] = self.mockMessage(messages[i])

        instance = MuseBot()

        for msg in messages:
            instance.handleMessage(msg)

test = MessagesTest("Messages", "various messages are handled without crashing")
