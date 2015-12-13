import datetime
import subprocess
import time

from clients import config
from common import host, stage
from util import proc

class InitHosts(stage.WithConfig, stage.Stage):
    name = 'get initial host list'

    def run(self, state):
        for sname in config.get(self.config_url, state.group)['hosts']:
            host.Host(state, config.get(self.config_url, sname))


class WaitForSSHAvailable(stage.ParallelStage):
    name = 'wait for SSH available on all the hosts'

    def __init__(self, step_timeout, total_timeout, login='root'):
        self.login = login
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def run_single(self, host):
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            rv, _ = proc.run_remote_process(
                host.name, self.login, ['exit'], host.state.log,
                opts=['ConnectTimeout={}'.format(self.step_timeout.seconds)])
            if rv == 0:
                return self.ok()
            else:
                time.sleep(self.step_timeout.seconds)
        return self.fail('failed to ensure SSH is available')


class ConfigureBoot(stage.WithConfig, stage.SimpleStage):
    BOOT_PROP = 'boot'

    def run_single(self, host):
        config.set(self.config_url, host.name,
                   [(ConfigureBoot.BOOT_PROP, self.__class__.value)])


class SetBootIntoCOWMemory(ConfigureBoot):
    name = 'enable boot to COW memory image'
    value = 'cow-m'

    def rollback_single(self, host):
        config.set(self.config_url, host.name,
                   [(ConfigureBoot.BOOT_PROP, ResetBoot.value)])


class ResetBoot(ConfigureBoot):
    name = "reset boot into it's default state"
    value = ''
