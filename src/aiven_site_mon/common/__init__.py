APP_LOGGER_NAME = "site_mon"

#TODO use automatic appoach, create extarnbal _version.py file and use it here and inside setup,py
APP_VERSION = '0.1'  # note: check also setup.py!

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