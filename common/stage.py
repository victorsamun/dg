import multiprocessing

class Stage(object):
    def parse(self, args):
        pass

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
                state.log.exception('rollback of {} for {} failed: {}'.format(
                    self.__class__.name, host.name, e))

    def run_single(self, host):
        raise NotImplementedError()

    def rollback_single(self, host):
        pass


def _run_forked((stage, host)):
    rv = stage.run_single(host)
    return (host.name, rv)


class ParallelStage(Stage):
    def __init__(self, poolsize=0):
        self.poolsize = poolsize

    def run(self, state):
        name_to_host = dict((host.name, host) for host in state.active_hosts)
        args = [(self, host) for host in state.active_hosts]
        pool = multiprocessing.Pool(
            self.poolsize if self.poolsize else len(state.active_hosts))
        self.setup()
        for name, (rv, reason) in pool.map(_run_forked, args):
            if not rv:
                name_to_host[name].fail(self, reason)
        self.teardown()
        pool.close()

    def run_single(self, host):
        return False, 'Not implemented.'

    def setup(self):
        pass

    def teardown(self):
        pass

    def ok(self):
        return (True, None)

    def fail(self, reason):
        return (False, reason)
