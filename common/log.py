import logging
import termcolor

class CustomFormatter(logging.Formatter):
    def __init__(self, colored):
        super(CustomFormatter, self).__init__(
            '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - ' +
            '%(message)s')
        self.colored = colored

    @staticmethod
    def get_color(record):
        return {
            logging.INFO:    'white',
            logging.WARNING: 'yellow',
            logging.ERROR:   'red',
        }.get(record.levelno)

    def format(self, record):
        base = super(CustomFormatter, self).format(record)
        if self.colored:
            return termcolor.colored(base, CustomFormatter.get_color(record))
        else:
            return base


def init(logger, colored):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(colored))
    logger.addHandler(handler)
