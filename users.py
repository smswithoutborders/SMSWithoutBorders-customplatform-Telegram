#!/usr/bin/env python3


from telegram_app import TelegramApp
import sys

class Users(TelegramApp):
    def __init__(self, phone):
        super().__init__(phone)
        self.phone = phone


    def start(self):
        self.login()
        self.idle()

    def _login(self):
        self.login()

    def is_logged_in(self):
        state = self.login()
        print('* State:', state)
        if state == 'ready':
            return True
        elif state == 'waiting code' or state == 'waiting password':
            return False

if __name__ == "__main__":
    
    phone, password, code = None, None, None

    if len(sys.argv) > 1:
        phone = sys.argv[1]

        if len(sys.argv) > 3:
            if sys.argv[2] == "--code":
                code = sys.argv[3]

            elif sys.argv[2] == "--password":
                password = sys.argv[3]


        users = Users(phone = phone)
        if not password and not code:
            if users.is_logged_in():
                print("* User is logged in...")
                users.start()
            else:
                print("* User is not logged in...")
                users._login()
        else:
            print("* Attempting to use code...")
            users.wait_login(password if password else code)
            users.idle()
