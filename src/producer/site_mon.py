import sys, os, time
import requests
import re, json
import concurrent.futures

DEFAULT_SETTINGS_FILENAME = "settings.json"

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

class SiteMonitor:
    def __init__(self, site_list) -> None:
        self.__site_list = site_list

    def __search_pattern(self, pattern, text):
        if not pattern:
            return False
        regex = re.compile(pattern)
        result = regex.search(text)
        return result.group(0) if result else None

    def check_site(self, site):
        url = site.get_url()
        pattern = site.get_pattern()
        response = requests.get(url)
        access_time = response.elapsed.total_seconds()
        info = '{:<70}{:<5}{:<7.3f}'.format(url, response.status_code, access_time)
        search_result = self.__search_pattern(pattern, response.text)
        if search_result:
            info += search_result
        return info

    @timeit
    def check(self):
        info_it = map(self.check_site, self.__site_list)
        for info in list(info_it):
            print(info)

    @timeit
    def parallel_check(self):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            info_it = executor.map(self.check_site, self.__site_list)
        for info in list(info_it):
            print(info)

@timeit
def main():
    print("Load settings")
    settings_manager = SettingsManager()
    if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
        return

    print("Working...")
    site_list = settings_manager.get_site_list()
    site_mon = SiteMonitor(site_list)
    #site_mon.check()
    site_mon.parallel_check()

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('exit...')
