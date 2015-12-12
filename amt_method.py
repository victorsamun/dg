import datetime
import disk_stages
import method
import amt_creds
import amt_stages
import amtredird_stages
import common_stages

class AMTMethod(method.Method):
    def __init__(self, amtpasswd, config_url, amtredird_url):
        creds_provider = amt_creds.AMTCredentialsProvider(amtpasswd)
        super(AMTMethod, self).__init__(
            [common_stages.InitHosts(config_url),
             amt_stages.DetermineAMTHosts(config_url),
             amtredird_stages.EnsureRedirectionPossible(amtredird_url),
             amt_stages.WakeupAMTHosts(creds_provider),
             amtredird_stages.EnableRedirection(amtredird_url),
             common_stages.SetBootIntoCOWMemory(config_url),
             amt_stages.ResetAMTHosts(creds_provider),
             common_stages.WaitForSSHAvailable(
                    datetime.timedelta(seconds=10),
                    datetime.timedelta(minutes=10)),
             amtredird_stages.DisableRedirection(amtredird_url),
             common_stages.ResetBoot(config_url),
             disk_stages.DetermineDisk(),
             disk_stages.FreeDisk(),
             disk_stages.PartitionDisk(),
             disk_stages.ConfigureDisk()])
