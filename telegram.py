#!/usr/bin/env python3

import os
import sys
import logging
from inspect import getsourcefile
from os.path import abspath

dir_path = os.path.dirname(abspath(getsourcefile(lambda:0)))
sys.path.insert(0, dir_path)

from methods import Methods
import asyncio
logging.basicConfig(level='DEBUG')

async def run(body: str, user_details: dict)->None:
    body = body.split(":")

    sender_phonenumber = user_details['token']
    phonenumber = body[0]
    message = ":".join(body[1:])

    try:
        telegram = Methods(identifier=sender_phonenumber)
        await telegram.message(recipient=phonenumber, text=message)
    except Exception as error:
        logging.exception(error)
        raise error

def execute(body: str, user_details: dict)->None:
    """
    <phone_number>:<body>
    """

    try:
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # future = asyncio.ensure_future(run(body, user_details))
        loop.close()
        """
        asyncio.run(run(body, user_details))
    except Exception as error:
        raise error


if __name__ == "__main__":
    user_details = {"phone_number": sys.argv[2]}
    body = sys.argv[1] +":Please let me know if you receive this"

