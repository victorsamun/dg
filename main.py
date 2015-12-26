import sys

from common import config
from methods import amt, simple, test

def main(raw_args):
    return config.execute_with(
        raw_args, [amt.AMTMethod, simple.SimpleMethod, test.TestMethod])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
