import os
from configparser import ConfigParser

def configuration() -> dict:
    """
    """
    config_filepath = os.path.join(
            os.path.dirname(__file__), 'configs', 'configs.ini')

    if not os.path.exists(config_filepath):
        error = "configs file not found at %s" % config_filepath
        raise FileNotFoundError(error)

    config = ConfigParser()
    config.read(config_filepath)

    return {
        "DEV": config["DEV"],
        "API": config["API"]
    }
