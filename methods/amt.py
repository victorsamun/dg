import datetime

from common import method
from stages import (
    amt, amtredird, basic, boot, config, disk, ndd, network, ssh
)

class AMTMethod(method.Method):
    'method for deploying AMT-capable hosts'
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
        disk.FreeDisk(),
        disk.ConfigureDisk(),
        config.StoreCOWConfig(),
        network.EnsureNetworkSpeed(),
        ndd.RunNDD(),
        config.CustomizeWindowsSetup(),
        boot.SetBootIntoNonDefault(),
        ssh.RebootLinux(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoNonDefault(*ssh.Timeouts.BIG),
        boot.ResetBoot(),
        ssh.RebootNonDefaultOS(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoDefault(*ssh.Timeouts.BIG),
    ]
