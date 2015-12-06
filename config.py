import json
import urllib2

def _get(base_url, entity, prop):
    reply = urllib2.urlopen('{}/{}'.format(base_url, entity))
    result = json.load(reply)
    reply.close()
    return result.get(prop)


def get_hosts(base_url, group):
    return _get(base_url, group, 'hosts')


def get_props(base_url, entity):
    return _get(base_url, entity, 'props')
