class AMTCredentialsProvider(object):
    def __init__(self, filename):
        with open(filename) as pwdfile:
            self.user, self.passwd = pwdfile.read().strip().split(':')

    def get_credentials(self, host):
        return (self.user, self.passwd)
