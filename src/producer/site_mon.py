import sys, os, time, signal
import requests
import re, json
import concurrent.futures, threading

DEFAULT_SETTINGS_FILENAME = "settings.json"
DEFAULT_UPDATE_PERIOD_SEC = 5

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print("Debug: Func ""{}"" done at {} seconds".format(func.__name__, duration))
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




# for testing we use non-class functions
def test_init():
    print("test initializer")

def test_check(site):
    try:
        time.sleep(2)
        print("inside test_check func")
        return "test_check: {}".format(site.get_url())
    except KeyboardInterrupt:
        return "sub-process exit on key"

def search_pattern(pattern, text):
    if not pattern:
        return False
    regex = re.compile(pattern)
    result = regex.search(text)
    return result.group(0) if result else None

def check_site(site):
    url = site.get_url()
    pattern = site.get_pattern()
    response = requests.get(url)
    access_time = response.elapsed.total_seconds()
    info = '{:<70}{:<5}{:<7.3f}'.format(url, response.status_code, access_time)
    search_result = search_pattern(pattern, response.text)
    if search_result:
        info += search_result
    return info

class SiteMonitor:
    def __init__(self, update_period_sec, site_list) -> None:
        self.__site_list = site_list
        self.__update_period = update_period_sec
        self.__update_thread = threading.Thread(target=self.monitoring)
        self.__exit_event = threading.Event()

        #self.__executor = concurrent.futures.ProcessPoolExecutor()
        self.__executor = concurrent.futures.ThreadPoolExecutor()

        #process pool executor gives
        #5.247151136398315 seconds
        #thread pool executor gives
        #3.9193339347839355 seconds

        #ussue - wrong handling of KeyboardInterrupt in workers...
        #TODO self.__executor = concurrent.futures.ProcessPoolExecutor(initializer=test_init)
        #we need to use initializer for disabling handling signal,
        #signal.signal(signal.SIGINT, signal.SIG_IGN)
        #but currant local version of my Python (3.6.9) is not support full impl of ProcessPoolExecutor
        #solutions:
        #- switch to modern Python (or/and use virtual env)
        #- use more control by multiprocessing Pool - see example on https://github.com/jreese/multiprocessing-keyboardinterrupt

    @timeit
    def check(self):
        info_it = map(check_site, self.__site_list)
        for info in list(info_it):
            print(info)

    @timeit
    def parallel_check(self):
        print("parallel_check started...")
        info_it = self.__executor.map(check_site, self.__site_list)  # TODO use check_site after testing
        for info in list(info_it):
            print(info)

    def monitoring(self):
        print("monitoring in thread...")
        while not self.__exit_event.wait(self.__update_period):
            self.parallel_check()

    def start(self):
        print("Monitor starting...")
        self.__update_thread.start()

    def stop(self):
        print("Monitor stopping...")
        self.__exit_event.set()
        self.__executor.shutdown(wait=True)  # we need to wait when all process is done
        self.__update_thread.join()  #wait for thread will be complete
        print("Monitor stopped")

@timeit
def main():
    print("Load settings")
    settings_manager = SettingsManager()
    if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
        return

    print("Working...")
    site_list = settings_manager.get_site_list()
    site_mon = SiteMonitor(DEFAULT_UPDATE_PERIOD_SEC, site_list)

    try:
        site_mon.start()
        while True:
            time.sleep(1)
            print(time.ctime(), " Main working... ")
    except KeyboardInterrupt:
        print(time.time(), "Main KeyboardInterrupt")
        site_mon.stop()
        print('---exit---')

if __name__ == '__main__':
        main()
