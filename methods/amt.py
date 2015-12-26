import datetime

from common import method
from stages import (
    amt, amtredird, basic, boot, config, disk, ndd, network, slurm, ssh
)

class AMTMethod(method.Method):
    name = 'amt'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        amt.DetermineAMTHosts(),
        amtredird.EnsureRedirectionPossible(),
        amt.WakeupAMTHosts(),
        amtredird.EnableRedirection(),
        boot.SetBootIntoCOWMemory(),
        amt.ResetAMTHosts(),
        ssh.WaitUntilBootedIntoCOWMemory(*ssh.Timeouts.NORMAL),
        amtredird.DisableRedirection(),
        boot.ResetBoot(),
        disk.DetermineDisk(),
        disk.FreeDisk(),
        disk.PartitionDisk(),
        disk.ConfigureDisk(),
        config.StoreCOWConfig(),
        network.EnsureNetworkSpeed(),
        slurm.WaitForSlurmAvailable(*slurm.Timeouts.NORMAL),
        ndd.RunNDDViaSlurm(),
        config.CopySSHCredentialsIntoWindows7Partition(),
        boot.SetBootIntoLocalWin7(),
        ssh.RebootLinuxHost(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoWindows(*ssh.Timeouts.BIG),
        boot.ResetBoot(),
        ssh.RebootWindowsHost(*ssh.Timeouts.TINY),
        ssh.WaitForSSHAvailable(*ssh.Timeouts.NORMAL),
    ]
