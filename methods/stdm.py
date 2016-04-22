import datetime

from common import method
from stages import (
    amt, amtredird, basic, boot, config, disk, ndd, network, slurm, ssh, stdm
)

class StdMMethod(method.Method):
    'method for deploying hosts with Standard Manageability'
    name = 'stdm'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        amt.DetermineAMTHosts(),
        amtredird.EnsureRedirectionPossible(),
        stdm.WakeupStdMHosts(),
        amtredird.EnableRedirection(),
        boot.SetBootIntoCOWMemory(),
        stdm.ResetStdMHosts(),
        ssh.WaitUntilBootedIntoCOWMemory(*ssh.Timeouts.NORMAL),
        amtredird.DisableRedirection(),
        boot.ResetBoot(),
        disk.FreeDisk(),
        disk.ConfigureDisk(),
        config.StoreCOWConfig(),
        network.EnsureNetworkSpeed(),
        slurm.WaitForSlurmAvailable(*slurm.Timeouts.NORMAL),
        ndd.RunNDDViaSlurm(),
        config.CustomizeWindowsSetup(),
        boot.SetBootIntoNonDefault(),
        ssh.RebootLinux(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoNonDefault(*ssh.Timeouts.BIG),
        boot.ResetBoot(),
        ssh.RebootNonDefaultOS(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoDefault(*ssh.Timeouts.BIG),
    ]

