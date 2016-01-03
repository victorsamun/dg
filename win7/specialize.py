#!/usr/bin/env python

import contextlib
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


@contextlib.contextmanager
def xml_sysprep(filename):
    tree = xml.dom.minidom.parse(filename)
    yield tree

    with open(filename, 'w') as f:
        f.write(unescape(tree.toxml()))


def set_computer_name(filename):
    hostname = subprocess.check_output(
        ['/sbin/hostname', '-f']).strip().decode('utf-8')

    with xml_sysprep(filename) as tree:
        elems = list(tree.getElementsByTagName('ComputerName'))
        if len(elems) != 2:
            raise ValueError('Wrong sysprep file: count(ComputerName) != 2')

        for e in elems:
            e.firstChild.nodeValue = hostname


def main():
    if len(sys.argv) < 2:
        sys.exit("`sysprep` template not specified. Winprep terminated")

    args = sys.argv[1:]
    steps = (set_computer_name,)

    for step in steps:
        try:
            step(*args)
        except Exception as e:
            logging.error("Failed step %s: %s", step.__name__, e)
            sys.exit(2)
        else:
            logging.info("%s: OK", step.__name__)


if __name__ == '__main__':
    main()
