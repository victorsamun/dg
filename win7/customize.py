import argparse
from contextlib import contextmanager
from lxml import etree
import subprocess
import sys


def ns(name): return '{{urn:schemas-microsoft-com:unattend}}{}'.format(name)


WCM_NS = 'http://schemas.microsoft.com/WMIConfig/2002/State'

def wcm_ns(name):
    return '{{{}}}{}'.format(WCM_NS, name)

def wcm_map():
    return {'wcm': WCM_NS}


def get_or_add(element, expr, add):
    results = element.findall(expr)
    if len(results) > 1:
        raise ValueError(
            '{} should have at most one child with expr {}, got {}'.format(
                element.tag, expr, len(results)))
    elif len(results) == 1:
        return results[0]
    else:
        return add(element)


def get_prop(element, name):
    return get_or_add(element, './{}'.format(ns(name)),
                      lambda element: etree.SubElement(element, ns(name)))


def add_setting(tree, pass_):
    setting = etree.SubElement(tree, ns('setting'))
    setting.attrib['pass'] = pass_
    return setting


def add_component(pass_, name):
    return etree.SubElement(
        pass_, ns('component'),
        name=name,
        language='neutral',
        processorArchitecture='amd64',
        publicKeyToken='31bf3856ad364e35',
        versionScope='nonSxS')


def get(tree, pass_, component, prop):
    setting = get_or_add(
        tree, './{}[@pass="{}"]'.format(ns('settings'), pass_),
        lambda tree: add_setting(tree, pass_))
    component = get_or_add(
        setting, './{}[@name="{}"]'.format(ns('component'), component),
        lambda pass_: add_component(pass_, component))
    return get_or_add(
        component, './{}'.format(ns(prop)),
        lambda component: etree.SubElement(component, ns(prop)))


def set_computer_name(tree, name):
    get(tree, 'specialize', 'Microsoft-Windows-Shell-Setup',
        'ComputerName').text = name


def set_auto_join(tree, domain, username, password):
    ident = get(tree, 'specialize', 'Microsoft-Windows-UnattendedJoin',
                'Identification')
    creds = get_prop(ident, 'Credentials')
    get_prop(creds, 'Domain').text = domain
    get_prop(creds, 'Username').text = username
    get_prop(creds, 'Password').text = password
    get_prop(ident, 'JoinDomain').text = domain


def add_local_admin(tree, username, password):
    accounts = get(tree, 'oobeSystem', 'Microsoft-Windows-Shell-Setup',
                   'UserAccounts')
    local_users = get_prop(accounts, 'LocalAccounts')
    user = etree.SubElement(local_users, 'LocalAccount', nsmap=wcm_map())
    user.attrib[wcm_ns('action')] = 'add'
    get_prop(user, 'Description').text = username
    get_prop(user, 'DisplayName').text = username
    get_prop(user, 'Group').text = 'Administrators'
    get_prop(user, 'Name').text = username
    get_prop(get_prop(user, 'Password'), 'Value').text = password
    get_prop(get_prop(user, 'Password'), 'PlainText').text = 'true'


@contextmanager
def xml_tree(filename, output):
    tree = etree.parse(filename)
    yield tree.getroot()
    with open(output, 'w') as out:
        out.write(etree.tostring(tree, xml_declaration=True, encoding='utf-8',
                                 pretty_print=True))


def get_hostname(name):
    return (name if len(name) != 0
            else subprocess.check_output(['/bin/hostname']).strip())


def main(raw_args):
    parser = argparse.ArgumentParser(description='Customize sysprep.xml file')
    parser.add_argument('SRC', help='Source file')
    parser.add_argument('DEST', help='Destination file')
    parser.add_argument(
        '-H', metavar='HOSTNAME',
        help='Set computer name (output of `hostname` will be used if empty')
    parser.add_argument('-j', metavar='DOMAIN', help='Configure domain to join')
    parser.add_argument(
        '-u', metavar='USER', help='Username to join', default='unix_manager')
    parser.add_argument(
        '-p', metavar='FILE', help='Password file for domain join')
    parser.add_argument('-a', metavar='USER:PASS', help='Add local admin user',
                        default=[], action='append')

    args = parser.parse_args(raw_args)

    with xml_tree(args.SRC, args.DEST) as tree:
        if args.H is not None:
            set_computer_name(tree, get_hostname(args.H))
        if args.j:
            if args.p is None:
                parser.error('-p must be specified in order to add join')
            with open(args.p) as pwdfile:
                set_auto_join(tree, args.j, args.u, pwdfile.read().strip())
        for user, pwd in map(lambda spec: spec.split(':', 1), args.a):
            add_local_admin(tree, user, pwd)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
