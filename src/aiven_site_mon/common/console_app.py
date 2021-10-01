import logging, time
import pathlib, argparse
from . import APP_LOGGER_NAME, APP_VERSION
from . import log_manager
import aiven_site_mon

logger = logging.getLogger().getChild(APP_LOGGER_NAME)

def main():
    log_manager.create_trace_level(logging)  #TODO use only for developing
    log_manager.init(logger, logging.TRACE)



    #TODO working with cli args:
    #- load setting json file from path from arg
    #- select working mode (producer or consumer)
    #- select log level (verbose level)

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s ' + APP_VERSION)
    parser.add_argument("-s", "--settings", type=pathlib.Path, default='settings.json',
                        help="path to settings file in JSON format")
    args = parser.parse_args()

    if not args.settings.is_file():
        logger.error('Settings file "{}" is not exist! Please, see usage with --help. Exit.'.format(args.settings))
        return

    logger.info('TODO Load settings from file: {}'.format(args.settings))




    #TODO prepate to work
    logger.info("TODO Working...")
    try:
        while True:
            logger.info("Do monitoring")
            time.sleep(1)
    except KeyboardInterrupt:
        #stop
        logger.info("exit")
