import collections
import datetime
import itertools
import time

import boot
from common import config, stage
from util import win

class Timeouts:
    TINY   = (datetime.timedelta(seconds=4),  datetime.timedelta(seconds=20))
    NORMAL = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=10))
    BIG    = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=30))


Command = collections.namedtuple('Command', ('login', 'command'))


REBOOT_MARKER = '/tmp/rebooting'

CHECK_WIN  = 'uname | grep -q NT'
REBOOT_WIN = 'shutdown /r /t 0'

CHECK_LINUX     = '! test -f {}'.format(REBOOT_MARKER)
CHECK_LINUX_MEM = 'grep -q cowtype=mem /proc/cmdline && ' + CHECK_LINUX
REBOOT_LINUX    = 'touch {} && shutdown -r'.format(REBOOT_MARKER)


class ExecuteRemoteCommands(config.WithSSHCredentials, stage.ParallelStage):
    def __init__(self, step_timeout, total_timeout):
        super(ExecuteRemoteCommands, self).__init__()
        self.step_timeout = step_timeout
        self.total_timeout = total_timeout

    def get_commands(self, host):
        raise NotImplementedError

    def check_result(self, host, command):
        rv, _ = self.run_ssh(host, command.command,
                             login=command.login, opts=['ConnectTimeout=1'])
        return rv

    def run_single(self, host):
        commands = self.get_commands(host)
        if not commands:
            return

        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            for command in commands:
                if self.check_result(host, command) == 0:
                    return
            host.state.log.info(
                'condition not met yet, sleeping for {} seconds'.format(
                    self.step_timeout.seconds))
            time.sleep(self.step_timeout.seconds)
        self.fail('failed to execute remote commands')


class WaitUntilBootedIntoCOWMemory(ExecuteRemoteCommands):
    'wait with SSH until host boots into COW memory image'

    def get_commands(self, host):
        return [Command(self.ssh_login_linux, [CHECK_LINUX_MEM])]


def get_win_commands(host, login, cmd):
    return map(lambda login: Command(login, [cmd]),
               win.get_possible_logins(host, login))


class CheckIsAccessible(ExecuteRemoteCommands):
    'check whether the host is accessible via SSH in some way'

    def get_commands(self, host):
        return (get_win_commands(host, self.ssh_login_windows, CHECK_WIN) +
                [Command(self.ssh_login_linux, [CHECK_LINUX])])


class RebootHost(ExecuteRemoteCommands):
    'reboot host with SSH, whether Linux or Windows'

    def get_commands(self, host):
        return (get_win_commands(host, self.ssh_login_windows, REBOOT_WIN) +
                [Command(self.ssh_login_linux, [REBOOT_LINUX])])


class MaybeRebootLocalLinux(ExecuteRemoteCommands):
    'reboot host booted into local Linux if it is not default boot'

    def get_commands(self, host):
        return ([Command(self.ssh_login_linux, [REBOOT_LINUX])]
                if boot.BootsToWindowsByDefault(host) else [])


class WaitUntilBootedIntoLocalWindows(ExecuteRemoteCommands):
    'wait until host has booted into local Windows'

    def get_commands(self, host):
        return get_win_commands(host, self.ssh_login_windows, CHECK_WIN)


class WaitUntilBootedIntoLocalLinux(ExecuteRemoteCommands):
    'wait until host has booted into local Linux'

    def get_commands(self, host):
        return [Command(self.ssh_login_linux, [CHECK_LINUX])]


class RebootNonDefaultOS(ExecuteRemoteCommands):
    'reboot non-default OS'

    def get_commands(self, host):
        return ([Command(self.ssh_login_linux, [REBOOT_LINUX])]
                if boot.BootsToWindowsByDefault(host)
                else get_win_commands(host, self.ssh_login_windows, REBOOT_WIN))
