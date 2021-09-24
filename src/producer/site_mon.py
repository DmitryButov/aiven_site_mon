import sys, os, time, signal
import requests
import re, json
import multiprocessing

DEFAULT_SETTINGS_FILENAME = "settings.json"
DEFAULT_UPDATE_PERIOD_SEC = 3

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print("Debug: [pid={}] Func ""{}"" done at {:.3f} seconds".format(os.getpid(),  func.__name__, duration))
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
        print('load settings from file: ' + filename)
        if not os.path.isfile(filename):
            print('Error: no settings file found!')
            return False
        try:
            with open(filename, "r") as read_file:
                self.__settings = json.load(read_file)
        except json.decoder.JSONDecodeError:
            print("Error: wrong settings file format")
            return False
        return True

    def get_site_list(self):
        site_list = []
        try:
            for item in self.__settings['sites']:
                site_list.append(Site(item['url'], item['pattern']))
        except:
            print('Error: wrong settings')
        return site_list

@timeit
def search_pattern(pattern, text):
    if not pattern:
        return False
    regex = re.compile(pattern)
    result = regex.search(text)
    return result.group(0) if result else None

@timeit
def get_resp(url):
    response = requests.get(url)
    return response

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def check_site_worker(site):
    url = site.get_url()
    pattern = site.get_pattern()
    response = get_resp(url)
    access_time = response.elapsed.total_seconds()
    info = '{:<70}{:<5}{:<7.3f}'.format(url, response.status_code, access_time)

    search_result = search_pattern(pattern, response.text)
    if search_result:
       info += search_result

    return info

class SiteMonitor:
    def __init__(self, site_list, processes=os.cpu_count()) -> None:
        self.__site_list = site_list
        self.__update_period = DEFAULT_UPDATE_PERIOD_SEC
        self.__processes = processes
        self.__process_pool = multiprocessing.Pool(self.__processes, initializer=init_worker)

    def check(self):
        info_it = map(check_site, self.__site_list)
        for info in list(info_it):
            print(info)

    @timeit
    def parallel_check(self):
        print("parallel_check started! (use {} processes)".format(self.__processes))
        info_it = self.__process_pool.map(check_site_worker, self.__site_list)
        for info in list(info_it):
            print(info)

    def start(self, update_period):
        print("Monitor starting...")
        self.__update_period = update_period

    def monitoring(self):
        time.sleep(self.__update_period)
        #self.check()
        self.parallel_check()

    def stop(self):
        print("Monitor stopping...")
        self.__process_pool.close()
        self.__process_pool.join()
        print("Monitor stopped")

@timeit
def main():
    print("Load settings")
    settings_manager = SettingsManager()
    if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
        return

    print("Working...")
    site_list = settings_manager.get_site_list()
    site_mon = SiteMonitor(site_list)

    try:
        site_mon.start(DEFAULT_UPDATE_PERIOD_SEC)
        while True:
            site_mon.monitoring()
    except KeyboardInterrupt:
        site_mon.stop()
        print('---exit---')

if __name__ == '__main__':
        main()
