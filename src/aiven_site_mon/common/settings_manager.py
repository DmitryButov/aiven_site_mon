import pathlib
import json
import logging
from . import APP_LOGGER_NAME
from . import Site

logger = logging.getLogger().getChild(APP_LOGGER_NAME)

class SettingsManager:
    def __init__(self) -> None:
        self.__settings = {}

    def load(self, filename):
        path = pathlib.Path(filename)
        logger.debug('Load settings from file: {}'.format(path))
        if not path.is_file():
            logger.error('Settings file "{}" is not exist!'.format(path))
            return False

        try:
            with open(filename, "r") as read_file:
                self.__settings = json.load(read_file)
        except json.decoder.JSONDecodeError:
            logger.error("wrong settings file format")
            return False
        return True

    def get_site_list(self):
        site_list = []
        try:
            for item in self.__settings['sites']:
                site_list.append(Site(item['url'], item['pattern']))
        except:
            logger.warning('wrong site list content')
        return site_list