import json
import urllib
import urllib2

def _get(base_url, entity, prop):
    reply = urllib2.urlopen('{}/{}'.format(base_url, entity))
    result = json.load(reply)
    reply.close()
    return result.get(prop)


def _post(base_url, entity, props):
    urllib2.urlopen('{}/{}'.format(base_url, entity),
                    urllib.urlencode(props)).close()


def get_hosts(base_url, group):
    return _get(base_url, group, 'hosts')


def get_name(base_url, entity):
    return _get(base_url, entity, 'name')


def get_props(base_url, entity):
    return _get(base_url, entity, 'props')


def set_props(base_url, entity, props):
    return _post(base_url, entity, props)
