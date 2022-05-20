#!/usr/bin/env python3
import logging

from error import Conflict, BadRequest, Forbidden, InternalServerError, RegisterAccount, UnprocessableEntity

logger = logging.getLogger(__name__)

from flask import Flask, jsonify, request
app = Flask(__name__)

from Configs import configuration
config = configuration()

from logs import logger_config
log = logger_config()

api = config["API"]

from src.telegram import (
    register, 
    contacts, 
    dialogs
)

from src.telegram import TelegramApp

@app.route("/", methods=["POST"])
async def start_session():
    try:
        app.logger.debug(request.json)
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        await telegramApp.initialization()

        return "", 201

    except BadRequest as error:
        app.logger.exception(error)
        return str(error), 400

    except Conflict as error:
        return "", 200

    except InternalServerError as error:
        app.logger.exception(error)
        return "internal server error", 500

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/", methods=["PUT"])
async def validate_code():
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
        app.logger.exception(error)
        return str(error), 400

    except Forbidden as error:
        app.logger.exception(error)
        return "", 403

    except RegisterAccount as error:
        app.logger.exception(error)
        return "", 202

    except InternalServerError as error:
        app.logger.exception(error)
        return "internal server error", 500

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/users", methods=["POST"])
async def register_account():
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

        result = await register(phoneNumber, firstName, lastName)

        return jsonify(result), 200
    except BadRequest as error:
        return str(error), 400
    except Forbidden as error:
        return "", 403
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/users", methods=["DELETE"])
async def revoke_access():
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        telegramApp = TelegramApp(phone_number = phoneNumber)
        await telegramApp.revoke()

        return "", 200

    except BadRequest as error:
        app.logger.exception(error)
        return str(error), 400

    except InternalServerError as error:
        app.logger.exception(error)
        return "internal server error", 500

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500

@app.route("/contacts", methods=["POST"])
async def get_contacts():
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        result = await contacts(phoneNumber)

        return jsonify(result), 200
    except BadRequest as error:
        return str(error), 400
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/dialogs", methods=["POST"])
async def get_dialogs():
    try:
        if not "phonenumber" in request.json or not request.json["phonenumber"]:
            logger.error("no phonenumber")
            raise BadRequest()

        phoneNumber = request.json["phonenumber"]

        result = await dialogs(phoneNumber)

        return jsonify(result), 200
    except BadRequest as error:
        return str(error), 400
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/message", methods=["POST"])
async def send_message():
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
        app.logger.exception(error)
        return str(error), 400

    except UnprocessableEntity as error:
        app.logger.exception(error)
        return "", 422

    except InternalServerError as error:
        app.logger.exception(error)
        return "internal server error", 500

    except Exception as error:
        app.logger.exception(error)
        return "internal server error", 500


if __name__ == "__main__":
    app.run(host=api["host"], port=api["port"])
