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
from ceilometerclient.openstack.common.apiclient import client as api_client
from ceilometerclient import shell as ceilometer_shell
from ceilometerclient.tests.unit import utils
from ceilometerclient.v2 import client as v2client

FAKE_V2_ENV = {'OS_USERNAME': 'username',
               'OS_PASSWORD': 'password',
               'OS_TENANT_NAME': 'tenant_name',
               'OS_AUTH_URL': 'http://localhost:5000/v2.0'}

FAKE_V3_ENV = {'OS_USERNAME': 'username',
               'OS_PASSWORD': 'password',
               'OS_USER_DOMAIN_NAME': 'domain_name',
               'OS_PROJECT_ID': '1234567890',
               'OS_AUTH_URL': 'http://localhost:5000/v3'}


class ShellTestBase(utils.BaseTestCase):

    @mock.patch('sys.stdout', new=six.StringIO())
    @mock.patch.object(ks_session, 'Session', mock.MagicMock())
    @mock.patch.object(v2client.client.HTTPClient,
                       'client_request', mock.MagicMock())
    def shell(self, argstr):
        try:
            _shell = ceilometer_shell.CeilometerShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)

        return sys.stdout.getvalue()

    # Patch os.environ to avoid required auth info.
    def make_env(self, env_version, exclude=None):
        env = dict((k, v) for k, v in env_version.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))


class ShellHelpTest(ShellTestBase):
    RE_OPTIONS = re.DOTALL | re.MULTILINE

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
                                                      self.RE_OPTIONS))

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
                                matchers.MatchesRegex(r, self.RE_OPTIONS))

    def test_get_base_parser(self):
        standalone_shell = ceilometer_shell.CeilometerShell()
        parser = standalone_shell.get_base_parser()
        self.assertEqual(600, parser.get_default('timeout'))


class ShellBashCompletionTest(ShellTestBase):

    def test_bash_completion(self):
        completion_commands = self.shell("bash-completion")
        options = completion_commands.split(' ')
        self.assertNotIn('bash-completion', options)
        self.assertNotIn('bash_completion', options)
        for option in options:
            self.assertThat(option,
                            matchers.MatchesRegex(r'[a-z0-9-]'))


class ShellKeystoneV2Test(ShellTestBase):

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_debug_switch_raises_error(self, aodh_redirect, mock_ksclient):
        mock_ksclient.side_effect = exc.HTTPUnauthorized
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', 'event-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_dash_d_switch_raises_error(self, aodh_redirect, mock_ksclient):
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


class ShellKeystoneV3Test(ShellTestBase):

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_debug_switch_raises_error(self, aodh_redirect, mock_ksclient):
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


class ShellTimeoutTest(ShellTestBase):

    @mock.patch('sys.stderr', new=six.StringIO())
    def _test_timeout(self, timeout, expected_msg):
        args = ['--timeout', timeout, 'alarm-list']
        self.assertRaises(SystemExit, ceilometer_shell.main, args)
        self.assertEqual(expected_msg, sys.stderr.getvalue().splitlines()[-1])

    def test_timeout_invalid_value(self):
        expected_msg = ('ceilometer: error: argument --timeout: '
                        'abc must be an integer')
        self._test_timeout('abc', expected_msg)

    def test_timeout_negative_value(self):
        expected_msg = ('ceilometer: error: argument --timeout: '
                        '-1 must be greater than 0')
        self._test_timeout('-1', expected_msg)

    def test_timeout_float_value(self):
        expected_msg = ('ceilometer: error: argument --timeout: '
                        '1.5 must be an integer')
        self._test_timeout('1.5', expected_msg)

    def test_timeout_zero(self):
        expected_msg = ('ceilometer: error: argument --timeout: '
                        '0 must be greater than 0')
        self._test_timeout('0', expected_msg)

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_timeout_keystone_session(self, aodh_redirect, mocked_session):
        mocked_session.side_effect = exc.HTTPUnauthorized("FAIL")
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', '--timeout', '5', 'alarm-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)
        args, kwargs = mocked_session.call_args
        self.assertEqual(5, kwargs.get('timeout'))


class ShellInsecureTest(ShellTestBase):

    @mock.patch.object(api_client, 'HTTPClient')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_insecure_true_ceilometer(self, aodh_redirect, mocked_client):
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', '--os-insecure', 'true', 'alarm-list']
        self.assertIsNone(ceilometer_shell.main(args))
        args, kwargs = mocked_client.call_args
        self.assertEqual(False, kwargs.get('verify'))

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_insecure_true_keystone(self, aodh_redirect, mocked_session):
        mocked_session.side_effect = exc.HTTPUnauthorized("FAIL")
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', '--os-insecure', 'true', 'alarm-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)
        args, kwargs = mocked_session.call_args
        self.assertEqual(False, kwargs.get('verify'))

    @mock.patch.object(api_client, 'HTTPClient')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_insecure_false_ceilometer(self, aodh_redirect, mocked_client):
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', '--os-insecure', 'false', 'alarm-list']
        self.assertIsNone(ceilometer_shell.main(args))
        args, kwargs = mocked_client.call_args
        self.assertEqual(True, kwargs.get('verify'))

    @mock.patch.object(ks_session, 'Session')
    @mock.patch('ceilometerclient.client.AuthPlugin.redirect_to_aodh_endpoint')
    def test_insecure_false_keystone(self, aodh_redirect, mocked_session):
        mocked_session.side_effect = exc.HTTPUnauthorized("FAIL")
        self.make_env(FAKE_V2_ENV)
        args = ['--debug', '--os-insecure', 'false', 'alarm-list']
        self.assertRaises(exc.CommandError, ceilometer_shell.main, args)
        args, kwargs = mocked_session.call_args
        self.assertEqual(True, kwargs.get('verify'))


class ShellEndpointTest(ShellTestBase):

    @mock.patch('ceilometerclient.v2.client.Client')
    def _test_endpoint_and_token(self, token_name, endpoint_name, mocked):
        args = ['--debug', token_name, 'fake-token',
                endpoint_name, 'http://fake-url', 'alarm-list']
        self.assertEqual(None, ceilometer_shell.main(args))
        args, kwargs = mocked.call_args
        self.assertEqual('http://fake-url', kwargs.get('endpoint'))
        self.assertEqual('fake-token', kwargs.get('token'))

    def test_endpoint_and_token(self):
        self._test_endpoint_and_token('--os-auth-token', '--ceilometer-url')
        self._test_endpoint_and_token('--os-auth-token', '--os-endpoint')
        self._test_endpoint_and_token('--os-token', '--ceilometer-url')
        self._test_endpoint_and_token('--os-token', '--os-endpoint')
