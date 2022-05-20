import logging
import os
import shutil
import json
import random
import hashlib

from telethon import TelegramClient
from telethon.errors import (
    PhoneNumberUnoccupiedError, 
    PhoneCodeInvalidError, 
    PhoneCodeExpiredError, 
    SessionPasswordNeededError
)
from telethon.tl.types import InputPhoneContact
from telethon import functions, types
from configparser import ConfigParser
from error import Forbidden, InternalServerError, Conflict, RegisterAccount, UnprocessableEntity

logger = logging.getLogger(__name__)

config_filepath = os.path.join(
        os.path.dirname(__file__), '../configs', 'configs.ini')

if not os.path.exists(config_filepath):
    error = f"configs file not found at {config_filepath}"
    raise Exception(error)

config = ConfigParser()
config.read(config_filepath)

dev = config["DEV"]
api_id = dev['API_ID']
api_hash = dev['API_HASH']

def md5hash( data: str) -> str:
    """
    """
    try:
        return hashlib.md5(data.encode("utf-8")).hexdigest()
    except Exception as error:
        raise error

class TelegramApp:

    def __init__(self, phone_number) -> None:
        """
        """
        self.phone_number = phone_number

        phone_number_hash = md5hash(data = phone_number)
        self.record_filepath = os.path.join(
                    os.path.dirname(__file__), '../records', phone_number_hash)
        self.record_session_filepath = os.path.join(
                    os.path.dirname(__file__), '../records', phone_number_hash, phone_number_hash)

    async def initialization(self) -> None:
        """
        """
        try:
            if not os.path.exists(self.record_filepath):
                logging.debug("- creating user file: %s", self.record_filepath)
                os.makedirs(self.record_filepath)

            # initialize telethon client
            client = TelegramClient(self.record_session_filepath, api_id=api_id, api_hash=api_hash)

            # open telethon connection
            await client.connect()
            logging.debug("- connection created")

            # check if record has session already
            if not await client.is_user_authorized():
                # send out authorization code
                result = await client.send_code_request(phone=self.phone_number, force_sms=True)
                
                # writing phone_code_hash to registry
                self.__write_registry__(phone_code_hash=result.phone_code_hash)
                logger.info("- authentication code sent to: %s", self.phone_number)

            else:
                raise Conflict()

        except Exception as error:
            raise InternalServerError(error)

        finally:
            # close telethon connection
            await client.disconnect()

    def __write_registry__(self, phone_code_hash: str, code: str = None)->None:
        """
        """
        try:
            # Data to be written
            dictionary ={
                "code" : code,
                "phone_code_hash" : phone_code_hash
            }
      
            json_object = json.dumps(dictionary)
            
            # Writing to sample.json
            registery_filepath = self.record_filepath + "/registry.json"
            with open(registery_filepath, "w") as outfile:
                outfile.write(json_object)
            
            return True

        except Exception as error:
            raise InternalServerError(error)


    def __read_registry__(self) -> None:
        """
        """
        try:
            registery_filepath = self.record_filepath + "/registry.json"
            with open(registery_filepath, 'r') as openfile:
                json_object = json.load(openfile)
            
            os.remove(registery_filepath)
            logger.debug("- removed user registery file: %s", registery_filepath)

            return json_object

        except Exception as error:
            raise InternalServerError(error)
    

    async def validation(self, code: str) -> dict:
        """
        """
        try:
            # check if record exists
            if not os.path.exists(self.record_filepath):
                os.makedirs(self.record_filepath)

            # initialize telethon client
            client = TelegramClient(self.record_session_filepath, api_id=api_id, api_hash=api_hash)
            await client.connect()

            result = self.__read_registry__()

            # validate code
            await client.sign_in(self.phone_number, 
                    code=code, phone_code_hash=result["phone_code_hash"])
            logger.info("- Code validation successful")
            
            # get user profile info
            logger.debug("Fetching user's info ...")
            me = await client.get_me()

            return {
                "phone_number": self.phone_number,
                "profile": {
                    "id": me.id,
                    "phone": me.phone,
                    "username": me.username,
                    "first_name": me.first_name,
                    "last_name": me.last_name
                }
            }

        except PhoneNumberUnoccupiedError as error:
            logger.error(f"{self.phone_number} has no account")
            self.__write_registry__(code=code, phone_code_hash=result["phone_code_hash"])
            raise RegisterAccount()
        except PhoneCodeInvalidError as error:
            logger.error("The phone code entered was invalid")
            raise Forbidden()
        except PhoneCodeExpiredError as error:
            logger.error("The confirmation code has expired")
            raise Forbidden()
        except SessionPasswordNeededError as error:
            logger.error("wo-steps verification is enabled and a password is required")
            raise InternalServerError(error)
        except Exception as error:
            raise InternalServerError(error)
        finally:
            # close telethon connection
            logger.debug("closing connection ...")
            await client.disconnect()


    async def message(self, recipoent: str, text: str) -> bool:
        """
        """
        try:
            # initialize telethon client
            client = TelegramClient(self.record_session_filepath, api_id=api_id, api_hash=api_hash)
            await client.connect()

            # sent message
            logger.debug(f"sending message to {recipoent} ...")
            await client.send_message(f"{recipoent}", f"{text}")

            logger.info("- Successfully sent message")

            return True
        except ValueError as error:
            if str(error) == f'Cannot find any entity corresponding to "{recipoent}"':
                logger.error(error)
                
                try:
                    # add recipient to contact list
                    logger.debug(f"adding {recipoent} to contact list ...")
                    contact = InputPhoneContact(random.randint(0, 9999), recipoent, str(recipoent), "")
                    await client(functions.contacts.ImportContactsRequest([contact]))

                    logger.info(f"Succesfully added {recipoent} to contact list")
                    
                    # sent message
                    logger.debug(f"sending message to {recipoent} ...")
                    await client.send_message(f"{recipoent}", f"{text}")
                    
                    logger.info("- Successfully sent message")

                    return True
                except ValueError as error:
                    if str(error) == f'Cannot find any entity corresponding to "{recipoent}"':
                        logger.error(error)
                        raise UnprocessableEntity()
        except Exception as error:
            raise InternalServerError(error)
        finally:
            # close telethon connection
            logger.debug("closing connection ...")
            await client.disconnect()

