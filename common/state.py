import log
import logging

class State(object):
    def __init__(self, group):
        self.group = group
        self.active_hosts = set()
        self.failed_hosts = set()
        self.all_failed_hosts = set()
        log.init(self.log)

    @property
    def log(self):
        return logging.getLogger(__name__)
