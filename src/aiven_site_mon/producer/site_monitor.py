import os, time
import requests
import re

from aiven_site_mon.common import Logger, timeit
from .load_balancer import LoadBalancer

@timeit
def request_to_url(url):
    Logger.trace("GET request to url: " + url)
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, ConnectionResetError):
        Logger.error("Connection error for url: {}".format(url))
        return None
    return response

@timeit
def search_pattern(pattern, text):
    if not pattern:
        return None
    regex = re.compile(pattern)
    if regex.groups != 1:
        return "<wrong pattern>"

    result = regex.search(text)
    return result.group(1) if result else None

def check_site_worker(site):
    #TODO сreate class SiteChecker
    url = site.get_url()
    pattern = site.get_pattern()
    response = request_to_url(url)
    info = {}
    info['url'] = url
    if response:
        info['status'] = 'done'
        info['status_code'] = response.status_code
        info['access_time'] = response.elapsed.total_seconds()
        info['search_result'] = search_pattern(pattern, response.text)
    else:
        info['status'] = 'error'
        info['status_code'] = 0
        info['access_time'] = 0
        info['search_result'] = None

    return info

def info_handler(list):
    for info in list:
        line = '{:<70}{:<7}{:<5}{:<7.3f}{}'.format(
            info['url'],
            info['status'],
            info['status_code'],
            info['access_time'],
            info['search_result'] if info['search_result'] else ""
            )
        Logger.info(line)
        #TODO send in one packet info about sites to Kafka

class SiteMonitor:
    __MIN_UPDATE_PERIOD_SEC = 1

    def __init__(self, site_list, update_period_sec, processes=os.cpu_count()) -> None:
        if update_period_sec < self.__MIN_UPDATE_PERIOD_SEC:
            update_period_sec = self.__MIN_UPDATE_PERIOD_SEC
        self.__update_period_sec = update_period_sec
        self.__load_balancer = LoadBalancer(check_site_worker, site_list, info_handler, processes)

    def monitoring(self):
        start_time = time.time()

        Logger.info("monitoring...")
        self.__load_balancer.do_work()

        work_duration = time.time() - start_time
        delay = self.__update_period_sec - work_duration
        Logger.info("sleep to {:.3f}".format(delay))
        if delay > 0:
            time.sleep(delay)
        else:
            Logger.warning("Processing takes a long time ({:.3f}sec). Please, increase update period."
                            .format(work_duration))

    def stop(self):
        Logger.info("Monitor stopping...")
        self.__load_balancer.stop()
        Logger.info("Monitor stopped")
