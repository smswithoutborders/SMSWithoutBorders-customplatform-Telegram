import logging

from error import Conflict, BadRequest, InternalServerError, RegisterAccount, UnprocessableEntity

logger = logging.getLogger(__name__)

from flask import Flask, jsonify, request
app = Flask(__name__)

from Configs import configuration
config = configuration()

from logs import logger_config
log = logger_config()

api = config["API"]

from src.telegram import (
    initialization, 
    validation, 
    revoke, 
    register, 
    contacts, 
    dialogs,
    message
)

@app.route("/", methods=["POST"])
async def start_session():
    try:
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]

        await initialization(phoneNumber)

        return "", 201

    except BadRequest as error:
        return str(error), 400
    except Conflict as error:
        return "", 200
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/", methods=["PUT"])
async def validate_code():
    try:
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()
        elif not "code" in request.json or not request.json["code"]:
            logger.error("no code")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]
        code = request.json["code"]

        result = await validation(phoneNumber, code)

        return jsonify(result), 200
    except BadRequest as error:
        return str(error), 400
    except RegisterAccount as error:
        return "", 202
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/users", methods=["POST"])
async def register_account():
    try:
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()
        elif not "first_name" in request.json or not request.json["first_name"]:
            logger.error("no first_name")
            raise BadRequest()
        elif not "last_name" in request.json or not request.json["last_name"]:
            logger.error("no last_name")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]
        firstName = request.json["first_name"]
        lastName = request.json["last_name"]

        result = await register(phoneNumber, firstName, lastName)

        return jsonify(result), 200
    except BadRequest as error:
        return str(error), 400
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/users", methods=["DELETE"])
async def revoke_access():
    try:
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]

        await revoke(phoneNumber)

        return "", 200
    except BadRequest as error:
        return str(error), 400
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500

@app.route("/contacts", methods=["POST"])
async def get_contacts():
    try:
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]

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
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]

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
        if not "phone_number" in request.json or not request.json["phone_number"]:
            logger.error("no phone_number")
            raise BadRequest()
        elif not "recipient" in request.json or not request.json["recipient"]:
            logger.error("no recipient")
            raise BadRequest()
        elif not "text" in request.json or not request.json["text"]:
            logger.error("no text")
            raise BadRequest()

        phoneNumber = request.json["phone_number"]
        recipient = request.json["recipient"]
        text = request.json["text"]

        await message(phoneNumber, recipient, text)

        return "", 200
    except BadRequest as error:
        return str(error), 400
    except UnprocessableEntity as error:
        return str(error), 422
    except InternalServerError as error:
        logger.error(error)
        return "internal server error", 500
    except Exception as error:
        logger.error(error)
        return "internal server error", 500


if __name__ == "__main__":
    app.run(host=api["host"], port=api["port"])