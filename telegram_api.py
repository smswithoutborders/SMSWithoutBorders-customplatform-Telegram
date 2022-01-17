#!/usr/bin/env python3

import os, sys
import logging
import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS

from users import Users
from telegram.client import AuthorizationState

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['POST'])
def start_session():
    logging.debug("starting new session for user")
    data = None

    try:
        data = request.json
    except Exception as error:
        return 'invalid json', 400

    if not 'phonenumber' in data:
        return 'phone number missing', 400

    number = data['phonenumber']
    try:
        user = Users(number)
        user_state = user.get_state()
        logging.info("%s", user_state)
        if user_state == AuthorizationState.READY:
            return '', 200

        if user_state == AuthorizationState.WAIT_CODE:
            return '', 100

    except Exception as error:
        logging.exception(error)
    finally:
        user.stop()

    return '', 400


@app.route('/', methods=['PUT'])
def wait_code():
    data=None

    try:
        data = request.json
    except Exception as error:
        return 'invalid json', 400

    password = None
    if not 'code' in data:
        return 'code missing', 400

    if not 'phonenumber' in data:
        return 'phone number missing', 400

    code = data['code']
    number = data['phonenumber']
    logging.debug("getting code for user %s", number)

    try:
        user = Users(number)
        user_state = user.get_state()
        if user_state == AuthorizationState.WAIT_CODE:
            logging.info("User code awaits...")
            try:
                user_state = user.wait_login(password if password else code)

                if user_state == AuthorizationState.WAIT_REGISTRATION: 
                    return '', 101

                elif user_state == AuthorizationState.READY:
                    return '', 200

            except Exception as error:
                logging.exception(error)

                if error.args[0] == 'PHONE_CODE_INVALID':
                    return '', 403

                raise error
                
        if user_state == AuthorizationState.READY:
            return '', 200
    except Exception as error:
        logging.exception(error)
    finally:
        user.stop()

    return '', 400


@app.route('/users', methods=['POST'])
def register_account():

    try:
        data = request.json
    except Exception as error:
        return 'invalid json', 400

    if not 'first_name' in data:
        return 'first_name missing', 400

    if not 'last_name' in data:
        return 'last_name missing', 400

    if not 'phonenumber' in data:
        return 'phone number missing', 400

    first_name = data['first_name']
    last_name = data['last_name']
    number = data['phonenumber']
    logging.debug("registering a new user %s", number)

    try:
        user = Users(number)
        registration_state = user.register(first_name, last_name)
        if registration_state == AuthorizationState.READY:
            return '', 200

    except Exception as error:
        logging.exception(error)

    return '', 400


if __name__ == "__main__":

    debug = True
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument(
            '-l', '--log',
            default='CRITICAL',
            help='--log=[DEBUG, INFO, WARNING, ERROR, CRITICAL]')

    parser.add_argument("-d", "--debug",
            help="turn on flask debug mode")

    args = parser.parse_args()


    log_file_path = os.path.join(os.path.dirname(__file__), '.logs', 'api.log')

    logging.basicConfig(
        # format='%(asctime)s|[%(levelname)s] %(pathname)s %(lineno)d|%(message)s',
        format='%(asctime)s|[%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout) ],
        level=args.log.upper())

    app.run( debug=debug )
