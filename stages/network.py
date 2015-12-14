import subprocess

from common import stage
from util import proc

class EnsureNetworkSpeed(stage.ParallelStage):
    name = 'ensure sufficient throughput of network interface'

    def __init__(self, addr, login='root', poolsize=3, minimum=200, time=5):
        super(EnsureNetworkSpeed, self).__init__(poolsize)
        self.addr = addr
        self.login = login
        self.minimum = minimum
        self.time = time
        self.server = None

    def setup(self):
        self.server = subprocess.Popen(['iperf', '-s'])

    def run_single(self, host):
        rv, output = proc.run_remote_process(
            str(host.name), self.login,
            ['iperf', '-c', self.addr, '-t', str(self.time), '-y', 'c'],
            host.state.log)
        if rv != 0:
            return self.fail('failed to execute iperf -c, rv is {}'.format(rv))
        else:
            speed = int(output.strip().split(',')[8]) / 1000000
            if speed < self.minimum:
                return self.fail(
                    ('insufficient network speed: need {} Mbits/s, ' +
                     'got {} Mbits/s').format(self.minimum, speed))
            return self.ok()

    def teardown(self):
        self.server.terminate()
        self.server = None
