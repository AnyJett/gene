import logging
import colorlog


def log_with_different_color():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    datefmt = '%Y-%m-%d %H:%M:%S %p'
    fmt = '%(log_color)s%(asctime)s %(levelname)s[%(name)s] %(message)s'
    # black red green yellow blue purple cyan 和 white
    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'purple'
    }
    fmt = colorlog.ColoredFormatter(fmt, datefmt=datefmt, log_colors=log_colors)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    return logger


log = log_with_different_color()
