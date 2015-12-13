import subprocess

from common import stage

class DiskBase(stage.SimpleStage):
    def __init__(self, login='root'):
        self.login = login

    def call_to(self, host, cmd):
        return subprocess.check_output(
            ['ssh', '-l', self.login, host.name] + cmd)

    def call_to_disk(self, host, cmd):
        return self.call_to(host, ['/usr/local/bin/disk.py', cmd, host.disk])


class DetermineDisk(DiskBase):
    name = 'determine exact device of local disk'

    def run_single(self, host):
        def with_disk(pattern):
            disk = '/dev/disk/by-id/{}'.format(host.props['disk'])
            return self.call_to(host, [pattern.format(disk)])

        count = with_disk('shopt -s nullglob; disks=({}); echo ${{#disks[@]}}')
        if int(count) != 1:
            host.fail(
                self, 'there should be exactly one disk ' +
                      'with pattern "{}", have {}'.format(self.disk, count))
        else:
            host.disk = with_disk('readlink -f {}').strip()
            host.state.log.info('real disk for {} is {}'.format(
                host.name, host.disk))


class FreeDisk(DiskBase):
    name = 'possibly unmount /place to free local disk'

    def run_single(self, host):
        self.call_to(host, ['if mountpoint /place; then umount /place; fi'])


class PartitionDisk(DiskBase):
    name = 'call "disk.py create" to partition and format local disk'

    def run_single(self, host):
        assert host.disk
        self.call_to_disk(host, 'create')


class ConfigureDisk(DiskBase):
    name = ('call "disk.py configure" to install and configure bootloader ' +
            'on local disk')

    def run_single(self, host):
        assert host.disk
        self.call_to_disk(host, 'configure')