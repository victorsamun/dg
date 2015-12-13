import datetime

from common import method
from stages import basic, ndd, slurm

class TestMethod(method.Method):
    def __init__(self, config_url, ndds):
        super(TestMethod, self).__init__(
            [basic.InitHosts(config_url),
             slurm.WaitForSlurmAvailable(tries=3, pause=1)] +
            [ndd.RunNDDViaSlurm(*spec.split(':')) for spec in ndds])
