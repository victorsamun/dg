import subprocess

from common import config, stage

class DiskBase(config.WithSSHCredentials, stage.ParallelStage):
    def call_to_disk(self, host, cmd):
        return self.run_ssh(host, ['/usr/local/bin/disk.py', cmd, host.disk])

    def run_single(self, host):
        if not host.disk:
            return (False, 'no disk found on host')

        rv, _ = self.call_to_disk(host, self.get_command())
        if rv != 0:
            return self.fail('call to disk.py failed')
        else:
            return self.ok()

    def get_command(self):
        raise NotImplementedError()


class DetermineDisk(config.WithSSHCredentials, stage.SimpleStage):
    name = 'determine exact device of local disk'

    def run_single(self, host):
        def with_disk(pattern):
            disk = '/dev/disk/by-id/{}'.format(host.props['disk'])
            return self.run_ssh(host, [pattern.format(disk)])

        rv, count = (
            with_disk('shopt -s nullglob; disks=({}); echo ${{#disks[@]}}'))
        if rv != 0:
            host.fail('call to disk.py failed')
        else:
            if int(count) != 1:
                host.fail(
                    self, 'there should be exactly one disk ' +
                          'with pattern "{}", have {}'.format(self.disk, count))
            else:
                rv, raw_disk = with_disk('readlink -f {}')
                if rv != 0:
                    host.fail('call to disk.py failed')
                else:
                    host.disk = raw_disk.strip()
                    host.state.log.info('real disk for {} is {}'.format(
                        host.name, host.disk))


class FreeDisk(config.WithSSHCredentials, stage.ParallelStage):
    name = 'possibly unmount /place to free local disk'

    def run_single(self, host):
        rv, _ = self.run_ssh(
            host, ['if mountpoint /place; then umount /place; fi'])
        if rv != 0:
            return self.fail('failed to free local disk')
        else:
            return self.ok()


class PartitionDisk(DiskBase, stage.ParallelStage):
    name = 'call "disk.py create" to partition and format local disk'

    def get_command(self):
        return 'create'


class ConfigureDisk(DiskBase, stage.ParallelStage):
    name = ('call "disk.py configure" to install and configure bootloader ' +
            'on local disk')

    def get_command(self):
        return 'configure'
