import os
import shutil
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

from configparser import ConfigParser
from telethon import TelegramClient
from telethon import functions
from telethon.errors import PhoneNumberUnoccupiedError

config_filepath = os.path.abspath("configs/configs.ini")

if not os.path.exists(config_filepath):
    error = f"configs file not found at {config_filepath}"
    raise Exception(error)

config = ConfigParser()
config.read(config_filepath)

dev = config["DEV"]
api_id = dev['API_ID']
api_hash = dev['API_HASH']

@app.route("/init", methods=["POST"])
async def start():
    try:
        phone_number = request.json["phonenumber"]

        record_filepath = os.path.abspath(f"records/{phone_number}")

        if not os.path.exists(record_filepath):
            os.makedirs(record_filepath)
        
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone=f"{phone_number}", force_sms=True)
            await client.disconnect()
        else:
            await client.disconnect()
            return jsonify("already logged in"), 429

        return jsonify(phone_number), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

@app.route("/validate", methods=["POST"])
async def code():
    try:
        phone_number = request.json["phonenumber"]
        code = request.json["code"]

        record_filepath = os.path.abspath(f"records/{phone_number}")

        if not os.path.exists(record_filepath):
            os.makedirs(record_filepath)

        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)
        await client.connect()

        try:
            result = await client.sign_in(f"{phone_number}")
            await client.sign_in(f"{phone_number}", code=code, phone_code_hash=result.phone_code_hash)
        except PhoneNumberUnoccupiedError as error:
            await client.disconnect()
            return jsonify(error), 403

        me = await client.get_me()
        
        await client.disconnect()

        return jsonify(me.stringify()), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

@app.route("/message", methods=["POST"])
async def message():
    try:
        phone_number = request.json["phonenumber"]
        number = request.json["number"]
        message = request.json["message"]

        record_filepath = os.path.abspath(f"records/{phone_number}")

        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)
        await client.connect()
        await client.send_message(f"{number}", f"{message}")
        await client.disconnect()

        return jsonify(True), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

@app.route("/revoke", methods=["POST"])
async def revoke():
    try:
        phone_number = request.json["phonenumber"]

        record_filepath = os.path.abspath(f"records/{phone_number}")

        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)
        await client.connect()
        await client.log_out()
        await client.disconnect()
        shutil.rmtree(record_filepath)

        return jsonify(True), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

@app.route("/contacts", methods=["POST"])
async def contacts():
    try:
        phone_number = request.json["phonenumber"]
        contacts = []

        record_filepath = os.path.abspath(f"records/{phone_number}")

        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)
        await client.connect()\
        
        result = await client(functions.contacts.GetContactsRequest(hash=0))
        for user in result.users:
            contacts.append({
                "id": user.id,
                "phone": user.phone,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            })

        await client.disconnect()

        return jsonify(contacts), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

@app.route("/dialogs", methods=["POST"])
async def dialogs():
    try:
        phone_number = request.json["phonenumber"]
        dialogs = []

        record_filepath = os.path.abspath(f"records/{phone_number}")

        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)
        await client.connect()\
        
        result = await client.get_dialogs()        
        for dialog in result:
            dialogs.append({
                "name": dialog.name,
                "id": dialog.entity.id,
                "message": {
                    "id": dialog.message.id,
                    "text": dialog.message.message,
                    "date":dialog.message.date
                },
                "date": dialog.date,
                "type": "chat" if not hasattr(dialog.entity, "title") else "channel"
            })

        await client.disconnect()

        return jsonify(dialogs), 200
    except Exception as error:
        await client.disconnect()
        return str(error), 500

if __name__ == "__main__":
    app.run(port=3000)