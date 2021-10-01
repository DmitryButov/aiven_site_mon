# import sys, os, time, signal
# import logging
# import requests
# import re, json
# import multiprocessing

# import site_mon_logger

# DEFAULT_SETTINGS_FILENAME = "settings.json"
# DEFAULT_UPDATE_PERIOD_SEC = 3

# logger = logging.getLogger().getChild("site_mon")

# def timeit(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         duration = time.time() - start_time
#         logger.trace("Func ""{}"" done at {:.3f} seconds".format(func.__name__, duration))
#         return result
#     return wrapper


# @timeit
# def search_pattern(pattern, text):
#     if not pattern:
#         return None
#     regex = re.compile(pattern)
#     if regex.groups != 1:
#         return "<wrong pattern>"

#     result = regex.search(text)
#     return result.group(1) if result else None

# @timeit
# def request_to_url(url):
#     try:
#         response = requests.get(url)
#     except (requests.exceptions.ConnectionError, ConnectionResetError):
#         logger.error("Connection error for url: {}".format(url))
#         return None
#     return response

# def init_worker():
#     signal.signal(signal.SIGINT, signal.SIG_IGN)
#     multiprocessing.current_process().name = "Worker-{}".format(os.getpid())

# def check_site_worker(site):
#     url = site.get_url()
#     pattern = site.get_pattern()
#     response = request_to_url(url)
#     info = {}
#     info['url'] = url
#     if response:
#         info['status'] = 'done'
#         info['status_code'] = response.status_code
#         info['access_time'] = response.elapsed.total_seconds()
#         info['search_result'] = search_pattern(pattern, response.text)
#     else:
#         info['status'] = 'error'
#         info['status_code'] = 0
#         info['access_time'] = 0
#         info['search_result'] = None

#     return info

# def info_handler(list):
#     for info in list:
#         line = '{:<70}{:<7}{:<5}{:<7.3f}{}'.format(
#             info['url'],
#             info['status'],
#             info['status_code'],
#             info['access_time'],
#             info['search_result'] if info['search_result'] else ""
#             )
#         logger.info(line)
#         #TODO send in one packet info about sites to Kafka


# class SiteMonitor:
#     UPDATE_MIN_SEC = 1
#     PROCESSES_MIN = 1
#     PROCESSES_MAX = 50
#     MAX_PARSING_TIME_SEC = 180

#     def __init__(self, site_list, update_period_sec, processes=os.cpu_count()) -> None:
#         self.__site_list = site_list
#         self.__update_period_sec = update_period_sec
#         self.__processes = processes
#         if self.__update_period_sec < self.UPDATE_MIN_SEC: self.__update_period_sec = self.UPDATE_MIN_SEC
#         if self.__processes < self.PROCESSES_MIN: self.__processes = self.PROCESSES_MIN
#         if self.__processes > self.PROCESSES_MAX: self.__processes = self.PROCESSES_MAX
#         self.__process_pool = multiprocessing.Pool(self.__processes, initializer=init_worker)

#     #for debug purposes
#     def __check(self):
#         info_it = map(check_site_worker, self.__site_list)
#         for info in list(info_it):
#              logger.info(info)

#     @timeit
#     def __parallel_check(self):
#         logger.debug("parallel_check started! (use {} processes)...".format(self.__processes))
#         try:
#             async_info_it = self.__process_pool.map_async(check_site_worker, self.__site_list)
#             info_it = async_info_it.get(self.MAX_PARSING_TIME_SEC)
#             info_handler(list(info_it))
#         except multiprocessing.TimeoutError:
#             logger.error("Error: parsing timeout is achieved!")

#     def monitoring(self):
#         time.sleep(self.__update_period_sec)
#         #self.check()
#         self.__parallel_check()

#     def stop(self):
#         logger.info("Monitor stopping...")
#         self.__process_pool.close()
#         self.__process_pool.join()
#         logger.info("Monitor stopped")

# @timeit
# def main():
#     site_mon_logger.create_trace_loglevel(logging)
#     site_mon_logger.init(logger, logging.TRACE, show_timemark=True)

#     #init_logger(logging.TRACE, show_timemark=False)
#     logger.info("Load settings")
#     settings_manager = SettingsManager()
#     if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
#         return

#     logger.info("Working...")
#     site_list = settings_manager.get_site_list()
#     site_mon = SiteMonitor(site_list, DEFAULT_UPDATE_PERIOD_SEC)

#     try:
#         while True:
#             site_mon.monitoring()
#     except KeyboardInterrupt:
#         site_mon.stop()

# if __name__ == '__main__':
#         main()
