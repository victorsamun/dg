import HTMLParser
import re
import requests

from common import config, stage

class TParser(HTMLParser.HTMLParser):

    def handle_starttag(self, tag, attrs):
        attrs_map = dict(attrs)
        if tag == 'input' and attrs_map.get('name') == 't':
            self.t = attrs_map.get('value')


class StdMStage(config.WithAMTCredentials, stage.SimpleStage):
    ON_RE = re.compile('Power state: On')
    OFF_RE = re.compile('Power state: Off')

    def make_request(self, method, host, url, validate=True, **args):
        response = method('http://{}:16992/{}'.format(host, url),
                          auth=requests.auth.HTTPDigestAuth(
                              *self.amt_creds.get_credentials(host)),
                          **args)
        if validate:
            response.raise_for_status()
        return response

    def get(self, host, url):
        return self.make_request(requests.get, host, url)

    def post(self, host, url, validate=False, **params):
        return self.make_request(requests.post, host, url, validate=validate,
                                 data=params)

    def boot_control(self, host, **params):
        parser = TParser()
        parser.feed(self.get(host, 'remote.htm').text)
        return self.post(host, 'remoteform', t=parser.t, **params)


class WakeupStdMHosts(StdMStage):
    'wake up hosts via Std. Manageability interface'

    def is_up(self, host):
        response_text = self.get(host, 'remote.htm').text
        on = WakeupStdMHosts.ON_RE.search(response_text) != None
        off = WakeupStdMHosts.OFF_RE.search(response_text) != None
        assert (on and not off) or (off and not on), \
            'Failed to determine host status: on={} off={}'.format(on, off)
        return on

    def run_single(self, host):
        if not self.is_up(host.amt_host):
            self.boot_control(
                host.amt_host,
                amt_html_rc_radio_group=2, amt_html_rc_boot_special=1)


class ResetStdMHosts(StdMStage):
    'reset hosts via Std. Manageability interface'

    def run_single(self, host):
        self.boot_control(
            host.amt_host,
            amt_html_rc_radio_group=4, amt_html_rc_boot_special=1)
