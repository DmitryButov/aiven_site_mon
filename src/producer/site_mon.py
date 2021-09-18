
import requests
import re

sites = [
    'https://example.com',
    'https://postgrespro.ru',
    'https://www.postgresql.org',
    'https://aiven.io/',
    'https://aiven.io/about',
    'https://www.google.com/search?q=aiven',
    'https://yandex.ru/search/?lr=51&text=aiven',
    'https://github.com/aiven/aiven-examples/',
    'https://medium.com/',
    'https://medium.com/@rinu.gour123/kafka-for-beginners-74ec101bc82d',
    'https://www.youtube.com/watch?v=YKXCRs_P-xU',
]

#find_regex = '<h1>(.+)</h1>'
find_regex = '<title>(.+)</title>'

def search(pattern, text):
    if not pattern: 
        return False
    result = pattern.search(text)
    return result.group(0) if result else None

def main():
    pattern = re.compile(find_regex) if find_regex else None 
    for site in sites:
        response = requests.get(site)
        access_time = response.elapsed.total_seconds()
        info = '{:<70}{:<5}{:<7.3f}'.format(site, response.status_code, access_time)
        search_result = search(pattern, response.text)
        if search_result:
            info += search_result
        print(info)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('exit...')
