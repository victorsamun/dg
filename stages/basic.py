import datetime
import subprocess
import time

from clients import config
from common import host, stage

class InitHosts(stage.WithConfig, stage.Stage):
    name = 'get initial host list'

    def run(self, state):
        for sname in config.get_hosts(self.config_url, state.group):
            host.Host(state, config.get_name(self.config_url, sname),
                      config.get_props(self.config_url, sname))


class WaitForSSHAvailable(stage.ParallelStage):
    name = 'wait for SSH available on all the hosts'

    def __init__(self, step_timeout, total_timeout, login='root'):
        self.login = login
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def run_single(self, host):
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            proc = subprocess.Popen(
                ['ssh', '-l', self.login,
                 '-o', 'ConnectTimeout={}'.format(self.step_timeout.seconds),
                 host.name, 'exit'], stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if len(stderr) > 0:
                host.state.log.error(stderr.strip())

            rv = proc.returncode
            if rv == 0:
                return (True, None)
            else:
                time.sleep(self.step_timeout.seconds)
        return (False, 'failed to ensure SSH is available')


class ConfigureBoot(stage.WithConfig, stage.SimpleStage):
    BOOT_PROP = 'boot'

    def run_single(self, host):
        config.set_props(self.config_url, host.name,
                         [(ConfigureBoot.BOOT_PROP, self.__class__.value)])


class SetBootIntoCOWMemory(ConfigureBoot):
    name = 'enable boot to COW memory image'
    value = 'cow-m'

    def rollback_single(self, host):
        config.set_props(self.config_url, host.name,
                         [(ConfigureBoot.BOOT_PROP, ResetBoot.value)])


class ResetBoot(ConfigureBoot):
    name = "reset boot into it's default state"
    value = ''
