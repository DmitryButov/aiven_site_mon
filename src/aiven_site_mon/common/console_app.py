import time
import argparse
from . import APP_VERSION
from . import log_manager, Logger
from . import timeit
from .settings_manager import SettingsManager

def __parse_console_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + APP_VERSION)
    parser.add_argument('-m', '--mode', default='console', metavar='<value>',
                        help='operating mode selection: console, kafka-producer, kafka-consumer')
    parser.add_argument('-s', '--settings', required=True, metavar='<filename.json>',
                        help='path to settings file in JSON format')
    parser.add_argument('-l', '--log_level', default='INFO', metavar='<level>',
                        help='set log level: TRACE, DEBUG, INFO, WARNING, etc.')
    return parser.parse_args()

def __monitoring():
    Logger.info('TODO monitoring')

@timeit
def main():
    args = __parse_console_args()
    log_manager.create_trace_level()            #useful for developing
    log_manager.init(Logger, args.log_level)

    settings_manager = SettingsManager()
    if not settings_manager.load(args.settings):
        return

    if args.mode == 'console':
        site_list = settings_manager.get_site_list()
        for item in site_list:
            Logger.trace(item)
        process_func = __monitoring
    elif args.mode == 'kafka-producer':
        Logger.warning('kafka-producer mode is under developing')
        #process_func = __monitoring2
        return
    elif args.mode == 'kafka-consumer':
        Logger.warning('kafka-consumer mode is under developing')
        #process_func = __listener
        return
    else:
        Logger.error('Wrong operation mode!')
        return

    Logger.info('TODO Working...')
    try:
        while True:
            process_func()
            time.sleep(1)
    except KeyboardInterrupt:
        #stop
        Logger.info('exit')
