class Stage(object):
    def __str__(self):
        return self.__class__.name

    def run(self, state):
        raise NotImplementedError()

    def rollback(self, state):
        pass


class SimpleStage(Stage):
    def run(self, state):
        for host in list(state.active_hosts):
            try:
                self.run_single(host)
            except Exception as e:
                host.fail(self, e)

    def rollback(self, state):
        for host in list(state.failed_hosts):
            try:
                self.rollback_single(host)
            except Exception as e:
                state.log.warning('rollback of {} for {} failed: {}'.format(
                    self.__class__.name, host.name, e))

    def run_single(self, host):
        raise NotImplementedError()

    def rollback_single(self, host):
        pass
