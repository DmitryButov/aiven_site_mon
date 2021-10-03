import pathlib
import json
from . import Logger, Site

DEFAULT_LOAD_BALANCING_POLICY = 'round_robin'

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

    def get_load_balancing_policy(self):
        allowed_policies = ['round_robin', 'compressed']
        producer = self.__settings['producer']
        if 'load_balancing_policy' in producer:
            if producer['load_balancing_policy'] in allowed_policies:
                return producer['load_balancing_policy']
            else:
                Logger.warning('Unsupported load_balancing_policy! Check settings file. Use default ({})'
                            .format(DEFAULT_LOAD_BALANCING_POLICY))
                return DEFAULT_LOAD_BALANCING_POLICY
        else:
            return DEFAULT_LOAD_BALANCING_POLICY
