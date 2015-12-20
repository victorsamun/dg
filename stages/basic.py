from clients import config as cfg
from common import config, host, stage

class InitHosts(config.WithConfigURL, stage.Stage):
    name = 'get initial host list'

    def run(self, state):
        for sname in cfg.get(self.config_url, state.group)['hosts']:
            host.Host(state, cfg.get(self.config_url, sname))


class ExcludeBannedHosts(config.WithBannedHosts, stage.Stage):
    name = 'exclude banned hosts from deployment'

    def run(self, state):
        for host in list(state.active_hosts):
            if any(map(lambda name: name in self.banned_hosts,
                       [host.name, host.sname])):
                host.fail(self, 'explicitly excluded from deployment')
