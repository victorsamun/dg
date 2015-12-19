import datetime

from common import method
from stages import amt, amtredird, basic, config, disk, ndd, network, slurm
from util import amt_creds

class AMTMethod(method.Method):
    name = 'amt'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        amt.DetermineAMTHosts(),
        amtredird.EnsureRedirectionPossible(),
        amt.WakeupAMTHosts(),
        amtredird.EnableRedirection(),
        basic.SetBootIntoCOWMemory(),
        amt.ResetAMTHosts(),
        basic.WaitForSSHAvailable(
            datetime.timedelta(seconds=10),
            datetime.timedelta(minutes=10)),
        amtredird.DisableRedirection(),
        basic.ResetBoot(),
        network.EnsureNetworkSpeed(),
        disk.DetermineDisk(),
        disk.FreeDisk(),
        disk.PartitionDisk(),
        disk.ConfigureDisk(),
        config.StoreCOWConfig(),
        slurm.WaitForSlurmAvailable(tries=3, pause=10),
        ndd.RunNDDViaSlurm(),
    ]
