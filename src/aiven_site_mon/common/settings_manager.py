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
    def __print_warning(param_name, default_value):
        Logger.warning('Wrong "{}" value. Please, check settings file. Reset to default ({})'
                        .format(param_name, default_value))

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
            return _DEFAULT_UPDATE_PERIOD_SEC
        val = producer['update_period_sec']
        if not isinstance(val, (int, float)) or val < 0:
            self.__print_warning('update_period_sec', _DEFAULT_UPDATE_PERIOD_SEC)
            return _DEFAULT_UPDATE_PERIOD_SEC
        return val

    def get_load_balancing_policy(self):
        producer = self.__settings['producer']
        allowed_policies = ['round_robin', 'compressed']
        if not 'load_balancing_policy' in producer:
            return _DEFAULT_LOAD_BALANCING_POLICY
        if producer['load_balancing_policy'] in allowed_policies:
            return producer['load_balancing_policy']
        else:
            self.__print_warning('load_balancing_policy', _DEFAULT_LOAD_BALANCING_POLICY)
            return _DEFAULT_LOAD_BALANCING_POLICY

    def get_process_count(self):
        producer = self.__settings['producer']
        if not 'process_count' in producer:
            return _DEFAULT_PROCESS_COUNT
        val = producer['process_count']
        if not isinstance(val, int) or val < 1:
            self.__print_warning('process_count', _DEFAULT_PROCESS_COUNT)
            return _DEFAULT_PROCESS_COUNT
        return val