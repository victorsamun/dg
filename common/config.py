import argparse

import stage
from util import amt_creds, proc

class Option(object):
    description = 'Deploy some machines'
    requirements = []

    @staticmethod
    def add_common_params(parser, methods):
        parser.add_argument(
            '-g', metavar='GROUP', help='Group to deploy', required=True)
        parser.add_argument(
            '-m', choices=[method.name for method in methods],
            help='Deploy method', required=True)

    @staticmethod
    def choose_method(methods, raw_args):
        names = dict((m.name, m) for m in methods)
        parser = argparse.ArgumentParser(description=Option.description)
        Option.add_common_params(parser, methods)
        Option.add_all(parser)
        args = parser.parse_args(raw_args)
        return names[args.m]

    @staticmethod
    def get_method_args(method, raw_args):
        parser = argparse.ArgumentParser(description=Option.description)
        Option.add_common_params(parser, [method])
        Option.add_required(parser, method)
        return parser.parse_args(raw_args)

    @staticmethod
    def requires(*args, **kwargs):
        def ret(cls):
            Option.requirements.append((cls, args, kwargs))
            return cls
        return ret

    @staticmethod
    def add_all(parser):
        for _, args, kwargs in Option.requirements:
            parser.add_argument(*args, **kwargs)

    @staticmethod
    def add_required(parser, method):
        required = dict()
        for stage in method.stages:
            for cls, args, kwargs in Option.requirements:
                if issubclass(stage.__class__, cls):
                    required[args] = kwargs
        for args, kwargs in required.iteritems():
            required = 'default' not in kwargs
            parser.add_argument(required=required, *args, **kwargs)


@Option.requires('-a', help='amtredird url', metavar='AMTREDIRD',
                 default='https://urgu.org/amtredird')
class WithAMTRedirdURL(stage.Stage):
    def parse(self, args):
        super(WithAMTRedirdURL, self).parse(args)
        self.amtredird_url = args.a


@Option.requires('-c', help='config API url', metavar='CONFIG',
                 default='https://urgu.org/config')
class WithConfigURL(stage.Stage):
    def parse(self, args):
        super(WithConfigURL, self).parse(args)
        self.config_url = args.c


@Option.requires('-p', help='AMT credentials', metavar='FILE',
                 default='amtpasswd')
class WithAMTCredentials(stage.Stage):
    def parse(self, args):
        super(WithAMTCredentials, self).parse(args)
        self.amt_creds = amt_creds.AMTCredentialsProvider(args.p)


@Option.requires('-s', help='ssh login', metavar='LOGIN', default='root')
class WithSSHCredentials(stage.Stage):
    def parse(self, args):
        super(WithSSHCredentials, self).parse(args)
        self.ssh_login = args.s

    def run_ssh(self, host, args, opts=[]):
        return proc.run_remote_process(
            host.name, self.ssh_login, args, host.state.log, opts)


@Option.requires('-l', help='local address', metavar='ADDR')
class WithLocalAddress(stage.Stage):
    def parse(self, args):
        super(WithLocalAddress, self).parse(args)
        self.local_addr = args.l


@Option.requires(
    '-n', help='deploy local INPUT into OUTPUT on all the hosts with ndd',
    metavar='INPUT:OUTPUT', action='append', default=[])
class WithNDDArgs(stage.Stage):
    def parse(self, args):
        super(WithNDDArgs, self).parse(args)
        self.ndds = [pair.split(':', 1) for pair in args.n]


@Option.requires(
    '-b', help='ban HOST, excluding it from deployment',
    metavar='HOST', action='append', default=[])
class WithBannedHosts(stage.Stage):
    def parse(self, args):
        super(WithBannedHosts, self).parse(args)
        self.banned_hosts = args.b
