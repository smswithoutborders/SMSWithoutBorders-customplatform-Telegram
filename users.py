#!/usr/bin/env python3


from telegram_app import TelegramApp
from telegram.client import AuthorizationState
import sys
import traceback

class Users(TelegramApp):
    def __init__(self, phone):
        super().__init__(phone)
        self.phone = phone


    def start(self):
        self.get_state()
        self.idle()

    def is_logged_in(self):
        state = self.get_state()
        print('* State:', state)
        if state == AuthorizationState.READY:
            return True
        elif state == AuthorizationState.WAIT_PASSWORD or \
                state == AuthorizationState.WAIT_CODE:
                    return False
