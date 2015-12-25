import datetime
import time

from common import config, stage

class Timeouts:
    TINY   = (datetime.timedelta(seconds=1),  datetime.timedelta(seconds=5))
    NORMAL = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=15))
    BIG    = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=20))


class WaitForRemoteCondition(config.WithSSHCredentials, stage.ParallelStage):
    def get_cmd(self):
        return ['exit']

    def ignore_errors(self):
        return False

    def __init__(self, step_timeout, total_timeout):
        super(WaitForRemoteCondition, self).__init__()
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def run_single(self, host):
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            rv, _ = self.run_ssh(
                host, self.get_cmd(),
                login=self.get_login(),
                opts=['ConnectTimeout={}'.format(self.step_timeout.seconds)])
            if rv == 0 or self.ignore_errors():
                return self.ok()
            else:
                time.sleep(self.step_timeout.seconds)
        return self.fail('failed to ensure SSH is available')


class WaitForSSHAvailable(WaitForRemoteCondition):
    name = 'wait for SSH available on all the hosts'

    def __init__(self, step_timeout, total_timeout):
        super(WaitForSSHAvailable, self).__init__(step_timeout, total_timeout)


class WaitUntilBootedIntoCOWMemory(WaitForRemoteCondition):
    name = 'wait with SSH until host boots into COW memory image'

    def __init__(self, step_timeout, total_timeout):
        super(WaitUntilBootedIntoCOWMemory, self).__init__(
            step_timeout, total_timeout)

    def get_cmd(self):
        return ['grep', '-q', 'cowtype=mem', '/proc/cmdline']


class UseWindowsLogin(WaitForRemoteCondition):
    def get_login(self):
        return self.ssh_login_windows


class WaitUntilBootedIntoWindows7(UseWindowsLogin, WaitForRemoteCondition):
    name = 'wait with SSH until host boots into Windows 7'

    def __init__(self, step_timeout, total_timeout):
        super(WaitUntilBootedIntoWindows7, self).__init__(
            step_timeout, total_timeout)

    def get_cmd(self):
        return ['uname | grep -q NT']


class RebootLinuxHost(WaitForRemoteCondition):
    name = 'reboot host with SSH'

    def __init__(self, step_timeout, total_timeout):
        super(RebootLinuxHost, self).__init__(
            step_timeout, total_timeout)

    def get_cmd(self):
        return ['reboot']

    def ignore_errors(self):
        return True


class RebootWindowsHost(UseWindowsLogin, WaitForRemoteCondition):
    name = 'reboot host with SSH'

    def __init__(self, step_timeout, total_timeout):
        super(RebootWindowsHost, self).__init__(
            step_timeout, total_timeout)

    def get_cmd(self):
        return ['shutdown', '/r', '/t', '0']

    def ignore_errors(self):
        return True
