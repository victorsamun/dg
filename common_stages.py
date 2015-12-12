import config
import datetime
import host
import multiprocessing
import stage
import subprocess
import time

class InitHosts(stage.Stage):
    name = 'get initial host list'

    def __init__(self, config_url):
        self.config_url = config_url

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


class ConfigureBoot(stage.SimpleStage):
    def __init__(self, config_url, default):
        self.config_url = config_url
        self.default = default

    def run_single(self, host):
        config.set_props(self.config_url, host.name, [('boot', self.default)])


class SetBootIntoCOWMemory(ConfigureBoot):
    name = 'enable boot to COW memory image'

    def __init__(self, config_url):
        super(SetBootIntoCOWMemory, self).__init__(config_url, 'cow-m')

    def rollback_single(self, host):
        config.set_props(self.config_url, host.name, [('boot', '')])


class ResetBoot(ConfigureBoot):
    name = "reset boot into it's default state"

    def __init__(self, config_url):
        super(ResetBoot, self).__init__(config_url, '')
