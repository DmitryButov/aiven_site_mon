import os, pathlib
import json
from . import Logger, Site

_DEFAULT_UPDATE_PERIOD_SEC = 3
_DEFAULT_LOAD_BALANCING_POLICY = 'round_robin'
_DEFAULT_PROCESS_COUNT= os.cpu_count()

class SettingsManager:
    def __init__(self) -> None:
        self.__settings = {}

    @staticmethod
    def __print_warning(param, default_value):
        Logger.warning('Wrong "{}" value. Please, check settings file. Reset to default ({})'
                        .format(param, default_value))

    def __get_producer_param(self, param, default):
        if not 'producer' in self.__settings:
            Logger.warning('Wrong settings. No producer settings')
            return None
        producer = self.__settings['producer']
        return producer[param] if param in producer else default

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

    def get_producer_site_list(self):
        site_list = []
        if not 'producer' in self.__settings:
            Logger.warning('Wrong settings. No producer settings')
            return site_list
        try:
            for item in self.__settings['producer']['sites']:
                site_list.append(Site(item['url'], item['pattern']))
        except:
            Logger.warning('Wrong site list content for producer')
        return site_list

    def get_update_period(self):
        param = 'update_period_sec'
        value = self.__get_producer_param(param, _DEFAULT_UPDATE_PERIOD_SEC)
        if not isinstance(value, (int, float)) or value < 0:
            self.__print_warning(param, _DEFAULT_UPDATE_PERIOD_SEC)
            return _DEFAULT_UPDATE_PERIOD_SEC
        return value

    def get_load_balancing_policy(self):
        param = 'load_balancing_policy'
        allowed_policies = ['round_robin', 'compressed']
        value = self.__get_producer_param(param, _DEFAULT_LOAD_BALANCING_POLICY)
        if not value in allowed_policies:
            self.__print_warning(param, _DEFAULT_LOAD_BALANCING_POLICY)
            return _DEFAULT_LOAD_BALANCING_POLICY
        return value

    def get_process_count(self):
        param = 'process_count'
        value = self.__get_producer_param(param, _DEFAULT_PROCESS_COUNT)
        if not isinstance(value, int) or value < 1:
            self.__print_warning(param, _DEFAULT_PROCESS_COUNT)
            return _DEFAULT_PROCESS_COUNT
        return value