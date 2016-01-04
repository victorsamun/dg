import multiprocessing

class Stage(object):
    def parse(self, args):
        pass

    def __str__(self):
        return self.__class__.__doc__

    def run(self, state):
        raise NotImplementedError

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
                    self, host.name, e))

    def run_single(self, host):
        raise NotImplementedError

    def rollback_single(self, host):
        pass


def _run_forked((stage, host)):
    return stage.run_single(host)


class ParallelStage(Stage):
    HUGE_TIMEOUT = 60 * 60 * 24

    def __init__(self, poolsize=0):
        self.poolsize = poolsize

    def run(self, state):
        try:
            pool = multiprocessing.Pool(
                self.poolsize if self.poolsize else len(state.active_hosts))
            self.setup()
            host_to_result = [
                (host, pool.apply_async(_run_forked, [(self, host)]))
                for host in state.active_hosts
            ]
            for host, result in host_to_result:
                try:
                    # Timeout is here to handle interruptions properly, otherwise
                    # it will not work as expected due to bug.
                    rv, reason = result.get(ParallelStage.HUGE_TIMEOUT)
                    if not rv:
                        host.fail(self, reason)
                except Exception as e:
                    state.log.exception(e)
                    host.fail(self,
                              'exception occured while running parallel stage')
        except:
            pool.terminate()
            raise
        finally:
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
