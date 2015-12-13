import logging
import termcolor

class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super(ColoredFormatter, self).__init__(
            '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - ' +
            '%(message)s')

    @staticmethod
    def get_color(record):
        return {
            logging.INFO:    'white',
            logging.WARNING: 'yellow',
            logging.ERROR:   'red',
        }.get(record.levelno)

    def format(self, record):
        return termcolor.colored(
            super(ColoredFormatter, self).format(record),
            ColoredFormatter.get_color(record))


def init(logger):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())
    logger.addHandler(handler)
