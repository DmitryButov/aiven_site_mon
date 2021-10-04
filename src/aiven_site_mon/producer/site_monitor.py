import os, time
import requests
import re

from aiven_site_mon.common import Logger, timeit
from .load_balancer import LoadBalancer

def check_site_worker(site):
    try:
        checker = SiteChecher(site)
        response = checker.request()
        search_result = checker.search_pattern_in(response)
        info = checker.prepare_info(response, search_result)
        SiteChecher.print_info(info)
        return info

    except Exception as e:
        Logger.error("Exception in worker when handling site {} : {}".format(site, e))
        return {}

def info_results_handler(list):
    for info in list:
        SiteChecher.print_info(info)
        #TODO send in one packet info about sites to Kafka

class SiteChecher:
    def __init__(self, site):
        self.__site = site

    @timeit
    def request(self):
        url = self.__site.get_url()
        Logger.trace("GET request to url: " + url)
        try:
            response = requests.get(url)
        except (requests.exceptions.ConnectionError, ConnectionResetError):
            Logger.error("Connection error for url: {}".format(url))
            return None
        return response

    @timeit
    def search_pattern_in(self, response):
        if not response:
            return None
        pattern = self.__site.get_pattern()
        if not pattern:
            return None
        regex = re.compile(pattern)
        if regex.groups != 1:
            return "<wrong pattern>"
        result = regex.search(response.text)
        return result.group(1) if result else None

    def prepare_info(self, response, search_result):
        info = {}
        info['url'] = self.__site.get_url()
        if response:
            info['status'] = 'done'
            info['status_code'] = response.status_code
            info['access_time'] = response.elapsed.total_seconds()
            info['search_result'] = search_result
        else:
            info['status'] = 'error'
            info['status_code'] = 0
            info['access_time'] = 0
            info['search_result'] = None
        return info

    @staticmethod
    def print_info(info):
        if not info:
            return
        line = '{:<70}{:<7}{:<5}{:<7.3f}{}'.format(
            info['url'],
            info['status'],
            info['status_code'],
            info['access_time'],
            info['search_result'] if info['search_result'] else ""
            )
        Logger.info(line)


class SiteMonitor:
    def __init__(self, site_list, update_period_sec, load_balancing_policy=LoadBalancer.ROUND_ROBIN, processes=os.cpu_count()) -> None:
        self.__load_balancer = LoadBalancer(load_balancing_policy,
                                            update_period_sec,
                                            check_site_worker,
                                            site_list,
                                            info_results_handler,
                                            processes)

    def monitoring(self):
        self.__load_balancer.do_work()

    def stop(self):
        Logger.info("Monitor stopping...")
        self.__load_balancer.stop()
        Logger.info("Monitor stopped")
