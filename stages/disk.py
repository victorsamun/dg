import subprocess

from common import config, stage

class ConfigureDisk(config.WithSSHCredentials, config.WithConfigURL,
                    stage.ParallelStage):
    def run_single(self, host):
        rv, _ = self.run_ssh(host, ['disk.py', '-c', self.config_url],
                             login=self.ssh_login)
        if rv != 0:
            return self.fail('call to disk.py failed')
        else:
            return self.ok()

class FreeDisk(config.WithSSHCredentials, stage.ParallelStage):
    name = 'possibly unmount /place to free local disk'

    def run_single(self, host):
        rv, _ = self.run_ssh(
            host, ['if mountpoint /place; then umount /place; fi'],
            login=self.ssh_login_linux)
        if rv != 0:
            return self.fail('failed to free local disk')
        else:
            return self.ok()
