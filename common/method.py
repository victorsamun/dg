def format_hosts(hosts):
    return '({} total) {}'.format(
        len(hosts), ', '.join(sorted(str(host) for host in hosts)))


class Method(object):
    def __init__(self, stages):
        self.stages = stages

    def run(self, state):
        for index, stage in enumerate(self.stages):
            state.log.info('running stage "{}"'.format(stage))
            stage.run(state)
            state.log.info('finished "{}"'.format(stage))
            state.log.info('active hosts after this stage: {}'.format(
                format_hosts(state.active_hosts)))

            if len(state.failed_hosts) > 0:
                state.log.warning('failed hosts after "{}": {}'.format(
                    stage.name, format_hosts(state.failed_hosts)))
                state.log.warning('doing rollback for those')
                for stage in reversed(self.stages[:index+1]):
                    stage.rollback(state)
                state.all_failed_hosts.update(state.failed_hosts)
                state.failed_hosts.clear()

            if len(state.active_hosts) == 0:
                state.log.error('all the hosts failed, stopping now')
                return False

        state.log.warning('finished. Failed hosts are: {}'.format(
            format_hosts(state.all_failed_hosts)))
        return True
