import sys, os, time, signal
import logging
import requests
import re, json
import multiprocessing

DEFAULT_SETTINGS_FILENAME = "settings.json"
DEFAULT_UPDATE_PERIOD_SEC = 3

#For developing only! - Add TRACE log level and Logger.trace() method.
def _create_trace_loglevel(logging):
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")
    def _trace(logger, message, *args, **kwargs):
        if logger.isEnabledFor(logging.TRACE):
            logger._log(logging.TRACE, message, args, **kwargs)
    logging.Logger.trace = _trace

_create_trace_loglevel(logging)
logger = logging.getLogger().getChild("site_mon")

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.trace("Func ""{}"" done at {:.3f} seconds".format(func.__name__, duration))
        return result
    return wrapper

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

class SettingsManager:
    def __init__(self) -> None:
        self.__settings = {}

    def load(self, settings_filename):
        filename = os.path.join(sys.path[0], settings_filename)
        logger.debug('load settings from file: ' + filename)
        if not os.path.isfile(filename):
            logger.error('no settings file found!')
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

@timeit
def search_pattern(pattern, text):
    if not pattern:
        return None
    regex = re.compile(pattern)
    if regex.groups != 1:
        return "<wrong pattern>"

    result = regex.search(text)
    return result.group(1) if result else None

@timeit
def request_to_url(url):
    try:
        response = requests.get(url)
    except (requests.exceptions.ConnectionError, ConnectionResetError):
        logger.error("Connection error for url: ", url)
        return None
    return response

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    multiprocessing.current_process().name = "Worker-{}".format(os.getpid())

def check_site_worker(site):
    url = site.get_url()
    pattern = site.get_pattern()
    response = request_to_url(url)
    if not response:
        return None   #TODO! fill info when connection is fail!

    info = {}
    info['url'] = url

    info['status_code'] = response.status_code
    info['access_time'] = response.elapsed.total_seconds()

    search_result = search_pattern(pattern, response.text)
    info['search_result'] = search_result
    return info

def info_handler(list):
    for info in list:
        line = '{:<70}{:<5}{:<7.3f}{}'.format(
            info['url'],
            info['status_code'],
            info['access_time'],
            info['search_result'] if info['search_result'] else ""
            )
        logger.info(line)
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
    def __check(self):
        info_it = map(check_site_worker, self.__site_list)
        for info in list(info_it):
             logger.info(info)

    @timeit
    def __parallel_check(self):
        logger.debug("parallel_check started! (use {} processes)...".format(self.__processes))
        try:
            async_info_it = self.__process_pool.map_async(check_site_worker, self.__site_list)
            info_it = async_info_it.get(self.MAX_PARSING_TIME_SEC)
            info_handler(list(info_it))
        except multiprocessing.TimeoutError:
            logger.debug("Error: parsing timeout is achieved!")

    def monitoring(self):
        time.sleep(self.__update_period_sec)
        #self.check()
        self.__parallel_check()

    def stop(self):
        logger.info("Monitor stopping...")
        self.__process_pool.close()
        self.__process_pool.join()
        logger.info("Monitor stopped")

def init_logger(level, show_timemark=True):
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    timemark = '%(asctime)s ' if show_timemark else ''
    format_str = timemark + '%(name)s %(levelname)-8s %(processName)-16s: %(message)s'
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

@timeit
def main():
    init_logger(logging.TRACE, show_timemark=False)
    logger.info("Load settings")
    settings_manager = SettingsManager()
    if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
        return

    logger.info("Working...")
    site_list = settings_manager.get_site_list()
    site_mon = SiteMonitor(site_list, DEFAULT_UPDATE_PERIOD_SEC)

    try:
        while True:
            site_mon.monitoring()
    except KeyboardInterrupt:
        site_mon.stop()

if __name__ == '__main__':
        main()
