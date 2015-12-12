import sys

class Log(object):
    def info(self, message):
        print >> sys.stderr, message

    def warning(self, message):
        print >> sys.stderr, message

    def error(self, message):
        print >> sys.stderr, message


class State(object):
    def __init__(self, group):
        self.group = group
        self.active_hosts = set()
        self.failed_hosts = set()
        self.log = Log()
