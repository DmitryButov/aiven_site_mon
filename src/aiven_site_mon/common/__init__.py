import time
import logging

APP_LOGGER_NAME = "site_mon"

#TODO use automatic appoach, create extarnbal _version.py file and use it here and inside setup,py
APP_VERSION = '0.1'  # note: check also setup.py!

Logger = logging.getLogger().getChild(APP_LOGGER_NAME)

class Site:
    def __init__(self, url, pattern) -> None:
        self.__url = url
        self.__pattern = pattern

    def get_url(self):
        return self.__url

    def get_pattern(self):
        return self.__pattern

    def __str__(self):
        return self.__url

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        Logger.trace("Function ""{}"" done at {:.3f} seconds".format(func.__name__, duration))
        return result
    return wrapper