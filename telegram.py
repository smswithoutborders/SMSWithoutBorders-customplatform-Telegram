#!/usr/bin/env python3

import sys
import logging
from src.telegram import TelegramApp
import asyncio
logging.basicConfig(level='DEBUG')

async def execute(body: str, user_details: dict)->None:
    """
    <phone_number>:<body>
    """

    body = body.split(":")

    sender_phonenumber = user_details['phone_number']
    phonenumber = body[0]
    message = ":".join(body[1:])

    try:
        telegram = TelegramApp(phone_number=sender_phonenumber)
        await telegram.message(recipient=phonenumber, text=message)
    except Exception as error:
        logging.exception(error)
        raise error


async def run(body, user_details):
    await execute(body=body, user_details = user_details)

if __name__ == "__main__":
    user_details = {"phone_number": sys.argv[2]}
    body = sys.argv[1] +":Please let me know if you receive this"

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(execute(body, user_details))
    loop.run_forever()
    loop.close()
