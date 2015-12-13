import subprocess
import os.path

from clients import config
from common import stage

class DetermineAMTHosts(stage.WithConfig, stage.SimpleStage):
    name = 'determine AMT hosts'

    def run_single(self, host):
        amt_host = host.props.get('amt')
        if amt_host is None:
            host.fail(self, 'host props do not have "amt" attribute')
        else:
            host.amt_host = config.get_name(self.config_url, amt_host)


class AMTStage(stage.SimpleStage):
    def __init__(self, creds_provider):
        self.provider = creds_provider

    def call_amttool(self, host, cmd):
        AMTTOOL = os.path.join(os.path.dirname(__file__), 'amttool')
        user, passwd = self.provider.get_credentials(host)
        return subprocess.check_output(
            ['/usr/bin/perl', AMTTOOL, host, cmd],
            env={'AMT_USER': user, 'AMT_PASSWORD': passwd})


class WakeupAMTHosts(AMTStage):
    name = 'wake up hosts via AMT interface'

    def run_single(self, host):
        try:
            status = self.call_amttool(host.amt_host, 'powerstate')
            if status != 0:
                self.call_amttool(host.amt_host, 'powerup')
        except Exception:
            host.fail(self, 'call to amttool failed')


class ResetAMTHosts(AMTStage):
    name = 'reset hosts via AMT interface'

    def run_single(self, host):
        try:
            self.call_amttool(host.amt_host, 'reset')
        except Exception:
            host.fail(self, 'call to amttool failed')
