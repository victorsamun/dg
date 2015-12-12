class Host(object):
    def __init__(self, state, name, props):
        self.state = state
        self.name = name
        self.props = props
        self.amt_host = None
        self.state.active_hosts.add(self)

    def __str__(self):
        return self.name

    def fail(self, stage, reason):
        self.state.log.error('host {} failed, stage: {}, reason: {}'.format(
            self, stage, reason))
        self.state.active_hosts.remove(self)
        self.state.failed_hosts.add(self)
