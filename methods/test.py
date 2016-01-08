import datetime

from common import method
from stages import basic, boot, config, network, slurm, ssh

class TestMethod(method.Method):
    'simple method used for testing'
    name = 'test'

    stages = [
        basic.InitHosts(),
        basic.ExcludeBannedHosts(),
        ssh.CheckIsAccessible(*ssh.Timeouts.TINY),
        boot.SetBootIntoCOWMemory(),
        ssh.RebootHost(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoCOWMemory(*ssh.Timeouts.NORMAL),
        network.EnsureNetworkSpeed(),
        boot.SetBootIntoNonDefault(),
        ssh.RebootLinux(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoNonDefault(*ssh.Timeouts.BIG),
        boot.ResetBoot(),
        ssh.RebootNonDefaultOS(*ssh.Timeouts.TINY),
        ssh.WaitUntilBootedIntoDefault(*ssh.Timeouts.NORMAL),
    ]
