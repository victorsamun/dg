import datetime

from common import method
from stages import basic, boot, config, network, slurm, ssh

class TestMethod(method.Method):
    name = 'test'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        slurm.WaitForSlurmAvailable(),
        ssh.WaitForSSHAvailable(*ssh.Timeouts.TINY),
        network.EnsureNetworkSpeed(),
    ]
