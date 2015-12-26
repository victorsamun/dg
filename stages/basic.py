from clients import config as cfg
from common import config, host, stage

class InitHosts(config.WithConfigURL, stage.Stage):
    name = 'get initial host list'

    def run(self, state):
        all_hosts = set(
            map(lambda sname: cfg.get(self.config_url, sname)['name'],
                state.hosts))

        for group in state.groups:
            all_hosts |= set(cfg.get(self.config_url, group)['hosts'])

        for name in all_hosts:
            host.Host(state, cfg.get(self.config_url, name))


class ExcludeBannedHosts(config.WithBannedHosts, stage.Stage):
    name = 'exclude banned hosts from deployment'

    def run(self, state):
        for host in list(state.active_hosts):
            if any(map(lambda name: name in self.banned_hosts,
                       [host.name, host.sname])):
                host.fail(self, 'explicitly excluded from deployment')
