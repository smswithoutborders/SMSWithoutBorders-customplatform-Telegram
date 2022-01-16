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

if __name__ == "__main__":
    
    phone, password, code, first_name, last_name = None, None, None, None, None

    if len(sys.argv) > 1:
        phone = sys.argv[1]

        if len(sys.argv) > 3:
            if sys.argv[2] == "--code":
                code = sys.argv[3]

            elif sys.argv[2] == "--password":
                password = sys.argv[3]

            elif sys.argv[2] == "--register":
                first_name, last_name = sys.argv[3], sys.argv[4]


        users = Users(phone = phone)

        if first_name and last_name:
            print("+ Registrating user", first_name, last_name)
            try:
                users.register(first_name, last_name)
            except Exception as error:
                # raise error
                print(traceback.format_exc())

        elif password or code:
            print("* Attempting to use code...")
            try:
                if users.wait_login(password if password else code) == \
                        AuthorizationState.WAIT_REGISTRATION:
                            print("* First and last name required")
            except Exception as error:
                print("* Invalid code" if error.args[0] == 'PHONE_CODE_INVALID' else traceback.format_exc())

        else:
            if users.is_logged_in():
                print("* User is logged in...")
                users.start()
            else:
                print("* User is not logged in...")
                users.get_state()
