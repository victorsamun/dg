import subprocess

from common import config, stage
from util import proc

class EnsureNetworkSpeed(config.WithLocalAddress,
                         config.WithSSHCredentials,
                         stage.ParallelStage):
    name = 'ensure sufficient throughput of network interface'

    def __init__(self, poolsize=3, minimum=200, time=5):
        stage.ParallelStage.__init__(self, poolsize)
        self.minimum = minimum
        self.time = time
        self.server = None

    def setup(self):
        self.server = subprocess.Popen(['iperf', '-s'])

    def run_single(self, host):
        rv, output = self.run_ssh(
            host,
            ['iperf', '-c', self.local_addr, '-t', str(self.time), '-y', 'c'])
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
