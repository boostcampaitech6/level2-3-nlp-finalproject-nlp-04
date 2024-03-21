import sys
# from loguru import logger
import uuid
import os

USER = "KHAN"
LOG_DIR = "logs/user/"

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = None
    LOGURU_SETTINGS = {}

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    unique_key = str(uuid.uuid4())
    # os.makedirs(unique_key,exist_ok=True)
    log_path = os.path.join(unique_key,"file.log")
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} - {message}"},
            {"sink": log_path, "serialize": True},
        ],
        "extra": {"user": USER}
    }

class DevConfig(Config):
    DEBUG = True
    TESTING = True
    unique_key = str(uuid.uuid4())
    SAVE_DIR = os.path.join(LOG_DIR,unique_key)
    os.makedirs(SAVE_DIR,exist_ok=True)
    config = {
        "handlers": [
            {"sink": sys.stdout, "format" : "{name} | {extra[user]} | {file} | line : {line} | {level} | {time:YYYY-MM-DD at HH:mm:ss} | {message}"},
            {"sink": os.path.join(SAVE_DIR,"file.log"), "serialize": True},
        ],
        "extra": {"user": USER}
    }
