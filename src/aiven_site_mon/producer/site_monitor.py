import os, time, signal
import multiprocessing

import requests
import re

from aiven_site_mon.common import Logger, timeit

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    multiprocessing.current_process().name = "Worker-{}".format(os.getpid())

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
    UPDATE_MIN_SEC = 1
    PROCESSES_MIN = 1
    PROCESSES_MAX = 50
    MAX_PARSING_TIME_SEC = 180

    def __init__(self, site_list, update_period_sec, processes=os.cpu_count()) -> None:
        self.__site_list = site_list
        self.__update_period_sec = update_period_sec
        self.__processes = processes
        if self.__update_period_sec < self.UPDATE_MIN_SEC: self.__update_period_sec = self.UPDATE_MIN_SEC
        if self.__processes < self.PROCESSES_MIN: self.__processes = self.PROCESSES_MIN
        if self.__processes > self.PROCESSES_MAX: self.__processes = self.PROCESSES_MAX
        self.__process_pool = multiprocessing.Pool(self.__processes, initializer=init_worker)

    #for debug purposes
    # def __check(self):
    #     info_it = map(check_site_worker, self.__site_list)
    #     for info in list(info_it):
    #          logger.info(info)

    @timeit
    def __parallel_check(self):
        Logger.debug("parallel_check started! (use {} processes)...".format(self.__processes))
        try:
            async_info_it = self.__process_pool.map_async(check_site_worker, self.__site_list)
            info_it = async_info_it.get(self.MAX_PARSING_TIME_SEC)
            info_handler(list(info_it))
        except multiprocessing.TimeoutError:
            Logger.error("Error: parsing timeout is achieved!")

    def monitoring(self):
        time.sleep(self.__update_period_sec)
        Logger.trace("monitoring...")
        self.__parallel_check()
        #self.check()

    def stop(self):
        Logger.info("Monitor stopping...")
        self.__process_pool.close()
        self.__process_pool.join()
        Logger.info("Monitor stopped")
