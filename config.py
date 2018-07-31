import os


# default config
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = '\x1al\td\x0eq\xaaZ\x10k\xc7L\x94o\xc0]\xdf\x123\xc1\xf3D\xdf\x1f'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///toast.db' #os.environ['DATABASE_URL']


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False