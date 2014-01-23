#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import re
import sys

import fixtures
from keystoneclient import session as ks_session
import mock
import six
from testtools import matchers

from ceilometerclient import exc
from ceilometerclient import shell as ceilometer_shell
from ceilometerclient.tests import utils
from ceilometerclient.v1 import client as v1client

FAKE_V2_ENV = {'OS_USERNAME': 'username',
               'OS_PASSWORD': 'password',
               'OS_TENANT_NAME': 'tenant_name',
               'OS_AUTH_URL': 'http://localhost:5000/v2.0'}

FAKE_V3_ENV = {'OS_USERNAME': 'username',
               'OS_PASSWORD': 'password',
               'OS_USER_DOMAIN_NAME': 'domain_name',
               'OS_PROJECT_ID': '1234567890',
               'OS_AUTH_URL': 'http://localhost:5000/v3'}


class ShellTest(utils.BaseTestCase):
    re_options = re.DOTALL | re.MULTILINE

    # Patch os.environ to avoid required auth info.
    def make_env(self, env_version, exclude=None):
        env = dict((k, v) for k, v in env_version.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()

    @mock.patch('sys.stdout', new=six.StringIO())
    @mock.patch.object(ks_session, 'Session', mock.MagicMock())
    @mock.patch.object(v1client.client.HTTPClient,
                       'client_request', mock.MagicMock())
    def shell(self, argstr):
        try:
            _shell = ceilometer_shell.CeilometerShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)

        return sys.stdout.getvalue()

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: ceilometer',
            '.*?^See "ceilometer help COMMAND" '
            'for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r,
                                                      self.re_options))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: ceilometer meter-list',
            ".*?^List the user's meter",
        ]
        argstrings = [
            'help meter-list',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r, self.re_options))


class ShellKeystoneV2Test(ShellTest):

    def test_auth_param(self):
        self.make_env(FAKE_V2_ENV, exclude='OS_USERNAME')
        self.test_help()

    @mock.patch.object(ks_session, 'Session')
    def test_debug_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.HTTPUnauthorized
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch.object(ks_session, 'Session')
    def test_dash_d_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.CommandError("FAIL")
        self.make_env(FAKE_V2_ENV)
        args = ['-d', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch('sys.stderr')
    @mock.patch.object(ks_session, 'Session')
    def test_no_debug_switch_no_raises_errors(self, mock_ksclient, __):
        mock_ksclient.side_effect = exc.HTTPUnauthorized("FAIL")
        self.make_env(FAKE_V2_ENV)
        args = ['event-list']
        self.assertRaises(SystemExit, ceilometer_shell.main, args)


class ShellKeystoneV3Test(ShellTest):

    def test_auth_param(self):
        self.make_env(FAKE_V3_ENV, exclude='OS_USER_DOMAIN_NAME')
        self.test_help()

    @mock.patch.object(ks_session, 'Session')
    def test_debug_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.HTTPUnauthorized
        self.make_env(FAKE_V3_ENV)
        args = ['--debug', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch.object(ks_session, 'Session')
    def test_dash_d_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.CommandError("FAIL")
        self.make_env(FAKE_V3_ENV)
        args = ['-d', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch('sys.stderr')
    @mock.patch.object(ks_session, 'Session')
    def test_no_debug_switch_no_raises_errors(self, mock_ksclient, __):
        mock_ksclient.side_effect = exc.HTTPUnauthorized("FAIL")
        self.make_env(FAKE_V3_ENV)
        args = ['event-list']
        self.assertRaises(SystemExit, ceilometer_shell.main, args)
