from .base import *

SECRET_KEY = ''
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbName',
        'USER': 'userName',
        'PASSWORD': 'userPass',
        'HOST': 'hostName',
        'PORT': '3306',
    }
}

