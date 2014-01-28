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
import six
import sys

import fixtures
import mock
from testtools import matchers

from keystoneclient.v2_0 import client as ksclient

from ceilometerclient import exc
from ceilometerclient import shell as ceilometer_shell
from ceilometerclient.tests import utils
from ceilometerclient.v1 import client as v1client

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where'}


class ShellTest(utils.BaseTestCase):
    re_options = re.DOTALL | re.MULTILINE

    # Patch os.environ to avoid required auth info.
    def make_env(self, exclude=None):
        env = dict((k, v) for k, v in FAKE_ENV.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()

    @mock.patch.object(ksclient, 'Client')
    @mock.patch.object(v1client.http.HTTPClient, 'json_request')
    @mock.patch.object(v1client.http.HTTPClient, 'raw_request')
    def shell(self, argstr, mock_ksclient, mock_json, mock_raw):
        orig = sys.stdout
        try:
            sys.stdout = six.StringIO()
            _shell = ceilometer_shell.CeilometerShell()
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

    def test_auth_param(self):
        self.make_env(exclude='OS_USERNAME')
        self.test_help()

    @mock.patch.object(ksclient, 'Client')
    def test_debug_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.Unauthorized
        self.make_env()
        args = ['--debug', 'event-list']
        self.assertRaises(exc.Unauthorized, ceilometer_shell.main, args)

    @mock.patch.object(ksclient, 'Client')
    def test_dash_d_switch_raises_error(self, mock_ksclient):
        mock_ksclient.side_effect = exc.CommandError("FAIL")
        self.make_env()
        args = ['-d', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch.object(ksclient, 'Client')
    def test_no_debug_switch_no_raises_errors(self, mock_ksclient):
        mock_ksclient.side_effect = exc.Unauthorized("FAIL")
        self.make_env()
        args = ['event-list']
        self.assertRaises(SystemExit, ceilometer_shell.main, args)
