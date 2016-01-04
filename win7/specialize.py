#!/usr/bin/env python

from collections import namedtuple
import contextlib
import functools
import logging
import subprocess
import sys
import xml.dom.minidom

import six
if six.PY2:
    from HTMLParser import HTMLParser

    def unescape(s):
        return HTMLParser().unescape(s)
else:
    from html import unescape


LOGGER = logging.getLogger()


@contextlib.contextmanager
def xml_sysprep(filename):
    tree = xml.dom.minidom.parse(filename)
    yield tree

    with open(filename, 'w') as f:
        f.write(unescape(tree.toxml()))


def log(internal_step=False):
    def _log(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            fname = fn.__name__
            try:
                fn(*args, **kwargs)
                LOGGER.info("%s: OK", fname)
            except Exception as e:
                LOGGER.error("Failed '%s': '%s'", fname, e)
                if internal_step:
                    raise Exception("`%s` failed" % fname)
                else:
                    raise
        return wrapper
    return _log


@log()
def modify_sysprep(args):
    @log(True)
    def set_hostname(tree):
        hostname = subprocess.check_output(
            ['/sbin/hostname', '-f']).strip().decode('utf-8')

        elems = list(tree.getElementsByTagName('ComputerName'))
        if len(elems) != 2:
            raise ValueError('Wrong sysprep file: count(ComputerName) != 2')

        for e in elems:
            e.firstChild.nodeValue = hostname

    steps = (set_hostname,)
    with xml_sysprep(args.fn_sysprep) as tree:
        for step in steps:
            step(tree)


RunArguments = namedtuple('RunArguments', ('fn_sysprep', ))


def prepare_log():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)


def main():
    if len(sys.argv) < 2:
        sys.exit("`sysprep` template not specified. Winprep terminated")

    args = RunArguments(*sys.argv[1:])
    steps = (modify_sysprep,)

    prepare_log()

    try:
        for step in steps:
            step(args)
    except Exception:
        sys.exit(2)


if __name__ == '__main__':
    main()
