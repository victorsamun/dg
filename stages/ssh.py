import collections
import datetime
import itertools
import time

from common import config, stage
from util import win

class Timeouts:
    TINY   = (datetime.timedelta(seconds=1),  datetime.timedelta(seconds=5))
    NORMAL = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=15))
    BIG    = (datetime.timedelta(minutes=1),  datetime.timedelta(minutes=20))


Command = collections.namedtuple('Command', ('login', 'command'))


REBOOT_MARKER = '/tmp/rebooting'


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
        start = datetime.datetime.now()
        while datetime.datetime.now() - start < self.total_timeout:
            for command in self.get_commands(host):
                if self.check_result(host, command) == 0:
                    return
            else:
                host.state.log.info(
                    'condition not met yet, sleeping for {} seconds'.format(
                        self.step_timeout.seconds))
                time.sleep(self.step_timeout.seconds)
        self.fail('failed to execute remote commands')


class CombineCommands(object):
    def get_commands(self, host):
        return itertools.chain.from_iterable(
            cls.get_commands(self, host) for cls in type(self).__bases__
            if cls is not CombineCommands)


class WaitForSSHAvailable(ExecuteRemoteCommands):
    'wait for SSH available on all the hosts'

    def get_commands(self, host):
        return [Command(self.ssh_login_linux, ['exit'])]


class WindowsBase(ExecuteRemoteCommands):
    def get_commands(self, host):
        return map(lambda login: Command(login, self.get_command()),
                   win.get_possible_logins(host, self.ssh_login_windows))


class WaitUntilBootedIntoWindows(WindowsBase):
    'wait with SSH until host boots into Windows'

    def get_command(self):
        return ['uname | grep -q NT']


class RebootWindows(WindowsBase):
    'reboot Windows host with SSH'

    def get_command(self):
        return ['shutdown', '/r', '/t', '0']


class CheckIsAccessibleViaSSH(CombineCommands,
                              WaitForSSHAvailable, WaitUntilBootedIntoWindows):
    'check whether the host is accessible via SSH in some way'


class WaitUntilBootedIntoCOWMemory(ExecuteRemoteCommands):
    'wait with SSH until host boots into COW memory image'

    def get_commands(self, host):
        return [Command(self.ssh_login_linux,
                        ['grep -q cowtype=mem /proc/cmdline && '
                         '! test -f {}'.format(REBOOT_MARKER)])]


class RebootLinux(ExecuteRemoteCommands):
    'reboot Linux host with SSH'

    def get_commands(self, host):
        return [Command(
            self.ssh_login_linux,
            ['touch {} && shutdown -r'.format(REBOOT_MARKER)])]


class RebootHost(CombineCommands, RebootLinux, RebootWindows):
    'reboot host with SSH, whether Linux or Windows'
