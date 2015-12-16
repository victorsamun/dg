from util import hosts

class Method(object):
    stages = []

    def __init__(self):
        self.stages = self.__class__.stages

    def parse(self, args):
        for stage in self.stages:
            stage.parse(args)

    def run(self, state):
        for index, stage in enumerate(self.stages):
            state.log.info('running stage "{}"'.format(stage))
            stage.run(state)
            state.log.info('finished "{}"'.format(stage))
            state.log.info('active hosts after this stage: {}'.format(
                hosts.format_hosts(state.active_hosts)))

            if len(state.failed_hosts) > 0:
                state.log.warning('failed hosts after "{}": {}'.format(
                    stage.name, hosts.format_hosts(state.failed_hosts)))
                state.log.warning('doing rollback for those')
                for stage in reversed(self.stages[:index+1]):
                    stage.rollback(state)
                state.all_failed_hosts.update(state.failed_hosts)
                state.failed_hosts.clear()

            if len(state.active_hosts) == 0:
                state.log.error('all the hosts failed, stopping now')
                return False

        if len(state.all_failed_hosts) > 0:
            state.log.warning('finished. Failed hosts are: {}'.format(
                hosts.format_hosts(state.all_failed_hosts)))
        else:
            state.log.info('finished.')
        return True
