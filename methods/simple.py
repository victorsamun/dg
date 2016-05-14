import datetime

from common import method
from stages import basic, boot, config, ndd, network, ssh

class SimpleMethod(method.Method):
    'method for deploying pre-configured machines'
    name = 'simple'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        ssh.CheckIsAccessible(*ssh.Timeouts.TINY),
        boot.SetBootIntoCOWMemory(),
        ssh.RebootHost(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoCOWMemory(*ssh.Timeouts.NORMAL),
        boot.ResetBoot(),
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
