from os import path, environ
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class BaseConfig(object):
    # Main settings
    DEBUG = True
    TESTING = False
    SECRET_KEY = environ.get('FLASK_APP_SECRET_KEY')

    # Database settings
    DB_HOST = environ.get('FLASK_APP_DB_HOST')
    DB_PORT = environ.get('FLASK_APP_DB_PORT')
    DB_USER = environ.get('FLASK_APP_DB_USER')
    DB_PASSWORD = environ.get('FLASK_APP_DB_PASSWORD')
    DB_NAME = environ.get('FLASK_APP_DB_NAME')
    DB_PREFIX = environ.get('FLASK_APP_DB_PREFIX')

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = f'{DB_PREFIX}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SESSION_COOKIE_SECURE = False


class DevConfig(BaseConfig):
    ENV = 'development'


class TestConfig(BaseConfig):
    ENV = 'test'
    DEBUG = False
    TESTING = True


class ProdConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False

    SESSION_COOKIE_SECURE = True


def configure_application(app):
    config_name = environ.get('FLASK_ENV', 'development')
    config = dict(
        development='project.settings.DevConfig',
        production='project.settings.ProdConfig',
        test='project.settings.TestConfig'
    )
    app.config.from_object(config[config_name])
