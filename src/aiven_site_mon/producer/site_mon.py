# import sys, os, time, signal
# import logging
# import requests
# import re, json
# import multiprocessing

# import site_mon_logger

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







# @timeit
# def main():
#     logger.info("Working...")
#     site_list = settings_manager.get_site_list()
#     site_mon = SiteMonitor(site_list, DEFAULT_UPDATE_PERIOD_SEC)

#     try:
#         while True:
#             site_mon.monitoring()
#     except KeyboardInterrupt:
#         site_mon.stop()
