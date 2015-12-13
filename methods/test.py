import datetime

from common import method
from stages import basic

class TestMethod(method.Method):
    def __init__(self, config_url):
        super(TestMethod, self).__init__(
            [basic.InitHosts(config_url),
             basic.WaitForSSHAvailable(
                 datetime.timedelta(seconds=1),
                 datetime.timedelta(seconds=3))])
