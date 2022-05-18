import os
from configparser import ConfigParser
from error import InternalServerError

def configuration():
    config_filepath = os.path.join(
            os.path.dirname(__file__), 'configs', 'configs.ini')

    if not os.path.exists(config_filepath):
        error = f"configs file not found at {config_filepath}"
        raise InternalServerError(error)

    config = ConfigParser()
    config.read(config_filepath)

    return {
        "DEV": config["DEV"],
        "API": config["API"]
    }
