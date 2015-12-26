import log
import logging

class State(object):
    @staticmethod
    def add_params(parser):
        parser.add_argument(
            '-H', metavar='HOST', help='Host(s) to deploy',
            default=[], action='append')
        parser.add_argument(
            '-g', metavar='GROUP', help='Group(s) to deploy',
            default=[], action='append')
        parser.add_argument(
            '-C', help='Colored log output', default=False, action='store_true')

    def __init__(self, parser, args):
        self.hosts, self.groups = args.H, args.g
        if len(self.hosts) == 0 and len(self.groups) == 0:
            parser.error('at least one host or group should be specified')

        self.active_hosts = set()
        self.failed_hosts = set()
        self.all_failed_hosts = set()
        log.init(self.log, args.C)

    @property
    def log(self):
        return logging.getLogger(__name__)
