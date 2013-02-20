import cStringIO
import os
import httplib2
import sys

import mox
import unittest
import unittest2
try:
    import json
except ImportError:
    import simplejson as json
from keystoneclient.v2_0 import client as ksclient

from ceilometerclient import exc
from ceilometerclient.v1 import client as v1client
import ceilometerclient.shell


class ShellValidationTest(unittest.TestCase):

    def shell_error(self, argstr, error_match):
        orig = sys.stderr
        try:
            sys.stderr = cStringIO.StringIO()
            _shell = ceilometerclient.shell.CeilometerShell()
            _shell.main(argstr.split())
        except exc.CommandError as e:
            self.assertRegexpMatches(e.__str__(), error_match)
        else:
            self.fail('Expected error matching: %s' % error_match)
        finally:
            err = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig
        return err


class ShellTest(unittest2.TestCase):

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        self.m = mox.Mox()
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(v1client.Client, 'json_request')
        self.m.StubOutWithMock(v1client.Client, 'raw_request')

        global _old_env
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        _old_env, os.environ = os.environ, fake_env.copy()

    def tearDown(self):
        self.m.UnsetStubs()
        global _old_env
        os.environ = _old_env

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = cStringIO.StringIO()
            _shell = ceilometerclient.shell.CeilometerShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_debug(self):
        httplib2.debuglevel = 0
        self.shell('--debug help')
        self.assertEqual(httplib2.debuglevel, 1)

    def test_help(self):
        required = [
            '^usage: ceilometer',
            '(?m)^See "ceilometer help COMMAND" for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_help_on_subcommand(self):
        required = [
            '^usage: ceilometer meter-list',
            "(?m)^List the user's meter",
        ]
        argstrings = [
            'help meter-list',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_auth_param(self):
        class TokenContext(object):
            def __enter__(self):
                fake_env = {
                    'OS_AUTH_TOKEN': 'token',
                    'CEILOMETER_URL': 'http://no.where'
                }
                self.old_env, os.environ = os.environ, fake_env.copy()

            def __exit__(self, exc_type, exc_value, traceback):
                os.environ = self.old_env

        with TokenContext():
            self.test_help()
