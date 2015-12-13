from common import stage
from util import proc

class RunNDDViaSlurm(stage.Stage):
    name = 'deploy the image with ndd via SLURM'

    def __init__(self, src, input, output):
        self.src, self.input, self.output = src, input, output

    def run(self, state):
        cmdline = ['python', '/usr/local/bin/ndd_slurm.py']
        cmdline.extend(['-s', self.src])
        cmdline.extend(['-i', self.input])
        cmdline.extend(['-o', self.output])

        for host in sorted(state.active_hosts, key=lambda host: host.sname):
            cmdline.extend(['-d', str(host.sname)])

        rv, _ = proc.run_process(cmdline, state.log)
        if rv != 0:
            for host in list(state.active_hosts):
                host.fail(self, 'failed to run ndd_slurm.py')
