#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

from Configs import configuration
config = configuration()

api = config["API"]

from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import UnprocessableEntity

from telegram_app import TelegramApp
from telegram_app import RegisterAccountError
from telegram_app import SessionExistError
from telegram_app import InvalidCodeError
from telegram_app import TooManyRequests

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/", methods=["POST"])
async def start_session():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        await telegramApp.initialization()

        return "", 201

    except BadRequest as error:
        return str(error), 400

    except SessionExistError as error:
        return "", 200

    except TooManyRequests as error:
        return "", 429

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/", methods=["PUT"])
async def validate_code():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        elif not "code" in request.json or not request.json["code"]:
            logger.error("no code")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]
        code = request.json["code"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        result = await telegramApp.validation(code=code)

        return result['phone_number'], 200

    except BadRequest as error:
        return str(error), 400

    except InvalidCodeError as error:
        return "", 403

    except TooManyRequests as error:
        return "", 429

    except RegisterAccountError as error:
        return "", 202

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/users", methods=["POST"])
async def register_account():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()
        elif not "first_name" in request.json or not request.json["first_name"]:
            logger.error("no first_name")
            raise BadRequest()
        elif not "last_name" in request.json or not request.json["last_name"]:
            logger.error("no last_name")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]
        firstName = request.json["first_name"]
        lastName = request.json["last_name"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        result = await telegramApp.register(firstName, lastName)

        return result["phone_number"], 200

    except BadRequest as error:
        return str(error), 400

    except InvalidCodeError as error:
        return "", 403

    except TooManyRequests as error:
        return "", 429

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/users", methods=["DELETE"])
async def revoke_access():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        await telegramApp.revoke()

        return "", 200

    except BadRequest as error:
        return str(error), 400

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/contacts", methods=["POST"])
async def get_contacts():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        result = await telegramApp.contacts()

        return jsonify(result), 200

    except BadRequest as error:
        return str(error), 400

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/dialogs", methods=["POST"])
async def get_dialogs():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        result = await telegramApp.dialogs()

        return jsonify(result), 200

    except BadRequest as error:
        return str(error), 400

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/message", methods=["POST"])
async def send_message():
    """
    """
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()
        elif not "recipient" in request.json or not request.json["recipient"]:
            logger.error("no recipient")
            raise BadRequest()
        elif not "text" in request.json or not request.json["text"]:
            logger.error("no text")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]
        recipient = request.json["recipient"]
        text = request.json["text"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        await telegramApp.message(recipient, text)

        return "", 200

    except BadRequest as error:
        return str(error), 400

    except UnprocessableEntity as error:
        return "", 422

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500


if __name__ == "__main__":
    app.run(host=api["host"], port=api["port"])
