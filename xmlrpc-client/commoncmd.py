from os import mkdir
from utils import Command
import getpass
import logging


class Login(Command):
    name = 'login'
    description ='Login to the devilry server.' 
    args_help = '<url>'
    urlpath = '/xmlrpc/'

    user_disabled = 1
    login_failed = 2
    successful_login = 3

    def add_options(self):
        self.add_user_option()

    def command(self):
        server = self.get_server()
        password = getpass.getpass('Password: ')
        ret = server.login(self.opt.username, password)
        if ret == self.successful_login:
            logging.info('Login successful')
        else:
            logging.error('Login failed. Reason:')
            if ret == self.user_disabled:
                print logging.error('Your user is disabled.')
            elif ret == self.login_failed:
                print logging.error('Invalid username/password.')
            raise SystemExit()


class Init(Command):
    name = 'init'
    description = 'Initialize.'
    args_help = '<url>'

    def read_config(self):
        pass

    def command(self):
        if self.find_confdir():
            raise SystemExit(
                    'You are in a existing Devilry directory tree. '\
                    'Initialization aborted.')
        self.validate_argslen(1)

        mkdir('.devilry')
        url = self.args[0]
        self.set_config('url', url)
        self.write_config()
