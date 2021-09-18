
import requests
import re

sites = [
    { 'url': 'https://example.com', 'pattern': '<h1>(.+)</h1>' },
    { 'url': 'https://postgrespro.ru', 'pattern': '<title>(.+)</title>' },
    { 'url': 'https://www.postgresql.org', 'pattern': ''},
#    'https://aiven.io/',
#    'https://aiven.io/about',
#    'https://www.google.com/search?q=aiven',
#    'https://yandex.ru/search/?lr=51&text=aiven',
#    'https://github.com/aiven/aiven-examples/',
#    'https://medium.com/',
#    'https://medium.com/@rinu.gour123/kafka-for-beginners-74ec101bc82d',
#    'https://www.youtube.com/watch?v=YKXCRs_P-xU',
]

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
    print("Working...")
    info_it = map(action, sites)
    for info in list(info_it):
        print(info)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('exit...')
