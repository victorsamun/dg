from common import config, stage
from util import proc

class RunCommands(stage.ParallelStage):
    def get_commands(self, host):
        return []

    def run_single(self, host):
        rvs = [self.run_ssh(host, cmd, login=self.ssh_login_linux)
               for cmd in self.get_commands(host)]

        if any(map(lambda (rv, _): rv != 0, rvs)):
            return self.fail('failed to {}'.format(self))
        return self.ok()


class StoreCOWConfig(config.WithSSHCredentials, RunCommands):
    name = 'store Puppet SSL stuff into COW config partition'

    def get_commands(self, host):
        return map(lambda cmd: ['/root/cow/conf.sh'] + cmd, [
            ['mkdir', '-p', '{}/puppet/certs', '{}/puppet/private_keys'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/ca.pem', '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/{}.pem'.format(host.name),
             '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/private_keys/{}.pem'.format(
                host.name), '{}/puppet/private_keys']
        ])


class CopySSHCredentialsIntoWindows7Partition(
        config.WithSSHCredentials, config.WithWindows7Partition, RunCommands):
    name = 'copy SSH credentials into Windows 7 root partition'

    def get_commands(self, host):
        mountpoint = '/mnt'
        prefix = '/cygwin64/etc'
        return [
            ['mount', self.get_win7_partition(), mountpoint],
            ['cp /etc/ssh/ssh_host_*_key{{,.pub}} {}{}'.format(
                mountpoint, prefix)],
            ['umount', mountpoint],
        ]
