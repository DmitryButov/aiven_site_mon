
import sys, os
import requests
import re, json

g_settings_filename = "settings.json"

g_site_list = []

def load_settings():
    global g_settings_filename, g_site_list
    filename = os.path.join(sys.path[0], g_settings_filename)
    print('load settings from file: ' + filename)
    if not os.path.isfile(filename):
        print('Error: no settings file found!')
        return False
    try:
        with open(filename, "r") as read_file:
            g_settings = json.load(read_file)
        for site in g_settings['sites']:
            g_site_list.append( {'url': site['url'], 'pattern': site['pattern']} )
    except (json.decoder.JSONDecodeError, NameError):
        print("Error: wrong settings file format")
        return False
    except:
        print('Error: wrong settings')
        return False
    return True

def search(pattern, text):
    if not pattern:
        return False
    regex = re.compile(pattern)
    result = regex.search(text)
    return result.group(0) if result else None

def action(site):
    response = requests.get(site['url'])
    access_time = response.elapsed.total_seconds()
    info = '{:<70}{:<5}{:<7.3f}'.format(site['url'], response.status_code, access_time)
    search_result = search(site['pattern'], response.text)
    if search_result:
        info += search_result
    return info

def main():
    print("Load settings")
    if not load_settings():
        return

    print("Working...")
    info_it = map(action, g_site_list)
    for info in list(info_it):
        print(info)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('exit...')
