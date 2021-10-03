import pathlib
import json
from . import Logger, Site

class SettingsManager:
    def __init__(self) -> None:
        self.__settings = {}

    def load(self, filename):
        path = pathlib.Path(filename)
        Logger.debug('Load settings from file: {}'.format(path))
        if not path.is_file():
            Logger.error('Settings file "{}" is not exist!'.format(path))
            return False

        try:
            with open(filename, "r") as read_file:
                self.__settings = json.load(read_file)
        except json.decoder.JSONDecodeError:
            Logger.error("wrong settings file format")
            return False
        return True

    def get_procuder_site_list(self):
        site_list = []
        try:
            for item in self.__settings['producer']['sites']:
                site_list.append(Site(item['url'], item['pattern']))
        except:
            Logger.warning('wrong site list content')
        return site_list
