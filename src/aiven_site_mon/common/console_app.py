import time
import argparse
from . import APP_VERSION
from . import log_manager, Logger
from . import timeit
from .settings_manager import SettingsManager
from aiven_site_mon.producer import SiteMonitor



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

def activate_console_producer(settings_manager):
    site_list = settings_manager.get_procuder_site_list()
    if len(site_list) == 0:
        Logger.warning("site list can't be empty")
        return (False, None, None)

    site_mon = SiteMonitor(site_list,
                           settings_manager.get_update_period(),
                           settings_manager.get_load_balancing_policy())

    return (True, site_mon.monitoring, site_mon.stop)

@timeit
def main():
    args = __parse_console_args()
    log_manager.create_trace_level()            #useful for developing
    log_manager.init(Logger, args.log_level)

    settings_manager = SettingsManager()
    if not settings_manager.load(args.settings):
        return

    if args.mode == 'console':
        activate_status, process_func, stop_func = activate_console_producer(settings_manager)
    elif args.mode == 'kafka-producer':
        Logger.warning('kafka-producer mode is under developing')
        activate_status = False
        #process_func = monitoring2
        #stop_func = stop2
        return
    elif args.mode == 'kafka-consumer':
        Logger.warning('kafka-consumer mode is under developing')
        activate_status = False
        #process_func = listener
        #stop_func = stop3
        return
    else:
        Logger.error('Wrong operation mode!')
        return

    if not activate_status:
        return

    Logger.trace('Start working...')
    try:
        while True:
            process_func()
    except KeyboardInterrupt:
        stop_func()
        Logger.trace('exit')
