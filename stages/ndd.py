from common import config, stage
from util import proc

class RunNDDViaSlurm(config.WithLocalAddress, config.WithNDDArgs, stage.Stage):
    'deploy the images with ndd via SLURM'

    def run(self, state):
        for src, dst in self.ndds:
            cmdline = ['python', '/usr/local/bin/ndd_slurm.py']
            cmdline.extend(['-s', self.local_addr, '-i', src, '-o', dst])

            for host in sorted(state.active_hosts,
                               key=lambda host: host.props.get('switch')):
                cmdline.extend(['-d', str(host.sname)])

            rv, _ = proc.run_process(cmdline, state.log)
            if rv != 0:
                for host in list(state.active_hosts):
                    host.fail(self, 'failed to run ndd_slurm.py')
