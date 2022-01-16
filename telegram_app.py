#!/usr/bin/env python3

from telegram.client import Telegram, AuthorizationState
import configparser

# https://python-telegram.readthedocs.io/en/0.14.0/tutorial.html#tutorial
# https://github.com/alexander-akhmetov/python-telegram/blob/a5c06855aed41ff1503c7949ccb5fe725374fa20/telegram/tdjson.py#L1
# https://python-telegram.readthedocs.io/en/0.14.0/tdlib.html

'''
api flow:
    - how to uniquely identify user?
        - phone numbers are md5 hashed and dirs are created for them 
            default = (/tmp/.tdlib_files/)
    - request for code
        - how to know which platform the code has been sent to?
    - authenticate code

    + look for mechanism that checks if user is signing up or login-in
        - if sign up: 
            - code comes via SMS 
                - (maybe should not support creating an account)
                - (maybe does not support creating an account)
        - if login:
            - code comes via other Telegram account

    + how to temporaly test login without creating too many accounts?
'''

class TelegramApp:
    def __init__(self, phone):
        self.phone = phone
        configs = configparser.ConfigParser()
        configs.read('configs.conf')

        api_id = int(configs['DEV']['API_ID'])
        api_hash = configs['DEV']['API_HASH']
        database_encryption_key = configs['DEV']['ENCRYPTION_KEY']

        self.tg = Telegram(
            api_id = api_id,  
            api_hash = api_hash,
            phone = phone,
            database_encryption_key='changeme1234')

        self.login_state=None
        self.tg.add_message_handler(self.new_message_handler)


    def register(self, first_name, last_name, blocking=False):
        if not self.login_state:
            self.login_state = self.tg.login(blocking=blocking)

        if self.login_state == AuthorizationState.WAIT_REGISTRATION:
            print('* Registration required')
            return self.tg.register_user(first=first_name, last=last_name)
        else:
            raise Exception('STATE_IS_NOT_REGISTRATION')


    def wait_login(self,code=None,password=None, blocking=False):
        if not self.login_state:
            self.login_state = self.tg.login(blocking=blocking)

        try:
            if self.login_state == AuthorizationState.WAIT_CODE:
                print('* Using code for login')
                self.tg.send_code(code)

            if self.login_state == AuthorizationState.WAIT_PASSWORD:
                print('* Using password for login')
                self.tg.send_password(password)

        except Exception as error:
            if error.args[0].find("PHONE_CODE_INVALID") > -1:

                # parse as error.args[0]
                raise Exception('PHONE_CODE_INVALID')

            raise error


        login_state = self.tg.login(blocking=blocking)
        print('* Logged in')
        return login_state

    def get_state(self,blocking=False):
        return self.tg.login(blocking=blocking)

    def idle(self):
        self.tg.idle()

    def new_message_handler(self, update):
        print('+ New message')
        message_content = update['message']['content'].get('text', {})
        message_text = message_content.get('text', '').lower()

        if message_text == 'ping':
            chat_id = update['message']['chat_id']
            print(f'Pint has been received from {chat_id}')

            self.tg.send_message(
                    chat_id = chat_id,
                    text = 'pong')
