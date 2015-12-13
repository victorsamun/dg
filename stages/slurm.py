import time

from common import stage
from util import hosts, proc

class WaitForSlurmAvailable(stage.Stage):
    name = 'ensure SLURM is available on the hosts'

    def __init__(self, tries=3, pause=10):
        self.tries = tries
        self.pause = pause

    def step(self, state):
        absent_hosts = dict((host.sname, host) for host in state.active_hosts)
        rv, output = proc.run_process(
            ['sinfo', '-p', state.group, '-t', 'idle', '-h', '-o', '%n'],
            state.log)
        if rv == 0:
            for name in output.strip().split('\n'):
                if name in absent_hosts:
                    del absent_hosts[name]
            return (True, absent_hosts.values())
        else:
            return (False, None)

    def run(self, state):
        for i in range(self.tries):
            if i != 0:
                time.sleep(self.pause)
            rv, failed = self.step(state)
            if len(failed) == 0:
                return
            state.log.warning('still waiting for SLURM to come up on ' +
                              'the following hosts: {}'.format(
                                  hosts.format_hosts(failed)))
        for host in failed:
            host.fail(self, 'timed out while waiting for SLURM to come up')
