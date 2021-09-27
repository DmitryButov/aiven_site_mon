import logging
from . import APP_LOGGER_NAME
from . import log_manager

logger = logging.getLogger().getChild(APP_LOGGER_NAME)

def main():
    log_manager.create_trace_level(logging)  #TODO use only for developing
    log_manager.init(logger, logging.TRACE)

    logger.debug("debug msg")
    logger.warning("warn msg")
    logger.trace("trace msg")
