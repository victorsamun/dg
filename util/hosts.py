def format_hosts(hosts):
    return '({} total) {}'.format(
        len(hosts), ', '.join(sorted(str(host) for host in hosts)))
