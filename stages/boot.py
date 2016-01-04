from common import config, stage
from clients import config as cfg

class ConfigureBoot(config.WithConfigURL, stage.SimpleStage):
    BOOT_PROP = 'boot'

    def run_single(self, host):
        cfg.set(self.config_url, host.name,
                [(ConfigureBoot.BOOT_PROP, self.__class__.value)])

    def rollback_single(self, host):
        if len(self.__class__.value) == 0:
            return
        cfg.set(self.config_url, host.name,
                [(ConfigureBoot.BOOT_PROP, ResetBoot.value)])


class SetBootIntoCOWMemory(ConfigureBoot):
    'enable boot to COW memory image'
    value = 'cow-m'


class SetBootIntoLocalWin7(ConfigureBoot):
    'enable boot to local Windows 7 via GRUB'
    value = 'grub.windows7'


class ResetBoot(ConfigureBoot):
    "reset boot into it's default state"
    value = ''
