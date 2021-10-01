import logging

#For developing only! - Add TRACE log level and Logger.trace() method.
def create_trace_level(logging):
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, 'TRACE')
    def _trace(logger, message, *args, **kwargs):
        if logger.isEnabledFor(logging.TRACE):
            logger._log(logging.TRACE, message, args, **kwargs)
    logging.Logger.trace = _trace

def init(logger, level, show_timemark=True):
    try:
        logger.setLevel(level)
    except ValueError:
        print('Warning: Wrong init logger level! Use INFO')
        level='INFO'
        logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    timemark = '%(asctime)s ' if show_timemark else ''
    format_str = timemark + '%(name)s %(levelname)-8s %(processName)-16s: %(message)s'
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
