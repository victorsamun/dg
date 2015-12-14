import datetime

from common import method
from stages import basic, network, slurm

class TestMethod(method.Method):
    def __init__(self, config_url, addr):
        super(TestMethod, self).__init__(
            [basic.InitHosts(config_url),
             slurm.WaitForSlurmAvailable(tries=3, pause=1),
             basic.WaitForSSHAvailable(
                datetime.timedelta(seconds=1),
                datetime.timedelta(seconds=3)),
             network.EnsureNetworkSpeed(addr)])
