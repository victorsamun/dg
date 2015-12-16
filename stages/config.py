from common import config, stage
from util import proc

class StoreCOWConfig(config.WithSSHCredentials, stage.ParallelStage):
    name = 'store Puppet SSL stuff into COW config partition'

    def run_single(self, host):
        cmds = [
            ['mkdir', '-p', '{}/puppet/certs', '{}/puppet/private_keys'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/ca.pem', '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/certs/{}.pem'.format(host.name),
             '{}/puppet/certs'],
            ['cp', '-a', '/var/lib/puppet/ssl/private_keys/{}.pem'.format(
                host.name), '{}/puppet/private_keys']
        ]

        rvs = [
            self.run_ssh(host, ['/root/cow/conf.sh'] + cmd)
            for cmd in cmds
        ]

        if any(map(lambda (rv, _): rv != 0, rvs)):
            return self.fail('failed to store Puppet SSL data ' +
                             'into config partition')
        return self.ok()