async def revoke(phone_number):
    try:
        record_filepath = os.path.abspath(f"records/{phone_number}")

        # initialize telethon client
        logger.debug("initializing telethon ...")
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        # open telethon connection
        logger.debug("opening connection ...")
        await client.connect()

        # revoke access
        logger.debug(f"revoking {phone_number} access ...")
        await client.log_out()
        logger.debug("deleting deps ...")
        shutil.rmtree(record_filepath)

        logger.info("Successfully revoked access")
      
        return True

    except Exception as error:
        raise InternalServerError(error)
    finally:
        # close telethon connection
        logger.debug("closing connection ...")
        await client.disconnect()

async def register(phone_number, first_name, last_name):
    try:
        record_filepath = os.path.abspath(f"records/{phone_number}")

        registry_data = read_registry(phone_number)

        # initialize telethon client
        logger.debug("initializing telethon ...")
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        # open telethon connection
        logger.debug("opening connection ...")
        await client.connect()

        # validate code
        logger.debug(f"creating account for {phone_number} ...")
        await client.sign_up(code=registry_data["code"], first_name=first_name, last_name=last_name, phone=f"{phone_number}", phone_code_hash=registry_data["phone_code_hash"])

        logger.info("account successfully created")
        
        # get user profile info
        logger.debug("Fetching user's info ...")
        me = await client.get_me()

        return {
            "phone_number": phone_number,
            "profile": {
                "id": me.id,
                "phone": me.phone,
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name
            }
        }

    except PhoneCodeInvalidError as error:
        logger.error("The phone code entered was invalid")
        raise Forbidden()
    except PhoneCodeExpiredError as error:
        logger.error("The confirmation code has expired")
        raise Forbidden()
    except Exception as error:
        raise InternalServerError(error)
    finally:
        # close telethon connection
        logger.debug("closing connection ...")
        await client.disconnect()



async def contacts(phone_number):
    try:
        record_filepath = os.path.abspath(f"records/{phone_number}")

        # initialize telethon client
        logger.debug("initializing telethon ...")
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        # open telethon connection
        logger.debug("opening connection ...")
        await client.connect()

        # fetch telegram contacts
        contacts = []
        
        logger.debug(f"Fetching telegram contacts for {phone_number} ...")
        result = await client(functions.contacts.GetContactsRequest(hash=0))
        for user in result.users:
            contacts.append({
                "id": user.id,
                "phone": user.phone,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            })

        logger.info("Successfully fetched all telegram contacts")
      
        return contacts

    except Exception as error:
        raise InternalServerError(error)
    finally:
        # close telethon connection
        logger.debug("closing connection ...")
        await client.disconnect()

async def dialogs(phone_number):
    try:
        record_filepath = os.path.abspath(f"records/{phone_number}")

        # initialize telethon client
        logger.debug("initializing telethon ...")
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        # open telethon connection
        logger.debug("opening connection ...")
        await client.connect()

        # fetch all active dialogs
        dialogs = []
        
        logger.debug(f"Fetching all active dialogs for {phone_number} ...")
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

        logger.info("Successfully fetched all active dialogs")
      
        return dialogs

    except Exception as error:
        raise InternalServerError(error)
    finally:
        # close telethon connection
        logger.debug("closing connection ...")
        await client.disconnect()

async def message(phone_number, recipoent, text):
    try:
        record_filepath = os.path.abspath(f"records/{phone_number}")

        # initialize telethon client
        logger.debug("initializing telethon ...")
        client = TelegramClient(f"{record_filepath}/{phone_number}", api_id=api_id, api_hash=api_hash)

        # open telethon connection
        logger.debug("opening connection ...")
        await client.connect()

        # sent message
        logger.debug(f"sending message to {recipoent} ...")
        await client.send_message(f"{recipoent}", f"{text}")

        logger.info("Successfully sent message")
      
        return True

    except ValueError as error:
        if str(error) == f'Cannot find any entity corresponding to "{recipoent}"':
            logger.error(error)
            
            try:
                # add recipient to contact list
                logger.debug(f"adding {recipoent} to contact list ...")
                contact = InputPhoneContact(random.randint(0, 9999), recipoent, str(recipoent), "")
                await client(functions.contacts.ImportContactsRequest([contact]))

                logger.info(f"Succesfully added {recipoent} to contact list")
                
                # sent message
                logger.debug(f"sending message to {recipoent} ...")
                await client.send_message(f"{recipoent}", f"{text}")
                
                logger.info("Successfully sent message")

                return True
            except ValueError as error:
                if str(error) == f'Cannot find any entity corresponding to "{recipoent}"':
                    logger.error(error)
                    raise UnprocessableEntity()
    except Exception as error:
        raise InternalServerError(error)
    finally:
        # close telethon connection
        logger.debug("closing connection ...")
        await client.disconnect()

