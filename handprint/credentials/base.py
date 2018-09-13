'''
base.py: credentials base class
'''

class Credentials(object):
    def __init__(self, credentials_dir = None):
        self.credentials_dir = credentials_dir
        self.credentials_file = None
        self.credentials = None


    def creds(self):
        return self.credentials


    def credentials_file():
        return self.credentials_file
