import datetime

from common import method
from stages import basic, network, slurm

class TestMethod(method.Method):
    name = 'test'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        slurm.WaitForSlurmAvailable(tries=3, pause=1),
        basic.WaitForSSHAvailable(
            step_timeout=datetime.timedelta(seconds=1),
            total_timeout=datetime.timedelta(seconds=3)),
        network.EnsureNetworkSpeed(),
    ]
