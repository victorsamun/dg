import collections
import datetime
import itertools
import time

from common import config, stage

class Timeouts:
    TINY   = (datetime.timedelta(seconds=1),  datetime.timedelta(seconds=5))
    NORMAL = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=15))
    BIG    = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=20))


Command = collections.namedtuple('Command', ('login', 'command'))


class ExecuteRemoteCommands(config.WithSSHCredentials, stage.ParallelStage):
    def __init__(self, step_timeout, total_timeout):
        super(ExecuteRemoteCommands, self).__init__()
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def get_commands(self):
        raise NotImplementedError()

    def ignore_errors(self):
        return False

    def check_result(self, host, command):
        rv, _ = self.run_ssh(host, command.command,
                             login=command.login, opts=['ConnectTimeout=1'])
        return rv

    def run_single(self, host):
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            for command in self.get_commands():
                if self.check_result(host, command) == 0:
                    return self.ok()
            else:
                time.sleep(self.step_timeout.seconds)
        return self.fail('failed to execute remote commands')


class CombineCommands(object):
    def get_commands(self):
        return itertools.chain.from_iterable(
            cls.get_commands(self) for cls in type(self).__bases__
            if cls is not CombineCommands)


class WaitForSSHAvailable(ExecuteRemoteCommands):
    name = 'wait for SSH available on all the hosts'

    def get_commands(self):
        return [Command(login=self.ssh_login_linux, command=['exit'])]


class WaitUntilBootedIntoWindows(ExecuteRemoteCommands):
    name = 'wait with SSH until host boots into Windows'

    def get_commands(self):
        return [Command(login=self.ssh_login_windows,
                        command=['uname | grep -q NT'])]


class CheckIsAccessibleViaSSH(CombineCommands,
                              WaitForSSHAvailable, WaitUntilBootedIntoWindows):
    name = 'check whether the host is accessible via SSH in some way'


class WaitUntilBootedIntoCOWMemory(ExecuteRemoteCommands):
    name = 'wait with SSH until host boots into COW memory image'

    def get_commands(self):
        return [Command(login=self.ssh_login_linux,
                        command=['grep', '-q', 'cowtype=mem', '/proc/cmdline'])]


class RebootLinuxHost(ExecuteRemoteCommands):
    name = 'reboot Linux host with SSH'

    def get_commands(self):
        return [Command(login=self.ssh_login_linux, command=['reboot'])]

    def ignore_errors(self):
        return True


class RebootWindowsHost(ExecuteRemoteCommands):
    name = 'reboot Windows host with SSH'

    def get_commands(self):
        return [Command(login=self.ssh_login_windows,
                        command=['shutdown', '/r', '/t', '0'])]

    def ignore_errors(self):
        return True


class RebootHost(CombineCommands, RebootLinuxHost, RebootWindowsHost):
    name = 'reboot host with SSH, whether Linux or Windows'
