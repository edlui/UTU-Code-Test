from os import environ, path
from dotenv import load_dotenv

APP_ROOT = path.dirname(path.abspath(__file__))
print(APP_ROOT)
load_dotenv(path.join(APP_ROOT, '.env'))

class Config(object):

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')

    # Mongo DB
    MONGO_URI = environ.get('MONGO_URI')
