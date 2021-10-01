import logging, time
import argparse
from . import APP_LOGGER_NAME, APP_VERSION
from . import log_manager
from .settings_manager import SettingsManager

logger = logging.getLogger().getChild(APP_LOGGER_NAME)

def parse_console_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + APP_VERSION)
    parser.add_argument('-m', '--mode', default='console', metavar='<value>',
                        help='operating mode selection: console, kafka-producer, kafka-consumer')
    parser.add_argument('-s', '--settings', required=True, metavar='<filename.json>',
                        help='path to settings file in JSON format')
    parser.add_argument('-l', '--log_level', default='INFO', metavar='<level>',
                        help='set log level: TRACE, DEBUG, INFO, WARNING, etc.')
    return parser.parse_args()


def main():
    args = parse_console_args()
    log_manager.create_trace_level(logging)  #TODO use only for developing
    log_manager.init(logger, args.log_level)

    settings_manager = SettingsManager()
    if not settings_manager.load(args.settings):
        return

    #simple check for settings:
    site_list = settings_manager.get_site_list()
    for item in site_list:
        logger.trace(item)

    #TODO prepare to work
    logger.info('TODO Working...')
    try:
        while True:
            logger.info('TODO monitoring')
            time.sleep(1)
    except KeyboardInterrupt:
        #stop
        logger.info('exit')
