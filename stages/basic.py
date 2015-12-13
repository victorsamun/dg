import datetime
import multiprocessing
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


def check_ssh((host, login, step_timeout, total_timeout)):
    start = datetime.datetime.now()
    while datetime.datetime.now() - start < total_timeout:
        rv = subprocess.call(
            ['ssh', '-l', login,
             '-o', 'ConnectTimeout={}'.format(step_timeout.seconds),
             host.name, 'exit'])
        if rv == 0:
            return (host.name, True)
        else:
            time.sleep(step_timeout.seconds)
    return (host.name, False)


class WaitForSSHAvailable(stage.Stage):
    name = 'wait for SSH available on all the hosts'

    def __init__(self, step_timeout, total_timeout, login='root'):
        self.login = login
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def run(self, state):
        name_to_host = dict((host.name, host) for host in state.active_hosts)
        args = [(host, self.login, self.step_timeout, self.total_timeout)
                for host in state.active_hosts]
        results = multiprocessing.Pool(
            len(state.active_hosts)).map(check_ssh, args)

        for name, result in results:
            if not result:
                name_to_host[name].fail(
                    self, 'failed to ensure SSH is available')


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
