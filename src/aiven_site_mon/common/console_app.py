import logging, time
from . import APP_LOGGER_NAME
from . import log_manager

logger = logging.getLogger().getChild(APP_LOGGER_NAME)

def main():
    log_manager.create_trace_level(logging)  #TODO use only for developing
    log_manager.init(logger, logging.TRACE)

    logger.info("TODO Load settings")

    #TODO working with cli args:
    #- load setting json file from path from arg
    #- select working mode (producer or consumer)

    #TODO prepate to work
    logger.info("TODO Working...")
    try:
        while True:
            logger.info("Do monitoring")
            time.sleep(1)
    except KeyboardInterrupt:
        #stop
        logger.info("exit")
