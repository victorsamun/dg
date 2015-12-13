import datetime

from common import method
from stages import amt, amtredird, basic, disk
from util import amt_creds

class AMTMethod(method.Method):
    def __init__(self, amtpasswd, config_url, amtredird_url):
        creds_provider = amt_creds.AMTCredentialsProvider(amtpasswd)
        super(AMTMethod, self).__init__(
            [basic.InitHosts(config_url),
             amt.DetermineAMTHosts(config_url),
             amtredird.EnsureRedirectionPossible(amtredird_url),
             amt.WakeupAMTHosts(creds_provider),
             amtredird.EnableRedirection(amtredird_url),
             basic.SetBootIntoCOWMemory(config_url),
             amt.ResetAMTHosts(creds_provider),
             basic.WaitForSSHAvailable(
                 datetime.timedelta(seconds=10),
                 datetime.timedelta(minutes=10)),
             amtredird.DisableRedirection(amtredird_url),
             basic.ResetBoot(config_url),
             disk.DetermineDisk(),
             disk.FreeDisk(),
             disk.PartitionDisk(),
             disk.ConfigureDisk()])
