#!/usr/bin/env python3

from telegram.client import Telegram, AuthorizationState
import configparser
import logging
import os
import hashlib
import shutil

# https://python-telegram.readthedocs.io/en/0.14.0/tutorial.html#tutorial
# https://github.com/alexander-akhmetov/python-telegram/blob/a5c06855aed41ff1503c7949ccb5fe725374fa20/telegram/tdjson.py#L1
# https://python-telegram.readthedocs.io/en/0.14.0/tdlib.html

class TelegramApp:
    def __init__(self, phone):
        self.phone = phone
        configs = configparser.ConfigParser()
        configs.read( 
                os.path.join(
                    os.path.dirname(__file__), '', 'configs.conf'))

        api_id = int(configs['DEV']['API_ID'])
        api_hash = configs['DEV']['API_HASH']
        database_encryption_key = configs['DEV']['ENCRYPTION_KEY']

        self.files_dir = os.path.join(
                    os.path.dirname(__file__), '.records/users', self.hash(phone))

        self.files_dir = ".records/users/" + self.hash(phone)
        self.tg = Telegram(
            api_id = api_id,  
            api_hash = api_hash,
            phone = phone,
            files_directory = self.files_dir,
            use_message_database = False,
            device_model = 'SMSWithoutBorders-Telegram',
            database_encryption_key=database_encryption_key)

        self.login_state=None
        self.tg.add_message_handler(self.new_message_handler)

    def hash(self, data: str) -> str:
        """
        """
        try:
            return hashlib.md5(data.encode("utf-8")).hexdigest()
        except Exception as error:
            raise error

    def register(self, first_name, last_name, blocking=False):
        if not self.login_state:
            self.login_state = self.tg.login(blocking=blocking)

        if self.login_state == AuthorizationState.WAIT_REGISTRATION:
            return self.tg.register_user(first=first_name, last=last_name)
        else:
            raise Exception('STATE_IS_NOT_REGISTRATION')


    def wait_login(self,code=None,password=None, blocking=False):
        if not self.login_state:
            self.login_state = self.tg.login(blocking=blocking)

        try:
            if self.login_state == AuthorizationState.WAIT_CODE:
                logging.debug('* Using code for login')
                self.tg.send_code(code)

            if self.login_state == AuthorizationState.WAIT_PASSWORD:
                logging.debug('* Using password for login')
                self.tg.send_password(password)

        except Exception as error:
            if error.args[0].find("PHONE_CODE_INVALID") > -1:

                # parse as error.args[0]
                raise Exception('PHONE_CODE_INVALID')

            raise error


        login_state = self.tg.login(blocking=blocking)
        logging.debug('* Logged in')

        state = self.tg.login(blocking=blocking)
        # self.tg.stop()

        return login_state

    def stop(self):
        self.tg.stop()

    def get_state(self,blocking=False):
        state = self.tg.login(blocking=blocking)
        """
        asyncResult_state = self.tg.get_authorization_state()
        asyncResult_state.wait(raise_exc=True)

        authorization_state = None
        if asyncResult_state.id == 'getAuthorizationState':
            authorization_state = asyncResult_state.update['@type']
        else:
            authorization_state = asyncResult_state.update['authorization_state']['@type']

        state = AuthorizationState(authorization_state)
        """
        logging.info("%s", state)

        return state

    def idle(self):
        self.tg.idle()

    def new_message_handler(self, update):
        message_content = update['message']['content'].get('text', {})
        message_text = message_content.get('text', '').lower()

        if message_text == 'ping':
            chat_id = update['message']['chat_id']
            print(f'Pint has been received from {chat_id}')

            self.tg.send_message(
                    chat_id = chat_id,
                    text = 'pong')


    def delete(self):
        try:
            shutil.rmtree(self.files_dir, ignore_errors=True)
        except Exception as error:
            raise error

