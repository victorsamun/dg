import sys

from common import config, state
from methods import amt, test

def main(raw_args):
    methods = [amt.AMTMethod, test.TestMethod]
    method_cls = config.Option.choose_method(methods, raw_args)

    method = method_cls()
    method_args = config.Option.get_method_args(method_cls, raw_args)
    method.parse(method_args)

    return 0 if method.run(state.State(method_args.g)) else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
