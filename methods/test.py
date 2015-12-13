import datetime

from common import method
from stages import basic, config, ndd, slurm

class TestMethod(method.Method):
    def __init__(self, config_url, ndds):
        super(TestMethod, self).__init__(
            [basic.InitHosts(config_url),
             slurm.WaitForSlurmAvailable(tries=3, pause=1),
             basic.WaitForSSHAvailable(
                datetime.timedelta(seconds=1),
                datetime.timedelta(seconds=3)),
             config.StoreCOWConfig()])
