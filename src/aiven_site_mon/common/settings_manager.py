import pathlib
import json
from . import Logger, Site

DEFAULT_UPDATE_PERIOD_SEC = 3
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

    def get_update_period(self):
        producer = self.__settings['producer']
        if not 'update_period_sec' in producer:
            return DEFAULT_UPDATE_PERIOD_SEC
        val = producer['update_period_sec']
        if not isinstance(val, (int, float)) or val < 0:
            Logger.warning("Wrong update_period_sec value. Use default ({})"
                            .format(DEFAULT_UPDATE_PERIOD_SEC))
            return DEFAULT_UPDATE_PERIOD_SEC
        return val

    def get_load_balancing_policy(self):
        allowed_policies = ['round_robin', 'compressed']
        producer = self.__settings['producer']
        if not 'load_balancing_policy' in producer:
            return DEFAULT_LOAD_BALANCING_POLICY

        if producer['load_balancing_policy'] in allowed_policies:
            return producer['load_balancing_policy']
        else:
            Logger.warning('Unsupported load_balancing_policy! Check settings file. Use default ({})'
                            .format(DEFAULT_LOAD_BALANCING_POLICY))
            return DEFAULT_LOAD_BALANCING_POLICY
