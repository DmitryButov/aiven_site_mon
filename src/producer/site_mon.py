import sys, os
import requests
import re, json

DEFAULT_SETTINGS_FILENAME = "settings.json"

class Site:
    def __init__(self, url, pattern):
        self.__url = url
        self.__pattern = pattern

    def get_url(self):
        return self.__url

    def get_pattern(self):
        return self.__pattern

    def __str__(self):
        return self.__url

class SettingsManager:
    def __init__(self):
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

def search(pattern, text):
    if not pattern:
        return False
    regex = re.compile(pattern)
    result = regex.search(text)
    return result.group(0) if result else None

def action(site):
    url = site.get_url()
    pattern = site.get_pattern()
    response = requests.get(url)
    access_time = response.elapsed.total_seconds()
    info = '{:<70}{:<5}{:<7.3f}'.format(url, response.status_code, access_time)
    search_result = search(pattern, response.text)
    if search_result:
        info += search_result
    return info

def main():
    settings_manager = SettingsManager()
    print("Load settings")
    if not settings_manager.load(DEFAULT_SETTINGS_FILENAME):
        return

    print("Working...")
    sites = settings_manager.get_site_list()
    info_it = map(action, sites)
    for info in list(info_it):
        print(info)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('exit...')
