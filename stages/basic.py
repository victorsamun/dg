import datetime
import subprocess
import time

from clients import config as cfg
from common import config, host, stage
from util import proc

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


class WaitForSSHAvailable(config.WithSSHCredentials, stage.ParallelStage):
    name = 'wait for SSH available on all the hosts'

    def __init__(self, step_timeout, total_timeout):
        super(WaitForSSHAvailable, self).__init__()
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def run_single(self, host):
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            rv, _ = self.run_ssh(
                host, ['exit'],
                opts=['ConnectTimeout={}'.format(self.step_timeout.seconds)])
            if rv == 0:
                return self.ok()
            else:
                time.sleep(self.step_timeout.seconds)
        return self.fail('failed to ensure SSH is available')


class ConfigureBoot(config.WithConfigURL, stage.SimpleStage):
    BOOT_PROP = 'boot'

    def run_single(self, host):
        cfg.set(self.config_url, host.name,
                [(ConfigureBoot.BOOT_PROP, self.__class__.value)])


class SetBootIntoCOWMemory(ConfigureBoot):
    name = 'enable boot to COW memory image'
    value = 'cow-m'

    def rollback_single(self, host):
        cfg.set(self.config_url, host.name,
                [(ConfigureBoot.BOOT_PROP, ResetBoot.value)])


class ResetBoot(ConfigureBoot):
    name = "reset boot into it's default state"
    value = ''
