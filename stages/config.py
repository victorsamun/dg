from common import config, stage
from util import proc
import os

class RunCommands(stage.ParallelStage):
    def get_commands(self, host):
        return []

    def get_files_to_copy(self, host):
        return []

    def run_single(self, host):
        rvs = [self.run_scp(host, self.ssh_login_linux, src, dst)
               for src, dst in self.get_files_to_copy(host)]
        rvs += [self.run_ssh(host, cmd, login=self.ssh_login_linux)
                for cmd in self.get_commands(host)]

        if any(map(lambda (rv, _): rv != 0, rvs)):
            self.fail('failed to {}'.format(self))


class StoreCOWConfig(config.WithSSHCredentials, RunCommands):
    'store Puppet SSL stuff into COW config partition'

    def get_commands(self, host):
        return map(lambda cmd: ['/root/cow/conf.sh'] + cmd, [
            ['mkdir', '-p', '{}/puppet/certs', '{}/puppet/private_keys'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/ca.pem', '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/{}.pem'.format(host.name),
             '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/private_keys/{}.pem'.format(
                host.name), '{}/puppet/private_keys']
        ])


class CustomizeWindowsSetup(
        config.WithSSHCredentials, config.WithWindows7Partition, RunCommands):
    'customize SSH credentials and sysprep config in Windows root partition'

    def get_files_to_copy(self, host):
        return [
            (os.path.join(os.path.dirname(__file__), os.path.pardir,
             'win7', 'customize.py'), '/tmp/customize.py')
        ]

    def get_commands(self, host):
        mountpoint = '/mnt'
        prefix = '/cygwin64/etc'
        args = ['-H', '""', '-j', 'runc.urgu.org', '-p', '/etc/smb.pwd']
        if 'userqwer' in host.props['services']:
            args += ['-a', 'user:qwer']
        sysprep_xml = '/mnt/Windows/Panther/unattend.xml'
        return [
            ['mount', self.get_win7_partition(), mountpoint],
            ['cp /etc/ssh/ssh_host_*_key{{,.pub}} {}{}'.format(
                mountpoint, prefix)],
            ['python', '/tmp/customize.py'] + args + [sysprep_xml, sysprep_xml],
            ['umount', mountpoint],
        ]
